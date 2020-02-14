import datetime
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from modules.email import send_paw_email

from .models import Event, DaysAvailable, Panel, PanelDuration, PanelSlot

# Create your views here.
def index(request):
    return render(request, 'panels.html', {'is_panels': True})

def apply(request):
    event = Event.objects.filter(event_end__gte=datetime.date.today())[:1].get()
    days = DaysAvailable.objects.filter(available_scheduling=True).order_by('order')
    durations = PanelDuration.objects.order_by('order')
    time_slots = PanelSlot.objects.order_by('order')
    context = {
        'is_panels': True,
        'event': event,
        'days': days,
        'durations': durations,
        'time_slots': time_slots
    }
    return render(request, 'panels-apply.html', context)

def new(request):
    try:
        # Event
        event = Event.objects.get(pk=request.POST['event'])

        # Duration
        duration = PanelDuration.objects.get(pk=request.POST['panel_duration'])

        # Days Available
        days = DaysAvailable.objects.filter(key__in=request.POST.getlist('panel_day'))

        # Time Slots
        time_slots = PanelSlot.objects.filter(key__in=request.POST.getlist('panel_slot'))
    except ():
        event = Event.objects.filter(event_end__gte=datetime.date.today())[:1].get()
        days = DaysAvailable.objects.order_by('order')
        durations = PanelDuration.objects.order_by('order')
        time_slots = PanelSlot.objects.order_by('order')
        context = {
            'is_panels': True,
            'event': event,
            'days': days,
            'durations': durations,
            'time_slots': time_slots,
            'error': 'Something has gone wrong, please contact us at <a href="mailto:feedback@pacanthro.org" class="alert-link">feedback@pacanthro.org</a>'
        }
        return render(request, 'panels-apply.html', context)
    else:
        panel = Panel()
        panel.event = event
        panel.email = request.POST['email']
        panel.legal_name = request.POST['legal_name']
        panel.fan_name = request.POST['fan_name']
        panel.phone_number = request.POST['phone']
        panel.twitter_handle = request.POST['twitter']
        panel.telegram_handle = request.POST['telegram']
        panel.panelist_bio = request.POST['panelist_bio']
        panel.panel_name = request.POST['panel_name']
        panel.panel_description = request.POST['panel_description']
        panel.equipment_needs = request.POST['equipment_needs']
        panel.panel_duration = duration
        panel.mature_content = request.POST.get('mature_content', default=False)
        panel.check_ids = request.POST.get('check_ids', default=False)
        panel.save()

        for day in days:
            panel.panel_day.add(day)

        for time_slot in time_slots:
            panel.panel_times.add(time_slot)

        send_paw_email('email-panels-confirm.html', {'panelist':panel}, subject='PAWCon Panel Submission', recipient_list=[panel.email], reply_to=settings.PANEL_EMAIL)

        return HttpResponseRedirect(reverse('panels:confirm'))

def confirm(request):
    return render(request, 'panels-confirm.html', {'is_panels': True})
