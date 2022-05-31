import logging
import random, csv, requests, collections, uuid, base64, urllib.request, json
import pandas as pd

from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from pathlib import Path

from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from accounts.models import UserPasswordHistory, Worker, User
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.base import ContentFile
from django.utils import timezone, formats

from incidents.models import Incident, IncidentCategory, Camera
from django.db.models import Q

from django.views.decorators.csrf import csrf_exempt

from incidents.functions import get_incidents_by_request, get_incidents_by_date_range, get_period_ranges

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

    # Ordenar incidentes por fecha
    incidents = incidents.order_by('-date_time')

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

    if not incident.is_reviewed:
        try:
            async_to_sync(get_channel_layer().group_send)(
                'noti' + str(incident.security_user.id),
                {'type': 'notification_read'}
            )
        except:
            pass

    incident.delete()

    return redirect('incidents:list_incidents')


def get_incident_page(request, id):
    incident = get_object_or_404(Incident, id=id)

    context = {
        'incident': incident,
    }

    if not incident.is_reviewed and incident.security_user.id == request.user.id:
        incident.is_reviewed = True
        incident.save()

        try:
            async_to_sync(get_channel_layer().group_send)(
                'noti' + str(incident.security_user.id),
                {'type': 'notification_read'}
            )
        except:
            pass

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
    incidents, _, _ = get_incidents_by_request(request, "GET")
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
        labels.append(incident_category.name + ' (' + str(0 if total == 0 else round((local/total) * 100, 2)) + '%)')

    context = {
        'data': data,
        'labels': labels,
        'data_colors': data_colors
    }

    return JsonResponse(context)


def get_covid_database(request):
    try:
        static_dir_path = settings.STATICFILES_DIRS
        context_file_path = Path(static_dir_path[0] + '\\context')
        cached_data_file_path = Path(static_dir_path[0] + '\\cached_data.csv')

        with open(context_file_path, 'r') as f:
            content = f.readlines()

        date_now = timezone.make_naive(timezone.localtime(timezone.now()).replace(hour=0, minute=0, second=0, microsecond=0))

        last_update_date = datetime.combine(datetime.strptime(content[0], '%Y%m%d').date(), datetime.min.time())

        if date_now > last_update_date:
            data = []

            storage_csv_headers = ['CONTAGIONS_THIS_WEEK', 'CONTAGIONS_THIS_MONTH', 'CONTAGIONS_THIS_YEAR', 'CONTAGIONS_LAST_WEEK', 'CONTAGIONS_LAST_MONTH', 'CONTAGIONS_LAST_YEAR',
                                   'CONTAGIONS_INCREASE_FROM_LAST_WEEK', 'CONTAGIONS_INCREASE_FROM_LAST_MONTH', 'CONTAGIONS_INCREASE_FROM_LAST_YEAR',
                                   'DEATHS_THIS_WEEK', 'DEATHS_THIS_MONTH', 'DEATHS_THIS_YEAR', 'DEATHS_LAST_WEEK', 'DEATHS_LAST_MONTH', 'DEATHS_LAST_YEAR',
                                   'DEATHS_INCREASE_FROM_LAST_WEEK', 'DEATHS_INCREASE_FROM_LAST_MONTH', 'DEATHS_INCREASE_FROM_LAST_YEAR']

            minsa_contagion_metadata = json.loads(urllib.request.urlopen('https://www.datosabiertos.gob.pe/api/3/action/package_show?id=3423d336-63b5-4a73-af54-7f9836a9bb26').read())
            minsa_deaths_metadata = json.loads(urllib.request.urlopen('https://www.datosabiertos.gob.pe/api/3/action/package_show?id=b44c937b-7f6d-4165-be78-f7d55651ee28').read())
            contagion_data = pd.read_csv(minsa_contagion_metadata['result'][0]['resources'][0]['url'], sep=';')
            deaths_data = pd.read_csv(minsa_deaths_metadata['result'][0]['resources'][0]['url'], sep=';')

            contagions_count = contagion_data.groupby('FECHA_RESULTADO').size().reset_index(name='COUNT')
            contagions_count['FECHA_RESULTADO'] = pd.to_numeric(contagions_count['FECHA_RESULTADO'], downcast='integer')

            deaths_count = deaths_data.groupby('FECHA_FALLECIMIENTO').size().reset_index(name='COUNT')
            deaths_count['FECHA_FALLECIMIENTO'] = pd.to_numeric(deaths_count['FECHA_FALLECIMIENTO'], downcast='integer')

            _, _, _, _, week_start, week_end, prev_week_start, prev_week_end, month_start, month_end, prev_month_start, prev_month_end, year_start, year_end, prev_year_start, prev_year_end = get_period_ranges()

            contagions_week = contagions_count.loc[(contagions_count['FECHA_RESULTADO'] >= int(week_start.strftime('%Y%m%d'))) & (contagions_count['FECHA_RESULTADO'] <= int(week_end.strftime('%Y%m%d')))].sum()['COUNT']
            contagions_last_week = contagions_count.loc[(contagions_count['FECHA_RESULTADO'] >= int(prev_week_start.strftime('%Y%m%d'))) & (contagions_count['FECHA_RESULTADO'] <= int(prev_week_end.strftime('%Y%m%d')))].sum()['COUNT']

            contagions_month = contagions_count.loc[(contagions_count['FECHA_RESULTADO'] >= int(month_start.strftime('%Y%m%d'))) & (contagions_count['FECHA_RESULTADO'] <= int(month_end.strftime('%Y%m%d')))].sum()['COUNT']
            contagions_last_month = contagions_count.loc[(contagions_count['FECHA_RESULTADO'] >= int(prev_month_start.strftime('%Y%m%d'))) & (contagions_count['FECHA_RESULTADO'] <= int(prev_month_end.strftime('%Y%m%d')))].sum()['COUNT']

            contagions_year = contagions_count.loc[(contagions_count['FECHA_RESULTADO'] >= int(year_start.strftime('%Y%m%d'))) & (contagions_count['FECHA_RESULTADO'] <= int(year_end.strftime('%Y%m%d')))].sum()['COUNT']
            contagions_last_year = contagions_count.loc[(contagions_count['FECHA_RESULTADO'] >= int(prev_year_start.strftime('%Y%m%d'))) & (contagions_count['FECHA_RESULTADO'] <= int(prev_year_end.strftime('%Y%m%d')))].sum()['COUNT']

            deaths_week = deaths_count.loc[(deaths_count['FECHA_FALLECIMIENTO'] >= int(week_start.strftime('%Y%m%d'))) & (deaths_count['FECHA_FALLECIMIENTO'] <= int(week_end.strftime('%Y%m%d')))].sum()['COUNT']
            deaths_last_week = deaths_count.loc[(deaths_count['FECHA_FALLECIMIENTO'] >= int(prev_week_start.strftime('%Y%m%d'))) & (deaths_count['FECHA_FALLECIMIENTO'] <= int(prev_week_end.strftime('%Y%m%d')))].sum()['COUNT']

            deaths_month = deaths_count.loc[(deaths_count['FECHA_FALLECIMIENTO'] >= int(month_start.strftime('%Y%m%d'))) & (deaths_count['FECHA_FALLECIMIENTO'] <= int(month_end.strftime('%Y%m%d')))].sum()['COUNT']
            deaths_last_month = deaths_count.loc[(deaths_count['FECHA_FALLECIMIENTO'] >= int(prev_month_start.strftime('%Y%m%d'))) & (deaths_count['FECHA_FALLECIMIENTO'] <= int(prev_month_end.strftime('%Y%m%d')))].sum()['COUNT']

            deaths_year = deaths_count.loc[(deaths_count['FECHA_FALLECIMIENTO'] >= int(year_start.strftime('%Y%m%d'))) & (deaths_count['FECHA_FALLECIMIENTO'] <= int(year_end.strftime('%Y%m%d')))].sum()['COUNT']
            deaths_last_year = deaths_count.loc[(deaths_count['FECHA_FALLECIMIENTO'] >= int(prev_year_start.strftime('%Y%m%d'))) & (deaths_count['FECHA_FALLECIMIENTO'] <= int(prev_year_end.strftime('%Y%m%d')))].sum()['COUNT']

            data.append(str(contagions_week))
            data.append(str(contagions_month))
            data.append(str(contagions_year))
            data.append(str(contagions_last_week))
            data.append(str(contagions_last_month))
            data.append(str(contagions_last_year))

            data.append(str(round(contagions_week * 100 if contagions_last_week == 0 else ((((contagions_week / contagions_last_week)) - 1) * 100), 2)))
            data.append(str(round(contagions_month * 100 if contagions_last_month == 0 else ((((contagions_month / contagions_last_month)) - 1) * 100), 2)))
            data.append(str(round(contagions_year * 100 if contagions_last_year == 0 else ((((contagions_year / contagions_last_year)) - 1) * 100), 2)))

            data.append(str(deaths_week))
            data.append(str(deaths_month))
            data.append(str(deaths_year))
            data.append(str(deaths_last_week))
            data.append(str(deaths_last_month))
            data.append(str(deaths_last_year))

            data.append(str(round(deaths_week * 100 if deaths_last_week == 0 else ((((deaths_week / deaths_last_week)) - 1) * 100), 2)))
            data.append(str(round(deaths_month * 100 if deaths_last_month == 0 else ((((deaths_month / deaths_last_month)) - 1) * 100), 2)))
            data.append(str(round(deaths_year * 100 if deaths_last_year == 0 else ((((deaths_year / deaths_last_year)) - 1) * 100), 2)))

            with open(context_file_path, 'w') as f:
                f.truncate()
                f.write(date_now.strftime('%Y%m%d'))

            with open(cached_data_file_path, 'w') as f:
                f.truncate()
                f.writelines([','.join(storage_csv_headers), '\n', ','.join(data)])
    except:
        pass

    context = {
        'data': {}
    }

    with open(cached_data_file_path, 'r') as f:
        csvreader = csv.reader(f)
        headers = next(csvreader)
        line = []

        #There will only be one row
        for row in csvreader:
            line.append(row)

        line = line[0]
        for i, header in enumerate(headers):
            context['data'][header] = line[i]

    return JsonResponse(context)


def get_incidents_summary_charts(request):
    incident_categories = IncidentCategory.objects.all()

    data_colors = []
    data_labels = []

    for incident_category in incident_categories:
        data_colors.append(incident_category.color)
        data_labels.append(incident_category.name)

    day_start, day_end, prev_day_start, prev_day_end, week_start, week_end, prev_week_start, prev_week_end, month_start, month_end, prev_month_start, prev_month_end, year_start, year_end, prev_year_start, prev_year_end = get_period_ranges()

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

        incidents, _, _ = get_incidents_by_date_range(request, date_start, date_end, False, False)
        prev_incidents, _, _ = get_incidents_by_date_range(request, prev_date_start, prev_date_end, False, False)

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

            incident_date = timezone.make_aware(timezone.make_naive(incident.date_time))
            incident_context = {
                'id': incident.id,
                'name': incident.worker.names + ' ' + incident.worker.surnames,
                'category': incident.incident_category.name.lower(),
                'color': incident.incident_category.color,
                'image': incident.worker.photo.url,
                'date': formats.date_format(incident_date) + ' a las ' + formats.time_format(incident_date)
            }

            try:
                async_to_sync(get_channel_layer().group_send)(
                    'noti' + str(request.user.id),
                    {'type': 'notification', 'incident_context': incident_context}
                )
            except:
                pass
        else:
            context['success'] = False
            context['recommendation'] = "Error en la validacion, por favor mire bien a la camara e intentelo de nuevo"

    return JsonResponse(context)


def get_last_unchecked_incidents(request):
    if request.method == 'GET' and 'count' in request.GET:
        incidents_unchecked = Incident.objects.filter(Q(security_user=request.user) & Q(is_reviewed=False)).order_by('-date_time')[0:int(request.GET['count'])]
    else:
        incidents_unchecked = Incident.objects.filter(Q(security_user=request.user) & Q(is_reviewed=False)).order_by('-date_time')

    incident_contexts = []

    for incident in incidents_unchecked:
        incident_date = timezone.make_aware(timezone.make_naive(incident.date_time))
        incident_contexts.append({
            'id': incident.id,
            'name': incident.worker.names + ' ' + incident.worker.surnames,
            'category': incident.incident_category.name.lower(),
            'color': incident.incident_category.color,
            'image': incident.worker.photo.url,
            'date': formats.date_format(incident_date) + ' a las ' + formats.time_format(incident_date)
        })

    context = {
        'data': incident_contexts
    }

    return JsonResponse(context)


def camera_instance(request, id):
    camera = get_object_or_404(Camera, id=id, security_user=request.user)

    context = {
        'camera_id': camera.id
    }

    return render(request, 'incidents/camera_instance.html', context)