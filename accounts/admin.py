from django.contrib import admin
from .models import Worker, User


admin.site.register(User)
admin.site.register(Worker)
