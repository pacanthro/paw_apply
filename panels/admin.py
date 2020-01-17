from django.contrib import admin

from .models import Event, PanelDuration, DaysAvailable, PanelSlots, Panel

# Register your models here.
admin.site.register(Event)
admin.site.register(PanelDuration)
admin.site.register(DaysAvailable)
admin.site.register(PanelSlots)
admin.site.register(Panel)
