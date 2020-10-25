from django.contrib import admin

# Register your models here.
from .models import Competitor

# Register your models here.
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ('event', 'email', 'legal_name', 'fan_name')
    list_filter = ['event']

admin.site.register(Competitor, CompetitorAdmin)
