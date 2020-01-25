from django.contrib import admin

from .models import TimesAvailable, Volunteer

class TimesAvailableAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ['order']

class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('event', 'email', 'legal_name', 'fan_name')
    list_filter = ['event']

# Register your models here.
admin.site.register(TimesAvailable, TimesAvailableAdmin)
admin.site.register(Volunteer, VolunteerAdmin)
