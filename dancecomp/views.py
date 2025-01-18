from core.models import get_current_event
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from modules.email import send_paw_email

from .forms import CompetitorForm
from .models import Competitor, Event

# Create your views here.
def index(request):
    event = get_current_event()
    context = {
        'is_dancecomp': True,
        'event': event
    }
    return render(request, 'dancecomp.html', context)

def apply(request):
    event = get_current_event()

    form = CompetitorForm()

    context = {
        'is_dancecomp': True,
        'event': event,
        'form': form
    }
    return render(request, 'dancecomp-apply.html', context)

def new(request):
    event = get_current_event()
    form = CompetitorForm(request.POST)
    
    if form.is_valid():
        competitor = form.save(commit=False)
        competitor.event = event
        competitor.save()

        send_paw_email('email-dance-confirm.html', {'competitor':competitor}, subject='PAWCon Dance Comp Submission', recipient_list=[competitor.email], reply_to=settings.DANCE_EMAIL)

        return HttpResponseRedirect(reverse('dancecomp:confirm'))

    for field, errors in form.errors.items():
        for error in errors:
            print(f"Form Error: {field}: {error}")

    context = {
        'is_dancecomp': True,
        'event': event,
        'form': form
    }

    return render(request, 'dancecomp-apply.html', context)

def confirm(request):
    event = get_current_event()

    context = {
        'event': event,
        'is_dancecomp': True
    }

    return render(request, 'dancecomp-confirm.html', context)
