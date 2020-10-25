from django.contrib import admin

# Register your models here.
from .models import PartyHost

# Register your models here.
class PartyHostAdmin(admin.ModelAdmin):
    list_display = ('event', 'email', 'legal_name', 'fan_name')
    list_filter = ['event']

admin.site.register(PartyHost, PartyHostAdmin)
