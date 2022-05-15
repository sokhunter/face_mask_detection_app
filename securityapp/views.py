import json

from django.shortcuts import render
from incidents.functions import get_incidents_by_date_range
from incidents.models import IncidentCategory
from django.core.paginator import Paginator
from django.utils import timezone

def home_page(request):
    start_date = None
    end_date = None

    if request.method == "GET":
        start_date = request.GET.get('start-date', False)
        end_date = request.GET.get('end-date', False)
    elif request.method == "POST":
        start_date = request.POST.get('start-date', False)
        end_date = request.POST.get('end-date', False)

    date_now = timezone.now()

    start_date_condition = start_date != None and start_date != False
    end_date_condition = end_date != None and end_date != False

    start_date = start_date if start_date_condition or end_date_condition else (date_now - timezone.timedelta(days=7)).strftime('%d/%m/%Y')
    end_date = end_date if start_date_condition or end_date_condition else date_now.strftime('%d/%m/%Y')

    incidents, fstart_date, fend_date = get_incidents_by_date_range(start_date, end_date)
    incident_categories = IncidentCategory.objects.all()

    if request.GET.get('view_all_incidents', 0) == 1:
        incidents = Paginator(incidents, 3).page(3)

    start_date = fstart_date.strftime('%d/%m/%Y') if fstart_date is not None else ''
    end_date = fend_date.strftime('%d/%m/%Y') if fend_date is not None else ''

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'categories': incident_categories
    }

    return render(request, 'incidents/dashboard.html', context)
