from typing import Any
from .page_view import PageView
from console.forms import HostAssignRoomForm, PartyHostUpdateContentForm
from core.models import get_current_event, ApplicationState
from datetime import date
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import RedirectView
from modules.email import send_paw_email, send_paw_email_new
from partyfloor.models import PartyHost, PartyHostContent

decorators = [login_required, permission_required('partyfloor.view_partyhost')]

@method_decorator(decorators, name="dispatch")
class PartyHostListPageViewView(PageView):
    template_name = 'console-hosts-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_current_event()
        new_hosts = PartyHost.objects.filter(event=event).filter(host_state=ApplicationState.STATE_NEW)
        accepted_hosts = PartyHost.objects.filter(event=event).filter(host_state=ApplicationState.STATE_ACCEPTED)
        waitlisted_hosts = PartyHost.objects.filter(event=event).filter(host_state=ApplicationState.STATE_WAITLIST)
        assigned_hosts = PartyHost.objects.filter(event=event).filter(host_state=ApplicationState.STATE_ASSIGNED)
        declined_hosts = PartyHost.objects.filter(event=event).filter(host_state=ApplicationState.STATE_DENIED)

        context['new_hosts'] = new_hosts
        context['accepted_hosts'] = accepted_hosts
        context['waitlisted_hosts'] = waitlisted_hosts
        context['assigned_hosts'] = assigned_hosts
        context['declined_hosts'] = declined_hosts

        return context

@method_decorator(decorators, name="dispatch")
class PartyHostDetailPageView(PageView):
    template_name = 'console-host-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host = get_object_or_404(PartyHost, pk=kwargs['host_id'])

        context['host'] = host
        
        return context

@method_decorator(decorators, name="dispatch")
class PartyHostActionDeclineRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:host-detail'

    def get_redirect_url(self, *args: Any, **kwargs: Any):
        host = get_object_or_404(PartyHost, pk=kwargs['host_id'])
        host.host_state = ApplicationState.STATE_DENIED
        host.state_changed = date.today()
        host.save()

        content = PartyHostContent.objects.first()

        send_paw_email_new(content.email_declined, {'host':host}, subject='PAWCon Party Floor Submission', recipient_list=[host.email], reply_to=settings.HOTEL_EMAIL)

        return reverse('console:hosts')
    
@method_decorator(decorators, name="dispatch")
class PartyHostActionAcceptRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:host-detail'

    def get_redirect_url(self, *args: Any, **kwargs: Any):
        host = get_object_or_404(PartyHost, pk=kwargs['host_id'])
        host.host_state = ApplicationState.STATE_ACCEPTED
        host.state_changed = date.today()
        host.save()

        content = PartyHostContent.objects.first()

        send_paw_email_new(content.email_accepted, {'host':host}, subject='PAWCon Party Floor Submission', recipient_list=[host.email], reply_to=settings.HOTEL_EMAIL)

        return super().get_redirect_url(*args, **kwargs)
    
@method_decorator(decorators, name="dispatch")
class PartyHostActionWaitlistRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:host-detail'

    def get_redirect_url(self, *args: Any, **kwargs: Any):
        host = get_object_or_404(PartyHost, pk=kwargs['host_id'])
        host.host_state = ApplicationState.STATE_WAITLIST
        host.state_changed = date.today()
        host.save()

        content = PartyHostContent.objects.first()

        send_paw_email_new(content.email_waitlisted, {'host':host}, subject='PAWCon Party Floor Submission', recipient_list=[host.email], reply_to=settings.HOTEL_EMAIL)

        return super().get_redirect_url(*args, **kwargs)

@method_decorator(decorators, name="dispatch")
class PartyHostActionDeleteRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:host-detail'

    def get_redirect_url(self, *args, **kwargs):
        host = get_object_or_404(PartyHost, pk=kwargs['host_id'])
        host.host_state = ApplicationState.STATE_DELETED
        host.state_changed = date.today()
        host.save()

        return reverse('console:hosts')

@method_decorator(decorators, name="dispatch")
class PartyHostActionAssignPageView(PageView):
    template_name = 'console-host-assign.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host = get_object_or_404(PartyHost, pk=kwargs['host_id'])
        form = HostAssignRoomForm(instance=host)

        context['host'] = host
        context['form'] = form
        
        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = HostAssignRoomForm(request.POST, instance=context['host'])
        
        context['form'] = form

        if form.is_valid():
            host = form.save(commit=False)
            host.host_state = ApplicationState.STATE_ASSIGNED
            host.state_changed = date.today()
            host.save()

            content = PartyHostContent.objects.first()

            send_paw_email_new(content.email_assigned, {'host':host}, subject='PAWCon Party Floor Submission', recipient_list=[host.email], reply_to=settings.HOTEL_EMAIL)

            return HttpResponseRedirect(reverse('console:host-detail', args=[kwargs['host_id']]))
        
        return self.render_to_response(context)

@method_decorator(decorators, name="dispatch")
class PartyHostUpdateContentPageView(PageView):
    template_name = 'console-host-content.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content = PartyHostContent.objects.first()
        form = PartyHostUpdateContentForm(instance=content)

        context['content'] = content
        context['form'] = form
        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = PartyHostUpdateContentForm(request.POST, instance=context['content'])
        
        context['form'] = form

        if form.is_valid():
            host = form.save()
        
        return self.render_to_response(context)