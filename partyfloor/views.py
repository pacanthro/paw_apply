from core.models import get_current_event, DaysAvailable
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from modules.email import send_paw_email

from .models import Event, PartyHost

# Create your views here.
def index(request):
    return render(request, 'partyfloor.html', {'is_partyfloor': True})

def apply(request):
    event = get_current_event()
    days_available = DaysAvailable.objects.filter(available_party=True)
    context =  {
        'is_partyfloor': True,
        'event': event,
        'days': days_available
    }
    return render(request, 'partyfloor-apply.html', context)

def new(request):
    try:
        event = Event.objects.get(pk=request.POST['event'])
        days = DaysAvailable.objects.filter(key__in=request.POST.getlist('days'))
    except (KeyError, Event.DoesNotExist):
        event = get_current_event()
        days_available = DaysAvailable.objects.filter(available_party=True)
        context =  {
            'is_partyfloor': True,
            'event': event,
            'days': days_available,
            'error': 'Something has gone wrong, please contact us at <a href="mailto:feedback@pacanthro.org" class="alert-link">feedback@pacanthro.org</a>'
        }
        return render(request, 'partyfloor-apply.html', context)
    else:
        email = request.POST['email']
        host_count = PartyHost.objects.filter(email=email,event=event).count()

        if (host_count > 0):
            event = get_current_event()
            days_available = DaysAvailable.objects.filter(available_party=True)
            context =  {
                'is_partyfloor': True,
                'event': event,
                'days': days_available,
                'error': "Email or Hotel Reservation has already applied."
            }
            return render(request, 'partyfloor-apply.html', context)

        host = PartyHost()
        host.event = event
        host.email = email
        host.legal_name = request.POST['legal_name']
        host.fan_name = request.POST['fan_name']
        host.phone_number = request.POST['phone']
        host.twitter_handle = request.POST['twitter']
        host.telegram_handle = request.POST['telegram']
        host.hotel_primary = request.POST['hotel_primary']
        host.hotel_ack_num = request.POST['hotel_ack_num']
        host.ack_no_smoking = request.POST.get('ack_no_smoking', default=False)
        host.ack_amplified_sound = request.POST.get('ack_amplified_sound', default=False)
        host.ack_verify_age = request.POST.get('ack_verify_age', default=False)
        host.ack_wristbands = request.POST.get('ack_wristbands', default=False)
        host.ack_closure_time = request.POST.get('ack_closure_time', default=False)
        host.ack_suspension_policy = request.POST.get('ack_suspension_policy', default=False)
        host.save()

        for day in days:
            host.party_days.add(day)

        send_paw_email('email-party-confirm.html', {'host':host}, subject='PAWCon Party Floor Submission', recipient_list=[host.email], reply_to=settings.HOTEL_EMAIL)

        return HttpResponseRedirect(reverse('partyfloor:confirm'))

def confirm(request):
    return render(request, 'partyfloor-confirm.html', {'is_partyfloor': True})
