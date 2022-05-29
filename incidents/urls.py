from django.urls import include, path

from incidents.views import (delete_incident_request, get_incident_page,
                             get_incidents_by_category_and_day_chart_data,
                             get_incidents_by_category_chart_data,
                             get_incidents_by_worker_chart_data,
                             get_incidents_chart_data, get_incidents_summary_charts,
                             list_incidents_page, list_incidents_page_csv,
                             camera_instance, camera_request, get_covid_database,
                             get_last_unchecked_incidents)

app_name = 'incidents'
urlpatterns = [
    path('incidents-chart/', get_incidents_chart_data, name='get_incidents'),
    path('incidents-by-worker-chart/', get_incidents_by_worker_chart_data,
         name='get_incidents_by_worker'),
    path('incidents-by-category-and-day-chart/', get_incidents_by_category_and_day_chart_data,
         name='get_incidents_by_category_and_day'),
    path('incidents-by-category-chart/', get_incidents_by_category_chart_data,
         name='get_incidents_by_category'),
    path('incidents-summary-charts', get_incidents_summary_charts, name='get_incidents_summary_charts'),
    path('camera_request/<int:id>/', camera_request, name='camera_request'),
    path('get_covid_database/', get_covid_database, name='get_covid_database'),
    path('get_last_unchecked_incidents/', get_last_unchecked_incidents, name='get_last_unchecked_incidents'),

    path('', list_incidents_page,
         name='list_incidents'),
    path('view/<int:id>', get_incident_page,
         name='get_incident'),
    path('delete/<int:id>/', delete_incident_request,
         name='delete_incident'),
    path('list_incidents_page_csv/', list_incidents_page_csv,
         name='list_incidents_page_csv'),
    path('camera_instance/<int:id>/', camera_instance, name='camera_instance')
]
