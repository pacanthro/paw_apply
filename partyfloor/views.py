import markdown

from core.models import get_current_event, ApplicationState
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from modules.email import send_paw_email, send_paw_email_new

from .forms import HostForm
from .models import PartyHost, PartyHostContent

def __is_partyfloor_full():
    max_partyhosts = 0
    partyhosts_count = 0
    event = get_current_event()
    if (event):
        max_partyhosts = event.max_party_rooms + 5
        partyhosts_count = PartyHost.objects.filter(event=event).exclude(Q(host_state=ApplicationState.STATE_DENIED) | Q(host_state=ApplicationState.STATE_DELETED) | Q(host_state=ApplicationState.STATE_OLD)).count()

    return (partyhosts_count >= max_partyhosts)

# Create your views here.
def index(request):
    event = get_current_event()
    content = PartyHostContent.objects.first()
    context =  {
        'is_partyfloor': True,
        'is_partyfloor_full': __is_partyfloor_full(),
        'event': event,
        'page_content': markdown.markdown(content.page_interstitial)
    }
    return render(request, 'partyfloor.html', context)

def apply(request):
    if (__is_partyfloor_full()):
        return HttpResponseRedirect(reverse('partyfloor:index'))
    
    event = get_current_event()
    content = PartyHostContent.objects.first()
    form = HostForm()
    context =  {
        'is_partyfloor': True,
        'event': event,
        'page_content': markdown.markdown(content.page_apply),
        'form': form
    }
    return render(request, 'partyfloor-apply.html', context)

def new(request):
    event = get_current_event()
    content = PartyHostContent.objects.first()
    form = HostForm(request.POST)

    if form.is_valid():
        host = form.save(commit=False)
        host.event = event
        host.save()
        form.save_m2m()

        send_paw_email_new(content.email_submit, {'host':host}, subject='PAWCon Party Floor Submission', recipient_list=[host.email], reply_to=settings.HOTEL_EMAIL)

        return HttpResponseRedirect(reverse('partyfloor:confirm'))
    
    context =  {
        'is_partyfloor': True,
        'event': event,
        'page_content': markdown.markdown(content.page_apply),
        'form': form
    }

    return render(request, 'partyfloor-apply.html', context)

def confirm(request):
    event = get_current_event()
    content = PartyHostContent.objects.first()

    context =  {
        'is_partyfloor': True,
        'event': event,
        'page_content': markdown.markdown(content.page_confirmation)
    }
    return render(request, 'partyfloor-confirm.html', context)
