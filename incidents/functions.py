import collections

from datetime import datetime

from incidents.models import Incident

def get_incidents_by_request(request, type):
    fstart_date = None
    fend_date = None

    if request.method == type:
        if type == "GET":
            start_date = request.GET.get('start-date', False)
            end_date = request.GET.get('end-date', False)
        elif type == "POST":
            start_date = request.POST.get('start-date', False)
            end_date = request.POST.get('end-date', False)
        incidents, fstart_date, fend_date = get_incidents_by_date_range(start_date, end_date)
    else:
        incidents = Incident.objects.all()

    return incidents, fstart_date, fend_date


def get_incidents_by_date_range(start_date, end_date):
    fstart_date = None
    fend_date = None

    if start_date and end_date:
        fstart_date = datetime.strptime(start_date, '%d/%m/%Y').date()
        fend_date = datetime.strptime(end_date, '%d/%m/%Y').date()
        incidents = Incident.objects.filter(
            date_time__gte=fstart_date, date_time__lte=fend_date)
    elif start_date:
        fstart_date = datetime.strptime(start_date, '%d/%m/%Y').date()
        incidents = Incident.objects.filter(
            date_time__gte=fstart_date)
    elif end_date:
        fend_date = datetime.strptime(end_date, '%d/%m/%Y').date()
        incidents = Incident.objects.filter(
            date_time__lte=fend_date)
    else:
        incidents = Incident.objects.all()

    return incidents, fstart_date, fend_date


def interpolate_incidents_data(data, labels):
    pass
    """
        counter = collections.Counter(list(map(lambda x : x.date_time_truncated, incidents)))

    data = []
    labels = []

    if len(counter.keys()) != 0:
        sorted_counter_keys = sorted(counter.keys())

        current_date = sorted_counter_keys[0]
        last_date = sorted_counter_keys[len(sorted_counter_keys) - 1]

        while current_date <= last_date:
            data.append(counter[current_date])
            labels.append(current_date.strftime('%d/%m/%Y'))
            current_date += timedelta(days=1)

    return data, labels
    """