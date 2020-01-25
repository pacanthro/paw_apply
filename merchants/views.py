import datetime
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from modules.email import send_paw_email

from .models import Event, Merchant, Table

# Create your views here.
def index(request):
    return render(request, 'merchants.html', {'is_merchants': True})

def apply(request):
    event = Event.objects.get(event_end__gte=datetime.date.today())
    tables = Table.objects.order_by('order')
    context = {
        'is_merchants': True,
        'event': event,
        'tables': tables
    }
    return render(request, 'merch-apply.html', context)

def new(request):
    try:
        # Event
        event = Event.objects.get(pk=request.POST['event'])

        # table
        table = Table.objects.get(pk=request.POST['table_size'])
    except (KeyError, Event.DoesNotExist, Table.DoesNotExist):
        event = Event.objects.get(event_end__gte=datetime.date.today())
        tables = Table.objects.order_by('order')
        context = {
            'is_merchants': True,
            'event': event,
            'tables': tables,
            'error': 'Something has gone wrong, please contact us at <a href="mailto:feedback@pacanthro.org" class="alert-link">feedback@pacanthro.org</a>'
        }
        return render(request, 'merch-apply.html', context)
    else:
        merchant = Merchant()
        merchant.event = event
        merchant.email = request.POST['email']
        merchant.legal_name = request.POST['legal_name']
        merchant.fan_name = request.POST['fan_name']
        merchant.phone_number = request.POST['phone']
        merchant.table_size = table
        merchant.business_name = request.POST['business_name']
        merchant.wares_description = request.POST['wares_description']
        merchant.helper_legal_name = request.POST['helper_legal_name']
        merchant.helper_fan_name = request.POST['helper_fan_name']
        merchant.special_requests = request.POST['special_requests']

        try:
            merchant.save()
        except (IntegrityError):
            event = Event.objects.get(event_end__gte=datetime.date.today())
            tables = Table.objects.order_by('order')
            context = {
                'is_merchants': True,
                'event': event,
                'tables': tables,
                'error': 'Email has already applied.'
            }
            return render(request, 'merch-apply.html', context)

        context = {
            'is_merchants': True
        }

        send_paw_email('email-merchant-confirm.html', {'merchant': merchant}, subject='PAWCon Merchant Application', recipient_list=[merchant.email], reply_to='board@pacanthro.org')

        return HttpResponseRedirect(reverse('merchants:confirm'))

def confirm(request):
    return render(request, 'merch-confirm.html', {'is_merchants': True})
