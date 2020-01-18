from django.contrib import admin

from .models import PanelDuration, PanelSlots, Panel

# Register your models here.
admin.site.register(PanelDuration)
admin.site.register(PanelSlots)
admin.site.register(Panel)
