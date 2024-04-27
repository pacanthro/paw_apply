from django.contrib import admin

from .models import DaysAvailable, Department, Event, SchedulingConfig

class DaysAvailableAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'available_scheduling', 'available_party', 'party_only')
    ordering = ['order']

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name', 'description', 'order')
    ordering = ['order']

class EventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'event_start', 'event_end')
    ordering = ['event_start']

class SchedulingConfigAdmin(admin.ModelAdmin):
    list_display = ['event']

# Register your models here.
admin.site.register(DaysAvailable, DaysAvailableAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(SchedulingConfig, SchedulingConfigAdmin)
