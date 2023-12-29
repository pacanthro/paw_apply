import datetime
from core.models import get_current_event
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from modules.email import send_paw_email

from .forms import PanelForm
from .models import Event, DaysAvailable, Panel, PanelDuration, PanelSlot

# Create your views here.
def index(request):
    event = get_current_event()
    context = {
        'is_panels': True,
        'event': event
    }
    return render(request, 'panels.html', context)

def apply(request):
    event = get_current_event()
    form = PanelForm()
    
    context = {
        'is_panels': True,
        'event': event,
        'form': form
    }
    return render(request, 'panels-apply.html', context)

def new(request):
    event = get_current_event()
    form = PanelForm(request.POST)
    
    if form.is_valid():
        panel = form.save(commit=False)
        panel.event = event
        panel.save()
        form.save_m2m()

        send_paw_email('email-panels-confirm.html', {'panelist':panel}, subject='PAWCon Panel Submission', recipient_list=[panel.email], reply_to=settings.PANEL_EMAIL)

        return HttpResponseRedirect(reverse('panels:confirm'))

    context = {
        'is_panels': True,
        'event': event,
        'form': form
    }

    return render(request, 'panels-apply.html', context)

def confirm(request):
    event = get_current_event()
    context = {
        'is_panels': True,
        'event': event,
    }
    return render(request, 'panels-confirm.html', context)
