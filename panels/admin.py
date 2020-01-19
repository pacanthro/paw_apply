from django.contrib import admin

from .models import PanelDuration, PanelSlot, Panel

# Register your models here.
admin.site.register(PanelDuration)
admin.site.register(PanelSlot)
admin.site.register(Panel)
