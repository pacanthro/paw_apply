from core.models import get_current_event, DaysAvailable
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from modules.email import send_paw_email

from .forms import HostForm
from .models import Event, PartyHost

# Create your views here.
def index(request):
    event = get_current_event()
    context =  {
        'is_partyfloor': True,
        'event': event,
    }
    return render(request, 'partyfloor.html', context)

def apply(request):
    form = HostForm()
    context =  {
        'is_partyfloor': True,
        'form': form
    }
    return render(request, 'partyfloor-apply.html', context)

def new(request):
    event = get_current_event()
    form = HostForm(request.POST)

    if form.is_valid():
        host = form.save(commit=False)
        host.event = event
        host.save()
        form.save_m2m()

        send_paw_email('email-party-confirm.html', {'host':host}, subject='PAWCon Party Floor Submission', recipient_list=[host.email], reply_to=settings.HOTEL_EMAIL)

        return HttpResponseRedirect(reverse('partyfloor:confirm'))
    
    context =  {
        'is_partyfloor': True,
        'form': form
    }

    return render(request, 'partyfloor-apply.html', context)

def confirm(request):
    return render(request, 'partyfloor-confirm.html', {'is_partyfloor': True})
