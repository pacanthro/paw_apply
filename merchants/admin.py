from django.contrib import admin

from .models import Table, Merchant

class TableAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ['order']

class MerchantAdmin(admin.ModelAdmin):
    list_display = ('event', 'business_name', 'email', 'legal_name', 'fan_name')
    list_filter = ('event', 'merchant_state')

# Register your models here.
admin.site.register(Table, TableAdmin)
admin.site.register(Merchant, MerchantAdmin)
