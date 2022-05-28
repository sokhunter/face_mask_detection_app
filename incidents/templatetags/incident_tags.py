from django.template import Library
from incidents.models import Incident
from django.db.models import Q

register = Library()

@register.simple_tag
def get_latest_unreviewed_incidents(*args):
    incidents_unchecked = Incident.objects.filter(Q(security_user=args[0]) & Q(is_reviewed=False)).order_by('-date_time')[0:args[1]]
    return incidents_unchecked


@register.simple_tag
def get_notification_count(*args):
    incidents_unchecked_count = Incident.objects.filter(Q(security_user=args[0]) & Q(is_reviewed=False)).count()
    return incidents_unchecked_count

