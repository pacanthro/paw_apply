from core.models import get_current_event
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from modules.email import send_paw_email

from .forms import PerformerForm
from .models import Event, Performer

# Create your views here.
def index(request):
    event = get_current_event()
    context = {
        'is_djs': True,
        'event': event
    }
    return render(request, "performer.html", context)

def apply(request):
    form = PerformerForm()
    context = {
        'is_djs': True,
        'form': form
    }
    return render(request, 'performer-apply.html', context)

def new(request):
    event = get_current_event()
    form = PerformerForm(request.POST)

    print(form.errors)

    if form.is_valid():
        performer = form.save(commit=False)
        performer.event = event
        performer.save()

        send_paw_email('email-performers-confirm.html', {'performer': performer}, subject='PAWCon DJ Application', recipient_list=[performer.email], reply_to=settings.PERFORMERS_EMAIL)
        return HttpResponseRedirect(reverse('performers:confirm'))
    
    context = {
        'is_djs': True,
        'form': form
    }
    return render(request, 'performer-apply.html', context)

def confirm(request):
    return render(request, 'performer-confirm.html', {'is_djs': True})
