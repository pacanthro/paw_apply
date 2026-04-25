from django.contrib import admin

# Register your models here.
from .models import Competitor, CompetitorContent

# Register your models here.
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ('event', 'email', 'legal_name', 'fan_name')
    list_filter = ['event']

class CompetitorContentAdmin(admin.ModelAdmin):
    list_display = ('card_title', 'card_body', 'card_cta')

admin.site.register(Competitor, CompetitorAdmin)
admin.site.register(CompetitorContent, CompetitorContentAdmin)
