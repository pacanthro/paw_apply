import datetime
from core.models import get_current_event
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from modules.email import send_paw_email
import logging

from .models import Event, Merchant, MerchantState, Table
from .forms import MerchantForm


def __is_merchants_full():
    max_merchants = 0
    merchant_count = 0
    event = get_current_event()
    if (event):
        max_merchants = event.max_merchants + 10
        full_table_count = Merchant.objects.filter(event=event).exclude(merchant_state=MerchantState.STATE_DELETED).filter(table_size=Table.objects.get(key="FULL")).count()
        double_table_count = Merchant.objects.filter(event=event).exclude(merchant_state=MerchantState.STATE_DELETED).filter(table_size=Table.objects.get(key="DOUB")).count() * 2
        
        merchant_count = full_table_count + double_table_count

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
        'is_merchants_full': __is_merchants_full(),
        'event': event
    }
    return render(request, 'merchants.html', context)

def apply(request):
    if (__is_merchants_full()):
        return HttpResponseRedirect(reverse('merchants:index'))

    event = get_current_event()
    form = MerchantForm()
    context = {
        'is_merchants': True,
        'event': event,
        'form': form
    }
    return render(request, 'merch-apply.html', context)

def new(request):
    if (__is_merchants_full()):
        return HttpResponseRedirect(reverse('merchants:index'))

    event = get_current_event()
    form = MerchantForm(request.POST)

    if form.is_valid():
        merchant = form.save(commit=False)
        merchant.event = event
        merchant.save()
        form.save_m2m()

        send_paw_email('email-merchant-confirm.html', {'merchant': merchant}, subject='PAWCon Merchant Application', recipient_list=[merchant.email], reply_to=settings.MERCHANT_EMAIL)

        return HttpResponseRedirect(reverse('merchants:confirm'))
    
    context = {
        'is_merchants': True,
        'event': event,
        'form': form
    }
    return render(request, 'merch-apply.html', context)

def confirm(request):
    event = get_current_event()
    
    context = {
        'is_merchants': True,
        'event': event,
    }
    return render(request, 'merch-confirm.html', context)
