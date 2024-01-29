from .page_view import PageView
from core.models import get_current_event, ApplicationState
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import RedirectView
from modules.email import send_paw_email
from performers.models import Performer

from datetime import date

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