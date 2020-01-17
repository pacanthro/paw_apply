from django.contrib import admin

from .models import Event, Department, Volunteer, DaysAvailable, TimesAvailable

# Register your models here.
admin.site.register(Event)
admin.site.register(Department)
admin.site.register(Volunteer)
admin.site.register(DaysAvailable)
admin.site.register(TimesAvailable)
