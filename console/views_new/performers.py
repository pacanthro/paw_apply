from .page_view import PageView
from console.forms import PerformerScheduleDayForm, PerformerScheduleSlotForm
from core.models import get_current_event, ApplicationState, DaysAvailable, SchedulingConfig
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic.base import RedirectView
from modules.email import send_paw_email
from performers.models import Performer

from django.conf import settings
import django.utils.timezone

from datetime import date, timedelta
from datetimerange import DateTimeRange
import logging

decorators = [login_required, permission_required('performers.view_performer')]

@method_decorator(decorators, name="dispatch")
class PerformersListPageView(PageView):
    template_name = 'console-performers-list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_current_event()
        performers = Performer.objects.filter(event=event).filter(performer_state=ApplicationState.STATE_NEW)
        performers_accepted = Performer.objects.filter(event=event).filter(performer_state=ApplicationState.STATE_ACCEPTED)
        performers_assigned = Performer.objects.filter(event=event).filter(performer_state=ApplicationState.STATE_ASSIGNED)
        performers_waitlisted = Performer.objects.filter(event=event).filter(performer_state=ApplicationState.STATE_WAITLIST)
        performers_declined = Performer.objects.filter(event=event).filter(performer_state=ApplicationState.STATE_DENIED)
    
        context['performers'] = performers
        context['performers_accepted'] = performers_accepted
        context['performers_assigned'] = performers_assigned
        context['performers_waitlisted'] = performers_waitlisted
        context['performers_declined'] = performers_declined
    
        return context

@method_decorator(decorators, name="dispatch")
class PerformerDetailPageView(PageView):
    template_name = 'console-performer-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        performer = get_object_or_404(Performer, pk=kwargs['performer_id'])

        context['performer'] = performer

        return context
    
@method_decorator(decorators, name="dispatch")
class PerformerActionAcceptRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:performer-detail'

    def get_redirect_url(self, *args, **kwargs):
        performer = get_object_or_404(Performer, pk=kwargs['performer_id'])
        performer.performer_state = ApplicationState.STATE_ACCEPTED
        performer.state_changed = date.today()
        performer.save()

        send_paw_email('email-performers-accepted.html', {'performer': performer}, subject='PAWCon DJ Application', recipient_list=[performer.email], reply_to=settings.PERFORMERS_EMAIL)

        return super().get_redirect_url(*args, **kwargs)

@method_decorator(decorators, name="dispatch")
class PerformerActionWaitlistRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:performer-detail'

    def get_redirect_url(self, *args, **kwargs):
        performer = get_object_or_404(Performer, pk=kwargs['performer_id'])
        performer.performer_state = ApplicationState.STATE_WAITLIST
        performer.state_changed = date.today()
        performer.save()

        send_paw_email('email-performers-waitlisted.html', {'performer': performer}, subject='PAWCon DJ Application', recipient_list=[performer.email], reply_to=settings.PERFORMERS_EMAIL)

        return super().get_redirect_url(*args, **kwargs)

@method_decorator(decorators, name="dispatch")
class PerformerActionDeclineRedirect(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        performer = get_object_or_404(Performer, pk=kwargs['performer_id'])
        performer.performer_state = ApplicationState.STATE_DENIED
        performer.state_changed = date.today()
        performer.save()

        send_paw_email('email-performers-declined.html', {'performer': performer}, subject='PAWCon DJ Application', recipient_list=[performer.email], reply_to=settings.PERFORMERS_EMAIL)

        return reverse('console:performers')

@method_decorator(decorators, name="dispatch")
class PerformerActionDeleteRedirect(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        performer = get_object_or_404(Performer, pk=kwargs['performer_id'])
        performer.performer_state = ApplicationState.STATE_DELETED
        performer.state_changed = date.today()
        performer.save()

        return reverse('console:performers')

@method_decorator(decorators, name="dispatch")
class PerformersSchedulePageView(PageView):
    template_name = 'console-performers-schedule.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        currentEvent = get_current_event()
        
        performers = Performer.objects.filter(event=currentEvent).filter(performer_state=ApplicationState.STATE_ACCEPTED)
        schedulingConfigs = SchedulingConfig.objects.filter(event=currentEvent).order_by('day_available__order')

        days = []
        for config in schedulingConfigs:
            slots = [] 
            timeRange = DateTimeRange(config.performers_start, config.performers_end)
            for value in timeRange.range(timedelta(hours=1)):
                slots.append(value)
            
            filledSlots = Performer.objects.filter(event=currentEvent).filter(performer_state=ApplicationState.STATE_ASSIGNED)
            
            days.append({'day': config.day_available, 'slots': slots, 'filledSlots': filledSlots})

        forms = []
        for performer in performers:
            form = PerformerScheduleDayForm(instance=performer)

            forms.append(form)

        context['performers'] = forms
        context['items'] = days
            
        return context

@method_decorator(decorators, name="dispatch")
class PerformerActionAssignPageView(PageView):
    template_name = 'console-performers-assign.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        currentEvent = get_current_event()
        performer = get_object_or_404(Performer, pk=kwargs['performer_id'])
        form = PerformerScheduleDayForm(instance=performer)

        context['performer'] = performer
        context['form'] = form

        return context
    
    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        currentEvent = get_current_event()
        

        if context['performer'].scheduled_day is None:
            form = form = PerformerScheduleDayForm(request.POST, instance=context['performer'])
            
            context['form'] = form

            if form.is_valid():
                performer = form.save()
                context['performer'] = performer

                days = self._get_slots(currentEvent, performer.scheduled_day)
                form = PerformerScheduleSlotForm(instance=context['performer'], options=days[0]['slots'])
            
                context['form'] = form
                return self.render_to_response(context)

            return self.render_to_response(context)
        else:
            days = self._get_slots(currentEvent, context['performer'].scheduled_day)
            form = PerformerScheduleSlotForm(request.POST, instance=context['performer'], options=days[0]['slots'])
            
            context['form'] = form

            if form.is_valid():
                performer = form.save(commit=False)
                performer.performer_state = ApplicationState.STATE_ASSIGNED
                performer.state_changed = date.today()
                performer.save()

                send_paw_email('email-performers-assigned.html', {'performer': performer}, subject='PAWCon DJ Application', recipient_list=[performer.email], reply_to=settings.PERFORMERS_EMAIL)

                return HttpResponseRedirect(reverse('console:performer-schedule'))
        
            return self.render_to_response(context)
    
    def _get_slots(self, currentEvent, day):
        schedulingConfigs = SchedulingConfig.objects.filter(event=currentEvent).filter(day_available=day).order_by('day_available__order')

        days = []
        for config in schedulingConfigs:
            slots = [] 
            timeRange = DateTimeRange(config.performers_start, config.performers_end)
            for value in timeRange.range(timedelta(hours=1)):
                slots.append(value)
            
            days.append({'day': config.day_available, 'slots': slots})
        
        return days

class PerformerActionUnscheduleRedirect(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        performer = get_object_or_404(Performer, pk=kwargs['performer_id'])
        performer.scheduled_day = None
        performer.scheduled_time = None
        performer.performer_state = ApplicationState.STATE_ACCEPTED
        performer.state_changed = date.today()
        performer.save()

        return reverse('console:performer-schedule')
