import collections

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
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


def get_incidents_by_date_range(request, start_date, end_date, camera=False, category=False):
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
        fstart_date = timezone.make_aware(datetime.strptime(start_date, '%d/%m/%Y %H:%M'))
        incidents = incidents.filter(date_time__gte=timezone.make_aware(datetime.combine(fstart_date, datetime.min.time())))
    if end_date:
        fend_date = timezone.make_aware(datetime.strptime(end_date, '%d/%m/%Y %H:%M'))
        incidents = incidents.filter(date_time__lte=timezone.make_aware(datetime.combine(fend_date, datetime.max.time())))
    if camera and camera != 'all' and camera != 'False':
        incidents = incidents.filter(camera=camera)
    if category and category != 'all' and category != 'False':
        incidents = incidents.filter(incident_category=category)
    if not find_all:
        incidents = incidents.filter(security_user=security_user)

    ids_to_remove = []
    if start_date and end_date:
        for e in incidents:
            time = timezone.localtime(e.date_time).time().replace(second=0, microsecond=0)
            if time < fstart_date.time() or time > fend_date.time():
                ids_to_remove.append(e.id)
    elif start_date:
        for e in incidents:
            time = timezone.localtime(e.date_time).time().replace(second=0, microsecond=0)
            if time < fstart_date.time():
                ids_to_remove.append(e.id)
    elif end_date:
        for e in incidents:
            time = timezone.localtime(e.date_time).time().replace(second=0, microsecond=0)
            if time > fend_date.time():
                ids_to_remove.append(e.id)

    incidents = incidents.exclude(id__in=ids_to_remove)

    return incidents, fstart_date, fend_date


def get_period_ranges():
    date_now = timezone.localtime(timezone.now()).replace(hour=0, minute=0, second=0, microsecond=0)

    day_start = timezone.make_aware(datetime.combine(date_now, datetime.min.time()))
    day_end = timezone.make_aware(datetime.combine(date_now, datetime.max.time()))

    prev_day_start = timezone.make_aware(datetime.combine(date_now - timedelta(days=1), datetime.min.time()))
    prev_day_end = timezone.make_aware(datetime.combine(date_now - timedelta(days=1), datetime.max.time()))

    week_start = timezone.make_aware(datetime.combine(date_now - timedelta(days=date_now.weekday()), datetime.min.time()))
    week_end = day_end

    prev_week_start = timezone.make_aware(datetime.combine(week_start - timedelta(days=7), datetime.min.time()))
    prev_week_end = timezone.make_aware(datetime.combine(week_end - timedelta(days=7), datetime.max.time()))

    month_start = timezone.make_aware(datetime.combine(date_now.replace(day=1), datetime.min.time()))
    month_end = day_end
    
    prev_month_start = timezone.make_aware(datetime.combine((month_start - timedelta(days=1)).replace(day=1), datetime.min.time()))

    prev_month_end = prev_month_start.replace(day=28) + timedelta(days=4)
    prev_month_end = timezone.make_aware(datetime.combine(prev_month_end - timedelta(days=prev_month_end.day), datetime.max.time()))

    if month_end.day < prev_month_end.day:
        prev_month_end = prev_month_end.replace(day=month_end.day)

    year_start = timezone.make_aware(datetime.combine(date_now.replace(day=1,month=1), datetime.min.time()))
    year_end = day_end

    prev_year_start = timezone.make_aware(datetime.combine(date_now.replace(day=1,month=1,year=date_now.year-1), datetime.min.time()))
    prev_year_end = timezone.make_aware(datetime.combine(date_now - relativedelta(years=1), datetime.max.time()))

    return day_start, day_end, prev_day_start, prev_day_end, week_start, week_end, prev_week_start, prev_week_end, month_start, month_end, prev_month_start, prev_month_end, year_start, year_end, prev_year_start, prev_year_end
