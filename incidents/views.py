import random, csv, requests, collections, uuid, base64

from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from accounts.models import UserPasswordHistory, Worker, User
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.base import ContentFile
from django.utils import timezone

from incidents.models import Incident, IncidentCategory, Camera
from django.views.decorators.csrf import csrf_exempt

from incidents.functions import get_incidents_by_request, get_incidents_by_date_range

def create_false_data():
    if not IncidentCategory.objects.all():
        IncidentCategory(name="Con mascarilla", color="green",
                         image="incident_categories/correct_mask.png").save()
        IncidentCategory(name="Mascarilla mal puesta", color="yellow",
                         image="incident_categories/incorrect_mask.png").save()
        IncidentCategory(name="Sin mascarilla", color="red",
                         image="incident_categories/no_mask.png").save()

    if not Incident.objects.all():
        incidents_categories = IncidentCategory.objects.all()
        workers = Worker.objects.all()
        camera = Camera.objects.get(id=1)
        security_user = User.objects.get(id=1)
        for i, worker in enumerate(workers):
            date_time = datetime(year=2021, month=random.randint(10, 11),
                                 day=random.randint(1, 30), hour=random.randint(10, 19), minute=random.randint(0, 59), second=random.randint(0, 59))
            Incident(incident_category=incidents_categories[i % len(incidents_categories)], worker=worker, camera=camera, security_user=security_user,
                     image="incident_images/test_incident.jpg", date_time=date_time).save()


def list_incidents_page(request):
    if not Incident.objects.all() or not IncidentCategory.objects.all():
        create_false_data()

    incidents, fstart_date, fend_date = get_incidents_by_request(request, "POST")

    page = request.GET.get('page', 1)
    paginator = Paginator(incidents, 10)

    try:
        incidents = paginator.page(page)
    except PageNotAnInteger:
        incidents = paginator.page(1)
    except EmptyPage:
        incidents = paginator.page(paginator.num_pages)

    context = {
        'incidents': incidents,
        'start_date': fstart_date.strftime('%d/%m/%Y') if fstart_date is not None else '',
        'end_date': fend_date.strftime('%d/%m/%Y') if fend_date is not None else ''
    }

    return render(request, 'incidents/list.html', context)


def list_incidents_page_csv(request):
    response = HttpResponse(
        content_type = 'text/csv',
        headers = {'Content-Disposition': 'attachment; filename="incidencias.csv"'},
    )

    incidents, fstart_date, fend_date = get_incidents_by_request(request, "GET")

    writer = csv.writer(response)
    writer.writerow(['Nombre del colaborador', 'Correo del colaborador', 'Categoria', 'Fecha y hora'])

    for incident in incidents:
        writer.writerow([incident.worker.names + ' ' + incident.worker.surnames, incident.worker.email, incident.incident_category.name, timezone.localtime(incident.date_time).strftime('%d/%m/%Y %H:%M')])

    return response


def delete_incident_request(request, id):
    incident = get_object_or_404(Incident, id=id)
    incident.delete()
    return redirect('incidents:list_incidents')


def get_incident_page(request, id):
    context = {
        'incident': get_object_or_404(Incident, id=id),
    }
    return render(request, 'incidents/view.html', context)

def get_incidents_chart_data(request):
    incidents, fstart_date, fend_date = get_incidents_by_request(request, "GET")

    counter = collections.Counter(list(map(lambda x: x.date_time_truncated, incidents)))
    sorted_counter_keys = sorted(counter.keys())

    data = []
    labels = []

    current_date = fstart_date if fstart_date != None else sorted_counter_keys[0]
    last_date = fend_date if fend_date != None else sorted_counter_keys[len(sorted_counter_keys) - 1]

    while current_date <= last_date:
        data.append(counter[current_date])
        labels.append(current_date.strftime('%d/%m/%Y'))
        current_date += timedelta(days=1)

    context = {
        'max_incidents': 3,
        'data': data,
        'labels': labels,
    }

    return JsonResponse(context)


def get_incidents_by_worker_chart_data(request):
    incidents, fstart_date, fend_date = get_incidents_by_request(request, "GET")
    workers = Worker.objects.all()

    counter = collections.Counter(list(map(lambda x: x.worker, incidents)))
    
    data = []
    labels = []

    for worker in workers:
        data.append(counter[worker])
        labels.append(worker.names + ' ' + worker.surnames)

    context = {
        'max_incidents': 2,
        'data': data,
        'labels': labels,
    }

    return JsonResponse(context)


def get_incidents_by_category_and_day_chart_data(request):
    if request.method == "GET":
        category = request.GET.get('category-selected', False)
    elif request.method == "POST":
        category = request.POST.get('category-selected', False)

    incident_categories = IncidentCategory.objects.all()

    if category and category != 'False' and category != 'all':
        incident_categories = incident_categories.filter(id=category)

    incidents, fstart_date, fend_date = get_incidents_by_request(request, "GET")

    labels = None
    data = []
    data_colors = []
    data_labels = []

    counter = collections.Counter(list(map(lambda x: x.date_time_truncated, incidents)))
    sorted_counter_keys = sorted(counter.keys())
    current_date_temp = fstart_date if fstart_date != None else sorted_counter_keys[0]
    last_date = fend_date if fend_date != None else sorted_counter_keys[len(sorted_counter_keys) - 1]

    for category in incident_categories:
        data_labels.append(category.name)
        data_colors.append(category.color)
        incident_per_category = filter(lambda x: x.incident_category == category, incidents)
        counter = collections.Counter(list(map(lambda x : x.date_time_truncated, incident_per_category)))

        sorted_counter_keys = sorted(counter.keys())

        data_local = []
        labels_local = []

        current_date = current_date_temp

        while current_date <= last_date:
            data_local.append(counter[current_date])
            if labels == None:
                labels_local.append(current_date.strftime('%d/%m/%Y'))
            current_date += timedelta(days=1)
        
        data.append(data_local)
        if labels == None:
            labels = labels_local

    context = {
        'data': data,
        'data_colors': data_colors,
        'data_labels': data_labels,
        'labels': labels,
    }

    return JsonResponse(context)


def get_incidents_by_category_chart_data(request):
    if request.method == "GET":
        category = request.GET.get('category-selected', False)
    elif request.method == "POST":
        category = request.POST.get('category-selected', False)

    incidents, fstart_date, fend_date = get_incidents_by_request(request, "GET")

    total = incidents.count()
    counter = collections.Counter(list(map(lambda x: x.incident_category, incidents)))

    incident_categories = IncidentCategory.objects.all()

    if category and category != 'False' and category != 'all':
        incident_categories = incident_categories.filter(id=category)

    data = []
    labels = []
    data_colors = []

    for incident_category in incident_categories:
        local = counter[incident_category]
        data_colors.append(incident_category.color)
        data.append(local)
        labels.append(incident_category.name + ' (' + str(round((local/total) * 100, 2)) + '%)')

    context = {
        'data': data,
        'labels': labels,
        'data_colors': data_colors
    }

    return JsonResponse(context)


def get_incidents_summary_charts(request):
    incident_categories = IncidentCategory.objects.all()

    data_colors = []
    data_labels = []

    for incident_category in incident_categories:
        data_colors.append(incident_category.color)
        data_labels.append(incident_category.name)

    date_now = timezone.localtime(timezone.now()).replace(hour=0, minute=0, second=0, microsecond=0)

    day_start = timezone.make_aware(datetime.combine(date_now, datetime.min.time()))
    day_end = timezone.make_aware(datetime.combine(date_now, datetime.max.time()))

    prev_day_start = timezone.make_aware(datetime.combine(date_now - timedelta(days=1), datetime.min.time()))
    prev_day_end = timezone.make_aware(datetime.combine(date_now - timedelta(days=1), datetime.max.time()))

    week_start = timezone.make_aware(datetime.combine(date_now - timedelta(days=date_now.weekday()), datetime.min.time()))
    week_end = timezone.make_aware(datetime.combine(week_start + timedelta(days=6), datetime.max.time()))

    prev_week_start = timezone.make_aware(datetime.combine(week_start - timedelta(days=7), datetime.min.time()))
    prev_week_end = timezone.make_aware(datetime.combine(week_start - timedelta(days=1), datetime.max.time()))

    month_start = timezone.make_aware(datetime.combine(date_now.replace(day=1), datetime.min.time()))
    
    month_end = month_start.replace(day=28) + timedelta(days=4)
    month_end = timezone.make_aware(datetime.combine(month_end - timedelta(days=month_end.day), datetime.max.time()))

    prev_month_end = timezone.make_aware(datetime.combine(month_start - timedelta(days=1), datetime.max.time()))
    prev_month_start = timezone.make_aware(datetime.combine(prev_month_end.replace(day=1), datetime.min.time()))

    year_start = timezone.make_aware(datetime.combine(date_now.replace(day=1,month=1), datetime.min.time()))
    year_end = timezone.make_aware(datetime.combine(date_now.replace(day=31,month=12), datetime.max.time()))

    prev_year_start = timezone.make_aware(datetime.combine(date_now.replace(day=1,month=1,year=date_now.year-1), datetime.min.time()))
    prev_year_end = timezone.make_aware(datetime.combine(date_now.replace(day=31,month=12,year=date_now.year-1), datetime.max.time()))

    context = {
        'labels': ['Incidencias'],
        'data_colors': data_colors,
        'data_labels': data_labels,
        'summary': {}
    }

    cats = ['day', 'week', 'month', 'year']

    for cat in cats:
        if cat == 'day':
            date_start = day_start.strftime('%d/%m/%Y')
            date_end = day_end.strftime('%d/%m/%Y')
            prev_date_start = prev_day_start.strftime('%d/%m/%Y')
            prev_date_end = prev_day_end.strftime('%d/%m/%Y')
        elif cat == 'week':
            date_start = week_start.strftime('%d/%m/%Y')
            date_end = week_end.strftime('%d/%m/%Y')
            prev_date_start = prev_week_start.strftime('%d/%m/%Y')
            prev_date_end = prev_week_end.strftime('%d/%m/%Y')
        elif cat == 'month':
            date_start = month_start.strftime('%d/%m/%Y')
            date_end = month_end.strftime('%d/%m/%Y')
            prev_date_start = prev_month_start.strftime('%d/%m/%Y')
            prev_date_end = prev_month_end.strftime('%d/%m/%Y')
        elif cat == 'year':
            date_start = year_start.strftime('%d/%m/%Y')
            date_end = year_end.strftime('%d/%m/%Y')
            prev_date_start = prev_year_start.strftime('%d/%m/%Y')
            prev_date_end = prev_year_end.strftime('%d/%m/%Y')

        incidents, fstart_date, fend_date = get_incidents_by_date_range(request, date_start, date_end, False, False)
        prev_incidents, prev_fstart_date, prev_fend_date = get_incidents_by_date_range(request, prev_date_start, prev_date_end, False, False)

        counter = collections.Counter(list(map(lambda x: x.incident_category, incidents)))

        data_colors = []
        data = []

        if prev_incidents.count() == 0:
            change = incidents.count() * 100
        else:
            change = ((((incidents.count() / prev_incidents.count())) - 1) * 100)

        change = round(change, 2)

        for incident_category in incident_categories:
            local = counter[incident_category]
            data.append(local)

        context['summary'][cat] = {'data': data, 'count': incidents.count(), 'change': change}

    return JsonResponse(context)


@csrf_exempt
def camera_request(request, id):
    context = {
        'camera_id': id,
        'success': True
    }

    if request.method == 'POST' and 'image' in request.POST and 'dni' in request.POST:
        image_data = request.POST['image']
        dni = request.POST['dni']

        try:
            worker = Worker.objects.get(document=dni)
        except ObjectDoesNotExist:
            context['success'] = False
            context['recommendation'] = "DNI Invalido"
            return JsonResponse(context)

        api_url = 'https://yolo-mask-api.herokuapp.com/detect'
        response = requests.post(api_url, json={"base64String": image_data})

        if len(response.json()):
            category = response.json()[0]['name']
            worker = Worker.objects.get(document=dni)
            context['category'] = category
            camera = Camera.objects.get(id=id)

            #Con mascarilla -> 1
            #Mascarilla mal puesta -> 2
            #Sin mascarilla -> 3

            #Verde -> Tiene
            #Amarillo -> Incorrecta
            #Rojo -> No tiene

            if category == 'With_Mask':
                context['recommendation'] = 'Tiene la mascarilla puesta correctamente'
                incident_category = IncidentCategory.objects.get(id=1)
                context['success'] = True
            elif category == 'Incorrect_Mask':
                context['recommendation'] = 'Recomendacion mascara incorrecta'
                incident_category = IncidentCategory.objects.get(id=2)
                context['success'] = False
            elif category == 'Without_Mask':
                context['recommendation'] = 'Recomendacion sin mascara'
                incident_category = IncidentCategory.objects.get(id=3)
                context['success'] = False

            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr))  
            file_name = uuid.uuid4().hex + '.' + ext

            incident = Incident(incident_category=incident_category, worker=worker, camera=camera, security_user=camera.security_user,
                        date_time=timezone.now())
            incident.image.save(file_name, data, save=True)
            incident.save()
        else:
            context['success'] = False
            context['recommendation'] = "Error en la validacion, por favor mire bien a la camara e intentelo de nuevo"

    return JsonResponse(context)


def camera_instance(request, id):
    context = {
        'camera_id': id
    }

    return render(request, 'incidents/camera_instance.html', context)
