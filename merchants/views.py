import datetime
from core.models import get_current_event
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from modules.email import send_paw_email
import logging

from .models import Event, Merchant, Table

def __is_merchants_full():
    max_merchants = 0
    merchant_count = 0
    event = get_current_event()
    if (event):
        max_merchants = event.max_merchants + 10
        full_table_count = Merchant.objects.filter(event=event).filter(payment_confirmed=True).filter(table_size=Table.objects.get(key="FULL")).count()
        double_table_count = Merchant.objects.filter(event=event).filter(payment_confirmed=True).filter(table_size=Table.objects.get(key="DOUB")).count() * 2
        waitlist_full_table_count =  Merchant.objects.filter(event=event).filter(waitlist_sent=True).filter(table_size=Table.objects.get(key="FULL")).count()
        waitlist_double_table_count = Merchant.objects.filter(event=event).filter(waitlist_sent=True).filter(table_size=Table.objects.get(key="DOUB")).count() * 2

        total_tables = full_table_count + double_table_count + waitlist_full_table_count + waitlist_double_table_count

        merchant_count = total_tables >= max_merchants;

    return (merchant_count >= max_merchants)

# Create your views here.
def index(request):
    max_merchants = 0
    merchant_count = 0
    event = get_current_event()
    if (event):
        max_merchants = event.max_merchants
        merchant_count = Merchant.objects.filter(event=event).count()

    context = {
        'is_merchants': True,
        'merchant_count': merchant_count,
        'max_merchants': max_merchants,
        'is_merchants_full': False,
        'event': event
    }
    return render(request, 'merchants.html', context)

def apply(request):
    if (__is_merchants_full()):
        return HttpResponseRedirect(reverse('merchants:index'))

    event = get_current_event()
    tables = Table.objects.filter(deleted=False).order_by('order')
    context = {
        'is_merchants': True,
        'event': event,
        'tables': tables
    }
    return render(request, 'merch-apply.html', context)

def new(request):
    if (__is_merchants_full()):
        return HttpResponseRedirect(reverse('merchants:index'))

    try:
        # Event
        event = Event.objects.get(pk=request.POST['event'])

        # table
        table = Table.objects.get(pk=request.POST['table_size'])
    except (KeyError, Event.DoesNotExist, Table.DoesNotExist):
        event = get_current_event()
        tables = Table.objects.order_by('order')
        context = {
            'is_merchants': True,
            'event': event,
            'tables': tables,
            'error': 'Something has gone wrong, please contact us at <a href="mailto:feedback@pacanthro.org" class="alert-link">feedback@pacanthro.org</a>'
        }
        return render(request, 'merch-apply.html', context)
    else:
        email = request.POST['email']
        email_registered = Merchant.objects.filter(email=email,event=event).count()

        if (email_registered > 0):
            event = get_current_event()
            tables = Table.objects.order_by('order')
            context = {
                'is_merchants': True,
                'event': event,
                'tables': tables,
                'error': 'Email has already applied.'
            }
            return render(request, 'merch-apply.html', context)

        merchant = Merchant()
        merchant.event = event
        merchant.email = email
        merchant.legal_name = request.POST['legal_name']
        merchant.fan_name = request.POST['fan_name']
        merchant.phone_number = request.POST['phone']
        merchant.table_size = table
        merchant.business_name = request.POST['business_name']
        merchant.wares_description = request.POST['wares_description']
        merchant.helper_legal_name = request.POST['helper_legal_name']
        merchant.helper_fan_name = request.POST['helper_fan_name']
        merchant.special_requests = request.POST['special_requests']
        merchant.save()

        context = {
            'is_merchants': True
        }

        send_paw_email('email-merchant-confirm.html', {'merchant': merchant}, subject='PAWCon Merchant Application', recipient_list=[merchant.email], reply_to=settings.MERCHANT_EMAIL)

        return HttpResponseRedirect(reverse('merchants:confirm'))

def confirm(request):
    return render(request, 'merch-confirm.html', {'is_merchants': True})
