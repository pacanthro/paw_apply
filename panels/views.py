import markdown

from core.models import get_current_event
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from modules.email import send_paw_email_new

from .forms import PanelForm
from .models import PanelContent

# Create your views here.
def index(request):
    event = get_current_event()
    content = PanelContent.objects.first()

    context = {
        'is_panels': True,
        'event': event,
        'page_content': markdown.markdown(content.page_interstitial)
    }
    return render(request, 'panels.html', context)

def apply(request):
    event = get_current_event()
    content = PanelContent.objects.first()
    form = PanelForm()
    
    context = {
        'is_panels': True,
        'event': event,
        'page_content': markdown.markdown(content.page_apply),
        'form': form
    }
    return render(request, 'panels-apply.html', context)

def new(request):
    event = get_current_event()
    content = PanelContent.objects.first()
    form = PanelForm(request.POST)
    
    if form.is_valid():
        panel = form.save(commit=False)
        panel.event = event
        panel.save()
        form.save_m2m()

        send_paw_email_new(content.email_submit, {'panelist':panel}, subject='PAWCon Panel Submission', recipient_list=[panel.email], reply_to=settings.PANEL_EMAIL)

        return HttpResponseRedirect(reverse('panels:confirm'))

    context = {
        'is_panels': True,
        'event': event,
        'page_content': markdown.markdown(content.page_apply),
        'form': form
    }

    return render(request, 'panels-apply.html', context)

def confirm(request):
    event = get_current_event()
    content = PanelContent.objects.first()

    context = {
        'is_panels': True,
        'event': event,
        'page_content': markdown.markdown(content.page_confirmation),
    }
    return render(request, 'panels-confirm.html', context)
