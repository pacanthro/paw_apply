from django.contrib import admin

from .models import Volunteer, TimesAvailable

# Register your models here.
admin.site.register(Volunteer)
admin.site.register(TimesAvailable)
