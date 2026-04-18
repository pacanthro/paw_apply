from django.contrib import admin

from .models import Performer, PerformerContent

class PerformerAdmin(admin.ModelAdmin):
    list_display = ('event', 'email', 'legal_name', 'fan_name')
    list_filter = ['event']


class PerformerContentAdmin(admin.ModelAdmin):
    list_display = ('card_title', 'card_body', 'card_cta')

# Register your models here.
admin.site.register(Performer, PerformerAdmin)
admin.site.register(PerformerContent, PerformerContentAdmin)
