from django.contrib import admin

from .models import TimesAvailable, Volunteer, VolunteerContent, VolunteerTask

class TimesAvailableAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ['order']

class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('event', 'email', 'legal_name', 'fan_name')
    list_filter = ['event']

class VolunteerContentAdmin(admin.ModelAdmin):
    list_display = ('card_title', 'card_body', 'card_cta')

class VolunteerTaskAdmin(admin.ModelAdmin):
    list_display = ('event', 'volunteer', 'task_name')

# Register your models here.
admin.site.register(TimesAvailable, TimesAvailableAdmin)
admin.site.register(Volunteer, VolunteerAdmin)
admin.site.register(VolunteerContent, VolunteerContentAdmin)
admin.site.register(VolunteerTask, VolunteerTaskAdmin)
