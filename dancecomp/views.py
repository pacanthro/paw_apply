import markdown

from core.models import get_current_event
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from modules.email import send_paw_email_new

from .forms import CompetitorForm
from .models import CompetitorContent

# Create your views here.
def index(request):
    event = get_current_event()
    content = CompetitorContent.objects.first()
    context = {
        'is_dancecomp': True,
        'event': event,
        'page_content': markdown.markdown(content.page_interstitial)
    }
    return render(request, 'dancecomp.html', context)

def apply(request):
    event = get_current_event()
    content = CompetitorContent.objects.first()
    form = CompetitorForm()

    context = {
        'is_dancecomp': True,
        'event': event,
        'page_content': markdown.markdown(content.page_apply),
        'form': form
    }
    return render(request, 'dancecomp-apply.html', context)

def new(request):
    event = get_current_event()
    content = CompetitorContent.objects.first()
    form = CompetitorForm(request.POST)
    
    if form.is_valid():
        competitor = form.save(commit=False)
        competitor.event = event
        competitor.save()

        send_paw_email_new(content.email_submit, {'competitor':competitor}, subject='PAWCon Dance Comp Submission', recipient_list=[competitor.email], reply_to=settings.DANCE_EMAIL)

        return HttpResponseRedirect(reverse('dancecomp:confirm'))

    context = {
        'is_dancecomp': True,
        'event': event,
        'page_content': markdown.markdown(content.page_apply),
        'form': form
    }

    return render(request, 'dancecomp-apply.html', context)

def confirm(request):
    event = get_current_event()
    content = CompetitorContent.objects.first()

    context = {
        'is_dancecomp': True,
        'event': event,
        'page_content': markdown.markdown(content.page_confirmation)
    }

    return render(request, 'dancecomp-confirm.html', context)
