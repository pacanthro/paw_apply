from django.contrib import admin

from .models import DaysAvailable, Department, Event

# Register your models here.
admin.site.register(DaysAvailable)
admin.site.register(Department)
admin.site.register(Event)
