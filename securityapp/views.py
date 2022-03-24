import json
from django.shortcuts import render


def home_page(request):
    return render(request, 'incidents/dashboard.html')
