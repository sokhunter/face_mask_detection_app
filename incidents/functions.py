import collections

from datetime import datetime
from django.utils import timezone

from incidents.models import Incident

def get_incidents_by_request(request, type):
    if request.user.role == None:
        return

    if request.method == type:
        if type == "GET":
            start_date = request.GET.get('start-date', False)
            end_date = request.GET.get('end-date', False)
            camera = request.GET.get('camera-selected', False)
            category = request.GET.get('category-selected', False)
        elif type == "POST":
            start_date = request.POST.get('start-date', False)
            end_date = request.POST.get('end-date', False)
            camera = request.POST.get('camera-selected', False)
            category = request.POST.get('category-selected', False)
        incidents, fstart_date, fend_date = get_incidents_by_date_range(request, start_date, end_date, camera, category)
    else:
        incidents, fstart_date, fend_date = get_incidents_by_date_range(request, False, False, False, False)

    return incidents, fstart_date, fend_date


def get_incidents_by_date_range(request, start_date, end_date, camera, category):
    fstart_date = None
    fend_date = None

    if request.user.role == None:
        return

    if request.user.role.name == 'admin':
        find_all = True
    elif request.user.role.name == 'security':
        find_all = False
        security_user = request.user

    incidents = Incident.objects.all()

    if start_date:
        fstart_date = timezone.make_aware(datetime.combine(datetime.strptime(start_date, '%d/%m/%Y').date(), datetime.min.time()))
        incidents = incidents.filter(date_time__gte=fstart_date)
    if end_date:
        fend_date = timezone.make_aware(datetime.combine(datetime.strptime(end_date, '%d/%m/%Y').date(), datetime.max.time()))
        incidents = incidents.filter(date_time__lte=fend_date)
    if camera and camera != 'all' and camera != 'False':
        incidents = incidents.filter(camera=camera)
    if category and category != 'all' and category != 'False':
        incidents = incidents.filter(incident_category=category)
    if not find_all:
        incidents = incidents.filter(security_user=security_user)

    return incidents, fstart_date, fend_date
