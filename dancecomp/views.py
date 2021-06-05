from core.models import get_current_event
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from modules.email import send_paw_email

from .models import Competitor, Event

# Create your views here.
def index(request):
    return render(request, 'dancecomp.html', {'is_dancecomp': True})

def apply(request):
    event = get_current_event()
    context = {
        'is_dancecomp': True,
        'event': event
    }
    return render(request, 'dancecomp-apply.html', context)

def new(request):
    try:
        event = Event.objects.get(pk=request.POST['event'])
    except (KeyError, Event.DoesNotExist):
        event = get_current_event()
        context = {
            'is_dancecomp': True,
            'event': event,
            'error': 'Something has gone wrong, please contact us at <a href="mailto:feedback@pacanthro.org" class="alert-link">feedback@pacanthro.org</a>'
        }
        return render(request, 'dancecomp-apply.html', context)
    else:
        if (request.POST.get('is_group', default=False)):
            if(request.POST.get('performer_two', default=None) == None or len(request.POST.get('performer_two')) == 0):
                event = get_current_event()
                context = {
                    'is_dancecomp': True,
                    'event': event,
                    'error': 'If applying as a group you must specify at least one other performer name.'
                }
                return render(request, 'dancecomp-apply.html', context)
        email = request.POST['email']
        competitor_count = Competitor.objects.filter(email=email, event=event).count()

        if (competitor_count > 0):
            event = get_current_event()
            context = {
                'is_dancecomp': True,
                'event': event,
                'error': 'That email has already applied.'
            }

            return render(request, 'dancecomp-apply.html', context)


        competitor = Competitor()
        competitor.event = event
        competitor.email = email
        competitor.legal_name = request.POST['legal_name']
        competitor.fan_name = request.POST['fan_name']
        competitor.competitor_name = request.POST['competitor_name']
        competitor.phone_number = request.POST['phone']
        competitor.twitter_handle = request.POST['twitter']
        competitor.telegram_handle = request.POST['telegram']
        competitor.music_url = request.POST['music_url']
        competitor.is_group = request.POST.get('is_group', default=False)

        if (competitor.is_group):
            competitor.performer_two = request.POST['performer_two']
            competitor.performer_three = request.POST['performer_three']
            competitor.performer_four = request.POST['performer_four']
            competitor.performer_five = request.POST['performer_five']

        competitor.save()

        send_paw_email('email-dance-confirm.html', {'competitor':competitor}, subject='PAWCon Damce Comp Submission', recipient_list=[competitor.email], reply_to=settings.DANCE_EMAIL)

        return HttpResponseRedirect(reverse('dancecomp:confirm'))

def confirm(request):
    return render(request, 'dancecomp-confirm.html', {'is_dancecomp': True})
