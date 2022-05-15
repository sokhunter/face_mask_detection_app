import random, csv, requests, collections

from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from accounts.models import Worker
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone

from incidents.models import Incident, IncidentCategory, Camera
from django.views.decorators.csrf import csrf_exempt

from incidents.functions import get_incidents_by_request

def create_false_data():
    if not IncidentCategory.objects.all():
        IncidentCategory(name="Cubre solo boca y nariz",
                         color="green", image="incident_categories/no_jaw.png").save()
        IncidentCategory(name="Cubre solo boca y barbilla",
                         color="blue", image="incident_categories/no_nose.png").save()
        IncidentCategory(name="Bajo la barbilla", color="yellow",
                         image="incident_categories/only_jaw.png").save()
        IncidentCategory(name="Sin mascarilla", color="red",
                         image="incident_categories/no_mask.png").save()

    if not Incident.objects.all():
        incidents_categories = IncidentCategory.objects.all()
        workers = Worker.objects.all()
        camera = Camera.objects.filter(id=1)
        security_user = Worker.objects.filter(id=1)
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
        writer.writerow([incident.worker.names + ' ' + incident.worker.surnames, incident.worker.email, incident.incident_category.name, incident.date_time.strftime('%d/%m/%Y %H:%M')])

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

    current_date = timezone.make_aware(datetime.combine(fstart_date, datetime.min.time())) if fstart_date != None else sorted_counter_keys[0]
    last_date = timezone.make_aware(datetime.combine(fend_date, datetime.min.time())) if fend_date != None else sorted_counter_keys[len(sorted_counter_keys) - 1]

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
    incident_categories = IncidentCategory.objects.all()
    incidents, fstart_date, fend_date = get_incidents_by_request(request, "GET")

    labels = None
    data = []
    data_colors = []
    data_labels = []

    counter = collections.Counter(list(map(lambda x: x.date_time_truncated, incidents)))
    sorted_counter_keys = sorted(counter.keys())
    current_date_temp = timezone.make_aware(datetime.combine(fstart_date, datetime.min.time())) if fstart_date != None else sorted_counter_keys[0]
    last_date = timezone.make_aware(datetime.combine(fend_date, datetime.min.time())) if fend_date != None else sorted_counter_keys[len(sorted_counter_keys) - 1]

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
    incidents, fstart_date, fend_date = get_incidents_by_request(request, "GET")

    total = incidents.count()
    counter = collections.Counter(list(map(lambda x: x.incident_category, incidents)))
    incident_categories = IncidentCategory.objects.all()

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

@csrf_exempt
def camera_request(request, id):
    context = {
        'camera_id': id,
        'success': True
    }

    if request.method == 'POST' and 'image' in request.POST and 'dni' in request.POST:
        image_data = request.POST['image']
        dni = request.POST['dni']

        api_url = 'https://yolo-mask-api.herokuapp.com/detect'
        response = requests.post(api_url, json={"base64String": image_data})

        if len(response.json()):
            category = response.json()[0]['name']
            if category != 'With_Mask':
                try:
                    worker = Worker.objects.get(document=dni)
                    context['category'] = category
                    camera = Camera.objects.get(id=id)

                    #Cubre solo boca y nariz -> 1
                    #Cubre solo boca y barbilla -> 2
                    #Bajo la barbilla -> 3
                    #Sin mascarilla -> 4

                    #Verde -> Tiene
                    #Amarillo -> Incorrecta
                    #Rojo -> No tiene

                    #Validar selector de fecha
                    #Selector de área va a ser selector de cámara

                    #Últimas incidencias -> Mostrar 5 últimas del día actual

                    #Para usuario de seguridad filtrar los resultados de incidencias

                    #El rango de fechas por defecto del dashboard debe ser la semana actual

                    #Implementar búsqueda de usuarios y colaboradores

                    #Añadir conteo de 3 segundos al momento de tomar foto

                    if category == 'Incorrect_Mask':
                        context['recommendation'] = 'Recomendacion mascara incorrecta'
                        incident_category = IncidentCategory.objects.get(id=1)
                    elif category == 'Without_Mask':
                        context['recommendation'] = 'Recomendacion sin mascara'
                        incident_category = IncidentCategory.objects.get(id=4)

                    Incident(incident_category=incident_category, worker=worker, camera=camera, security_user=camera.security_user,
                             image="incident_images/test_incident.jpg", date_time=timezone.now()).save()

                    context['success'] = False
                except ObjectDoesNotExist:
                    context['success'] = False
                    context['recommendation'] = "DNI Invalido"

    return JsonResponse(context)


def camera_instance(request, id):
    context = {
        'camera_id': id
    }

    return render(request, 'incidents/camera_instance.html', context)
