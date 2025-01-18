from typing import Any
from console.forms import PanelScheduleRoomDayForm, PanelScheduleSlotForm
from core.models import get_current_event, ApplicationState, EventRoom, RoomType, SchedulingConfig
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse, resolve
from django.utils.decorators import method_decorator
from django.views.generic.base import RedirectView
from modules.email import send_paw_email
from panels.models import Panel

from .page_view import PageView

from urllib.parse import urlparse
from datetime import date, timedelta
from datetimerange import DateTimeRange

decorators = [login_required, permission_required('panels.view_panel')]

def _toTimeDelta(duration):
    match duration.key:
        case "60MN":
            return timedelta(minutes=60)
        case "90MN":
            return timedelta(minutes=90)
        case "120M":
            return timedelta(minutes=120)


@method_decorator(decorators, name="dispatch")
class PanelsListPageView(PageView):
    template_name="console-panels-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_current_event()
        panels = Panel.objects.filter(event=event).filter(panel_state=ApplicationState.STATE_NEW)
        panels_accepted = Panel.objects.filter(event=event).filter(panel_state=ApplicationState.STATE_ACCEPTED)
        panels_scheduled = Panel.objects.filter(event=event).filter(panel_state=ApplicationState.STATE_ASSIGNED)
        panels_canceled = Panel.objects.filter(event=event).filter(panel_state=ApplicationState.STATE_CANCELED)
        panels_waitlisted = Panel.objects.filter(event=event).filter(panel_state=ApplicationState.STATE_WAITLIST)
        panels_denied = Panel.objects.filter(event=event).filter(panel_state=ApplicationState.STATE_DENIED)

        context['panels'] = panels
        context['panels_accepted'] = panels_accepted
        context['panels_scheduled'] = panels_scheduled
        context['panels_canceled'] = panels_canceled
        context['panels_waitlisted'] = panels_waitlisted
        context['panels_denied'] = panels_denied

        return context

@method_decorator(decorators, name="dispatch")
class PanelDetailsPageView(PageView):
     template_name = 'console-panels-detail.html'

     def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        panel = get_object_or_404(Panel, pk=kwargs['panel_id'])

        context['panel'] = panel
        
        return context

@method_decorator(decorators, name="dispatch")
class PanelActionAcceptRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:panel-detail'

    def get_redirect_url(self, *args, **kwargs):
        panel = get_object_or_404(Panel, pk=kwargs['panel_id'])
        panel.panel_state = ApplicationState.STATE_ACCEPTED
        panel.state_changed = date.today()
        panel.save()

        send_paw_email('email-panels-accepted.html', {'panelist':panel}, subject='PAWCon Panel Accepted', recipient_list=[panel.email], reply_to=settings.PANEL_EMAIL)

        return super().get_redirect_url(*args, **kwargs)
    
@method_decorator(decorators, name="dispatch")
class PanelActionWaitlistRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:panel-detail'

    def get_redirect_url(self, *args, **kwargs):
        panel = get_object_or_404(Panel, pk=kwargs['panel_id'])
        panel.panel_state = ApplicationState.STATE_WAITLIST
        panel.state_changed = date.today()
        panel.save()

        send_paw_email('email-panels-waitlisted.html', {'panelist':panel}, subject='PAWCon Panel Waitlisted', recipient_list=[panel.email], reply_to=settings.PANEL_EMAIL)

        return super().get_redirect_url(*args, **kwargs)

@method_decorator(decorators, name="dispatch")
class PanelActionDenyRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:panel-detail'

    def get_redirect_url(self, *args, **kwargs):
        panel = get_object_or_404(Panel, pk=kwargs['panel_id'])
        panel.panel_state = ApplicationState.STATE_DENIED
        panel.state_changed = date.today()
        panel.save()

        send_paw_email('email-panels-declined.html', {'panelist':panel}, subject='PAWCon Panel Denied', recipient_list=[panel.email], reply_to=settings.PANEL_EMAIL)

        return super().get_redirect_url(*args, **kwargs)

@method_decorator(decorators, name="dispatch")
class PanelActionDeleteRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:panels'

    def get_redirect_url(self, *args, **kwargs):
        panel = get_object_or_404(Panel, pk=kwargs['panel_id'])
        panel.panel_state = ApplicationState.STATE_DELETED
        panel.state_changed = date.today()
        panel.save()
        return reverse('console:panels')

@method_decorator(decorators, name="dispatch")
class PanelSchedulePageView(PageView):
    template_name="console-panels-schedule.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_current_event()
        event_rooms = EventRoom.objects.filter(event=event).filter(room_type=RoomType.ROOM_PANELS)

        panels_unsched = Panel.objects.filter(event=event).filter(panel_state=ApplicationState.STATE_ACCEPTED)

        forms = []
        for panel in panels_unsched:
            form = PanelScheduleRoomDayForm(instance=panel)

            forms.append(form)

        schedulingConfigs = SchedulingConfig.objects.filter(event=event).order_by('day_available__order')

        schedules = []
        for config in schedulingConfigs:
            slots = [] 
            timeRange = DateTimeRange(config.panels_start, config.panels_end)
            for value in timeRange.range(timedelta(minutes=30)):
                slots.append(value)
            
            schedules.append({'day': config.day_available, 'slots': slots})


        assignedPanels = Panel.objects.filter(event=event).filter(Q(panel_state=ApplicationState.STATE_ASSIGNED) | Q(panel_state=ApplicationState.STATE_CANCELED))

        filledSlots = []
        for assignedPanel in assignedPanels:
            timeDelta = _toTimeDelta(assignedPanel.panel_duration)
            filledSlots.append({
                'panel': assignedPanel,
                'end_time': assignedPanel.scheduled_time + timeDelta
            })

        context['event_rooms'] = event_rooms
        context['panels_unsched'] = forms
        context['schedules'] = schedules
        context['filled_slots'] = filledSlots

        return context

@method_decorator(decorators, name="dispatch")
class PanelActionAssignPageView(PageView):
    template_name="console-panels-assign.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        panel = get_object_or_404(Panel, pk=kwargs['panel_id'])
        form = PanelScheduleRoomDayForm(instance=panel)

        context['panel'] = panel
        context['form'] = form

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        currentEvent = get_current_event()

        if context['panel'].scheduled_day is None:
            form = PanelScheduleRoomDayForm(request.POST, instance=context['panel'])

            context['form'] = form

            if form.is_valid():
                panel = form.save()
                context['panel'] = panel

                days = self._get_slots(currentEvent, panel.scheduled_day)
                form = PanelScheduleSlotForm(instance=context['panel'], options=days[0]['slots'])
            
                context['form'] = form
                return self.render_to_response(context)

            return self.render_to_response(context)
        else:
            days = self._get_slots(currentEvent, context['panel'].scheduled_day)
            form = PanelScheduleSlotForm(request.POST, instance=context['panel'], options=days[0]['slots'])
            
            context['form'] = form

            if form.is_valid():
                panel = form.save(commit=False)
                panel.panel_state = ApplicationState.STATE_ASSIGNED
                panel.state_changed = date.today()
                panel.save()

                send_paw_email('email-panel-assigned.html', {'panel': panel}, subject='PAWCon Panel Application', recipient_list=[panel.email], reply_to=settings.PANEL_EMAIL)

                return HttpResponseRedirect(reverse('console:panels-schedule'))
        
            return self.render_to_response(context)
        
    def _get_slots(self, currentEvent, day):
        schedulingConfigs = SchedulingConfig.objects.filter(event=currentEvent).filter(day_available=day).order_by('day_available__order')

        days = []
        for config in schedulingConfigs:
            slots = [] 
            timeRange = DateTimeRange(config.panels_start, config.panels_end)
            for value in timeRange.range(timedelta(minutes=30)):
                slots.append(value)
            
            days.append({'day': config.day_available, 'slots': slots})
        
        return days
    
class PanelActionUnscheduleRedirect(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        panel = get_object_or_404(Panel, pk=kwargs['panel_id'])
        panel.scheduled_room = None
        panel.scheduled_day = None
        panel.scheduled_time = None
        panel.panel_state = ApplicationState.STATE_ACCEPTED
        panel.state_changed = date.today()
        panel.save()

        view_name = resolve(urlparse(self.request.META.get('HTTP_REFERER')).path).view_name
        if view_name == "console:panel-detail":
            return reverse('console:panel-detail', args=[panel.id])

        return reverse('console:panels-schedule')

class PanelActionCancelRedirect(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        panel = get_object_or_404(Panel, pk=kwargs['panel_id'])
        
        panel.panel_state = ApplicationState.STATE_CANCELED
        panel.state_changed = date.today()
        panel.save()

        view_name = resolve(urlparse(self.request.META.get('HTTP_REFERER')).path).view_name
        if view_name == "console:panel-detail":
            return reverse('console:panel-detail', args=[panel.id])

        return reverse('console:panels-schedule')