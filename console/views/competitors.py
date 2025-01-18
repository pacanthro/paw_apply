from typing import Any
from console.forms import PanelScheduleRoomDayForm, PanelScheduleSlotForm
from core.models import get_current_event, ApplicationState, EventRoom, RoomType, SchedulingConfig
from dancecomp.models import Competitor
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse, resolve
from django.utils.decorators import method_decorator
from django.views.generic.base import RedirectView
from modules.email import send_paw_email

from .page_view import PageView

from datetime import date

decorators = [login_required, permission_required('competitors.view_competitor')]

@method_decorator(decorators, name="dispatch")
class CompetitorsListPageView(PageView):
    template_name="console-competitors-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_current_event()
        new_competitors = Competitor.objects.filter(event=event).filter(competitor_state=ApplicationState.STATE_NEW)
        accepted_competitors = Competitor.objects.filter(event=event).filter(competitor_state=ApplicationState.STATE_ACCEPTED)
        declined_competitors = Competitor.objects.filter(event=event).filter(competitor_state=ApplicationState.STATE_DENIED)

        context['new_competitors'] = new_competitors
        context['accepted_competitors'] = accepted_competitors
        context['declined_competitors'] = declined_competitors

        return context

@method_decorator(decorators, name="dispatch")
class CompetitorDetailPageView(PageView):
    template_name="console-competitor-detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        competitor = get_object_or_404(Competitor, pk=kwargs['competitor_id'])

        context['competitor'] = competitor

        return context

@method_decorator(decorators, name="dispatch")
class CompetitorActionAcceptRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:competitor-detail'

    def get_redirect_url(self, *args, **kwargs):
        competitor = get_object_or_404(Competitor, pk=kwargs['competitor_id'])
        competitor.competitor_state = ApplicationState.STATE_ACCEPTED
        competitor.state_changed = date.today()
        competitor.save()

        send_paw_email('email-dance-accepted.html', {'competitor':competitor}, subject='PAWCon Dance Competitor Accepted', recipient_list=[competitor.email], reply_to=settings.DANCE_EMAIL)

        return super().get_redirect_url(*args, **kwargs)

@method_decorator(decorators, name="dispatch")
class CompetitorActionDeclineRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:competitor-detail'

    def get_redirect_url(self, *args, **kwargs):
        competitor = get_object_or_404(Competitor, pk=kwargs['competitor_id'])
        competitor.competitor_state = ApplicationState.STATE_DENIED
        competitor.state_changed = date.today()
        competitor.save()

        send_paw_email('email-dance-declined.html', {'competitor':competitor}, subject='PAWCon Dance Competitor Declined', recipient_list=[competitor.email], reply_to=settings.DANCE_EMAIL)

        return super().get_redirect_url(*args, **kwargs)

@method_decorator(decorators, name="dispatch")
class CompetitorActionDeleteRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:competitors'

    def get_redirect_url(self, *args, **kwargs):
        competitor = get_object_or_404(Competitor, pk=kwargs['competitor_id'])
        competitor.competitor_state = ApplicationState.STATE_DELETED
        competitor.state_changed = date.today()
        competitor.save()

        return reverse(self.pattern_name)