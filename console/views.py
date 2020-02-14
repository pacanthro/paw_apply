import datetime
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from modules.email import send_paw_email

from .models import Event, Merchant

# Create your views here.
def index(request):
    return render(request, 'console.html', {'is_console': True})

def merchants(request):
    event = Event.objects.filter(event_end__gte=datetime.date.today())[:1].get()
    merchants = Merchant.objects.filter(event=event)
    context = {
        'is_console': True,
        'merchants': merchants
    }
    return render(request, 'console-merchants-list.html', context)

def merchant_detail(request, merchant_id):
    merchant = get_object_or_404(Merchant, pk=merchant_id)
    context = {
        'is_console': True,
        'merchant': merchant
    }
    return render(request, 'console-merchants-detail.html', context)

def merchant_payment(request, merchant_id):
    merchant = get_object_or_404(Merchant, pk=merchant_id)
    # Update Merchant to awaiting payment.
    send_paw_email('email-merchant-payment.html', {'merchant': merchant}, subject='PAWCon Merchant Cart Ready', recipient_list=[merchant.email], reply_to='merchant@pacanthro.org')
    data = {
        'status': 'Success'
    }
    return JsonResponse(data)
