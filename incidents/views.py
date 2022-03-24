import random
from datetime import datetime

from accounts.models import Worker
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from incidents.models import Incident, IncidentCategory


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
        for i, worker in enumerate(workers):
            date_time = datetime(year=2021, month=random.randint(10, 11),
                                 day=random.randint(1, 30), hour=random.randint(10, 19), minute=random.randint(0, 59), second=random.randint(0, 59))
            Incident(incident_category=incidents_categories[i % len(incidents_categories)], worker=worker,
                     date_time=date_time).save()


def list_incidents_page(request):
    if not Incident.objects.all() or not IncidentCategory.objects.all():
        create_false_data()

    if request.method == "POST":
        start_date = request.POST.get(request.POST['start-date'], False)
        end_date = request.POST.get(request.POST['end-date'], False)
        if request.POST['start-date'] and request.POST['end-date']:
            start_date = request.POST['start-date']
            end_date = request.POST['end-date']
            fstart_date = datetime.strptime(start_date, '%d/%m/%Y').date()
            fend_date = datetime.strptime(end_date, '%d/%m/%Y').date()
            incidents = Incident.objects.filter(
                date_time__gte=fstart_date, date_time__lte=fend_date)
        elif request.POST['start-date']:
            start_date = request.POST['start-date']
            fstart_date = datetime.strptime(start_date, '%d/%m/%Y').date()
            incidents = Incident.objects.filter(
                date_time__gte=fstart_date)
        elif request.POST['end-date']:
            end_date = request.POST['end-date']
            fend_date = datetime.strptime(end_date, '%d/%m/%Y').date()
            incidents = Incident.objects.filter(
                date_time__lte=fend_date)
        else:
            incidents = Incident.objects.all()
    else:
        incidents = Incident.objects.all()

    context = {
        'incidents': incidents
    }
    return render(request, 'incidents/list.html', context)


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
    data = [5, 7, 2, 5, 8, 4, 10]
    labels = ['Lunes', 'Martes', 'Miercoles',
              'Jueves', 'Viernes', 'Sábado', 'Domingo']
    context = {
        'max_incidents': 3,
        'data': data,
        'labels': labels,
    }
    return JsonResponse(context)


def get_incidents_by_worker_chart_data(request):
    data = [4, 3, 3, 2, 1, 1, 1]
    labels = ['Sergio', 'Camila', 'Elizabeth',
              'Cesar', 'Bryan', 'Benjamin', 'Lucero']
    context = {
        'max_incidents': 2,
        'data': data,
        'labels': labels,
    }
    return JsonResponse(context)


def get_incidents_by_category_and_day_chart_data(request):
    labels = ['Lunes', 'Martes', 'Miercoles',
              'Jueves', 'Viernes', 'Sábado', 'Domingo']
    data = []
    data_labels = ['Sin mascarilla', 'Bajo la barbilla',
                   'Cubre solo boca y barbilla', 'Cubre solo boca y nariz']
    data.append([0, 1, 2, 0, 0, 1, 1])
    data.append([1, 0, 0, 2, 3, 1, 2])
    data.append([2, 4, 3, 3, 5, 5, 4])
    data.append([4, 2, 5, 4, 1, 4, 4])

    context = {
        'data': data,
        'data_labels': data_labels,
        'labels': labels,
    }
    return JsonResponse(context)


def get_incidents_by_category_chart_data(request):
    data = [5, 9, 26, 24]
    labels = ['Sin mascarilla (5%)', 'Bajo la barbilla (10%)',
              'Cubre solo boca y barbilla (45%)', 'Cubre solo boca y nariz (40%)']
    context = {
        'data': data,
        'labels': labels,
    }
    return JsonResponse(context)
