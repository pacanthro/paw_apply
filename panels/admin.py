from django.contrib import admin

from .models import PanelDuration, PanelSlot, Panel

class PanelDurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ['order']

class PanelSlotsAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ['order']

class PanelAdmin(admin.ModelAdmin):
    list_display = ('event', 'panel_name', 'email', 'legal_name', 'fan_name')
    list_filter = ['event']

# Register your models here.
admin.site.register(PanelDuration, PanelDurationAdmin)
admin.site.register(PanelSlot, PanelSlotsAdmin)
admin.site.register(Panel, PanelAdmin)
