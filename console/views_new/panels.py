from .page_view import PageView
from core.models import get_current_event, ApplicationState
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import RedirectView
from panels.models import Panel

from django.utils import timezone

decorators = [login_required, permission_required('panels.view_panel')]

@method_decorator(decorators, name="dispatch")
class PanelsListPageView(PageView):
    template_name="console-panels-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_current_event()
        panels = Panel.objects.filter(event=event).filter(panel_state=ApplicationState.STATE_NEW)
        panels_accepted = Panel.objects.filter(event=event).filter(panel_state=ApplicationState.STATE_ACCEPTED)
        panels_scheduled = Panel.objects.filter(event=event).filter(panel_state=ApplicationState.STATE_ASSIGNED)
        panels_waitlisted = Panel.objects.filter(event=event).filter(panel_state=ApplicationState.STATE_WAITLIST)
        panels_denied = Panel.objects.filter(event=event).filter(panel_state=ApplicationState.STATE_DENIED)

        context['panels'] = panels
        context['panels_accepted'] = panels_accepted
        context['panels_scheduled'] = panels_scheduled
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
        panel.state_changed = timezone.now()
        panel.save()
        return super().get_redirect_url(*args, **kwargs)
    
@method_decorator(decorators, name="dispatch")
class PanelActionWaitlistRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:panel-detail'

    def get_redirect_url(self, *args, **kwargs):
        panel = get_object_or_404(Panel, pk=kwargs['panel_id'])
        panel.panel_state = ApplicationState.STATE_WAITLIST
        panel.state_changed = timezone.now()
        panel.save()
        return super().get_redirect_url(*args, **kwargs)

@method_decorator(decorators, name="dispatch")
class PanelActionDenyRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:panel-detail'

    def get_redirect_url(self, *args, **kwargs):
        panel = get_object_or_404(Panel, pk=kwargs['panel_id'])
        panel.panel_state = ApplicationState.STATE_DENIED
        panel.state_changed = timezone.now()
        panel.save()
        return super().get_redirect_url(*args, **kwargs)

@method_decorator(decorators, name="dispatch")
class PanelActionDeleteRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:panels'

    def get_redirect_url(self, *args, **kwargs):
        panel = get_object_or_404(Panel, pk=kwargs['panel_id'])
        panel.panel_state = ApplicationState.STATE_DELETED
        panel.state_changed = timezone.now()
        panel.save()
        return reverse('console:panels')