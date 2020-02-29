from core.models import get_current_event
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from modules.email import send_paw_email

from .models import Event, Performer

# Create your views here.
def index(request):
    return render(request, "performer.html", {'is_djs': True})

def apply(request):
    event = get_current_event()
    context = {
        'is_djs': True,
        'event': event
    }
    return render(request, 'performer-apply.html', context)

def new(request):
    try:
        event = Event.objects.get(pk=request.POST['event'])
    except (KeyError, Event.DoesNotExist):
        event = get_current_event()
        context = {
            'is_djs': True,
            'event': event
        }
        return render(request, 'performer-apply.html', context)
    else:
        performer = Performer()
        performer.event = event
        performer.email = request.POST['email']
        performer.legal_name = request.POST['legal_name']
        performer.fan_name = request.POST['fan_name']
        performer.phone_number = request.POST['phone']
        performer.twitter_handle = request.POST['twitter']
        performer.telegram_handle = request.POST['telegram']
        performer.biography = request.POST['bio']
        performer.dj_history = request.POST['history']
        performer.set_link = request.POST['set_url']

        try:
            performer.save()
        except(IntegrityError):
            context = {
                'is_djs': True,
                'event': event,
                'error': 'Email has already applied.'
            }
            return render(request, 'performer-apply.html', context)

        send_paw_email('email-performers-confirm.html', {'performer': performer}, subject='PAWCon DJ Application', recipient_list=[performer.email], reply_to=settings.PERFORMERS_EMAIL)
        return HttpResponseRedirect(reverse('performers:confirm'))

def confirm(request):
    return render(request, 'performer-confirm.html', {'is_djs': True})
