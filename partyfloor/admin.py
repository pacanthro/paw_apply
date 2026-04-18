from django.contrib import admin

# Register your models here.
from .models import PartyHost, PartyHostContent

# Register your models here.
class PartyHostAdmin(admin.ModelAdmin):
    list_display = ('event', 'email', 'legal_name', 'fan_name')
    list_filter = ['event']

class PartyHostContentAdmin(admin.ModelAdmin):
    list_display = ('card_title', 'card_body', 'card_cta')

admin.site.register(PartyHost, PartyHostAdmin)
admin.site.register(PartyHostContent, PartyHostContentAdmin)
