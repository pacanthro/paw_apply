from django.contrib import admin

from .models import Performer

# Register your models here.
class PerformerAdmin(admin.ModelAdmin):
    list_display = ('event', 'email', 'legal_name', 'fan_name')
    list_filter = ['event']

admin.site.register(Performer, PerformerAdmin)
