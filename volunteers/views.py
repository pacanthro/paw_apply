import markdown

from core.models import get_current_event
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from modules.email import send_paw_email, send_paw_email_new

from .forms import VolunteerForm
from .models import VolunteerContent

# Create your views here.
def index(request):
    event = get_current_event()
    content = VolunteerContent.objects.first()
    context = {
        'is_volunteers': True,
        'event': event,
        'page_content': markdown.markdown(content.page_interstitial)
    }
    return render(request, 'volunteers.html', context)

def apply(request):
    event = get_current_event()
    content = VolunteerContent.objects.first()
    form = VolunteerForm()
    context = {
        'is_volunteers': True,
        'event': event,
        'page_content': markdown.markdown(content.page_apply),
        'form': form
    }
    return render(request, 'volunteer-apply.html', context)

def new(request):
    event = get_current_event()
    content = VolunteerContent.objects.first()
    form = VolunteerForm(request.POST)

    if form.is_valid():
        volunteer = form.save(commit=False)
        volunteer.event = event
        volunteer.save()
        form.save_m2m()

        send_paw_email_new(content.email_submit, {'volunteer': volunteer}, subject='PAWCon Volunteer Application', recipient_list=[volunteer.email], reply_to=settings.VOLUNTEER_EMAIL)

        return HttpResponseRedirect(reverse('volunteers:confirm'))
    
    context = {
        'is_volunteers': True,
        'event': event,
        'page_content': markdown.markdown(content.page_apply),
        'form': form
    }
    return render(request, 'volunteer-apply.html', context)


def confirm(request):
    event = get_current_event()
    content = VolunteerContent.objects.first()
    context =  {
        'is_volunteers': True,
        'event': event,
        'page_content': markdown.markdown(content.page_confirmation),
    }
    return render(request, 'volunteer-confirm.html', context)
