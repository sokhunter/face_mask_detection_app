import json

from django.shortcuts import render
from incidents.functions import get_incidents_by_date_range
from incidents.models import IncidentCategory, Camera
from django.utils import timezone
from datetime import datetime
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def home_page(request):
    if not request.user.is_authenticated:
        # return render(request, 'incidents/dashboard.html')
        response = redirect('/accounts/login_security/')
        return response

    if request.method == "GET":
        start_date = request.GET.get('start-date', False)
        end_date = request.GET.get('end-date', False)
        camera = request.GET.get('camera-selected', False)
        category = request.GET.get('category-selected', False)
    elif request.method == "POST":
        start_date = request.POST.get('start-date', False)
        end_date = request.POST.get('end-date', False)
        camera = request.POST.get('camera-selected', False)
        category = request.POST.get('category-selected', False)

    date_now = timezone.localtime(timezone.now())

    start_date_condition = start_date != False
    end_date_condition = end_date != False

    default_start_date = (datetime.combine(date_now, datetime.min.time()) - timezone.timedelta(days=7)).strftime('%d/%m/%Y %H:%M')
    default_end_date = datetime.combine(date_now, datetime.max.time()).strftime('%d/%m/%Y %H:%M')

    start_date = start_date if start_date_condition or end_date_condition else default_start_date
    end_date = end_date if start_date_condition or end_date_condition else default_end_date

    date_start_to_validate = timezone.make_aware(datetime.combine(datetime.strptime(start_date, '%d/%m/%Y %H:%M').date(), datetime.min.time()))
    date_end_to_validate = timezone.make_aware(datetime.combine(datetime.strptime(end_date, '%d/%m/%Y %H:%M').date(), datetime.min.time()))

    invalid_date_range = False

    if date_start_to_validate > date_end_to_validate:
        invalid_date_range = True
        start_date = default_start_date
        end_date = default_end_date

    incidents, fstart_date, fend_date = get_incidents_by_date_range(request, start_date, end_date, camera, category)

    incidents = incidents[:5]

    incident_categories = IncidentCategory.objects.all()

    if request.user.role.name == 'admin':
        find_all = True
    elif request.user.role.name == 'security':
        find_all = False
        security_user = request.user

    cameras = Camera.objects.all()

    if not find_all:
        cameras = cameras.filter(security_user=security_user)

    start_date = fstart_date if fstart_date is not None else ''
    end_date = fend_date if fend_date is not None else ''
    
    #DESCRIPCIONES DE LOS CARDS EN EL DASHBOARD (ESPAÑOL)

    import locale
    locale.setlocale(locale.LC_ALL, ("es_ES", "UTF-8"))

    start_year= (start_date).strftime('%Y')
    start_month= (start_date).strftime('%B')
    start_day= (start_date).strftime('%d')
    start_hour= (start_date).strftime('%H:%M')
    #start_hour= (start_date).strftime('%I:%M %p')

    end_year= (end_date).strftime('%Y')
    end_month= (end_date).strftime('%B')
    end_day= (end_date).strftime('%d')
    end_hour= (end_date).strftime('%H:%M')
    #end_hour= (end_date).strftime('%I:%M %p')


    context = {
        'start_date': start_date,
        'end_date': end_date,
        'incident_categories': incident_categories,
        'cameras': cameras,
        'incidents': incidents,
        'category_selected': category,
        'camera_selected': camera,
        'invalid_date_range': invalid_date_range,
        'start_year':start_year,
        'start_month':start_month,
        'start_day':start_day,
        'start_hour':start_hour,
        'end_year':end_year,
        'end_month':end_month,
        'end_day':end_day,
        'end_hour':end_hour,
        'max_date': datetime.combine(date_now, datetime.max.time())
    }

    return render(request, 'incidents/dashboard.html', context)
