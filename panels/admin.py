from django.contrib import admin

from .models import PanelDuration, PanelSlot, Panel, PanelContent

class PanelDurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ['order']

class PanelSlotsAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ['order']

class PanelAdmin(admin.ModelAdmin):
    list_display = ('event', 'panel_name', 'email', 'legal_name', 'fan_name')
    list_filter = ['event']

class PanelContentAdmin(admin.ModelAdmin):
    list_display = ('card_title', 'card_body', 'card_cta')

# Register your models here.
admin.site.register(PanelDuration, PanelDurationAdmin)
admin.site.register(PanelSlot, PanelSlotsAdmin)
admin.site.register(Panel, PanelAdmin)
admin.site.register(PanelContent, PanelContentAdmin)
