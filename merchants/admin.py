from django.contrib import admin

from .models import Event, Table, Merchant

# Register your models here.
admin.site.register(Event)
admin.site.register(Table)
admin.site.register(Merchant)
