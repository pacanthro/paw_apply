from .page_view import PageView
from core.models import get_current_event, ApplicationState
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import RedirectView
from merchants.models import Merchant, MerchantState, Table
from panels.models import Panel
from partyfloor.models import PartyHost
from performers.models import Performer
from volunteers.models import Volunteer
from dancecomp.models import Competitor

decorators = [login_required]

@method_decorator(decorators, name="dispatch")
class ConsoleIndexPageView(PageView):
    template_name = 'console.html'

    def merchant_table_count(self):
        max_merchants = 0
        merchant_count = 0
        event = get_current_event()
        if (event):
            full_table_count = Merchant.objects.filter(event=event).filter(Q(merchant_state=MerchantState.STATE_CONFIRMED) | Q(merchant_state=MerchantState.STATE_ASSIGNED)).filter(table_size=Table.objects.get(key="FULL")).count()
            double_table_count = Merchant.objects.filter(event=event).filter(Q(merchant_state=MerchantState.STATE_CONFIRMED) | Q(merchant_state=MerchantState.STATE_ASSIGNED)).filter(table_size=Table.objects.get(key="DOUB")).count() * 2

            merchant_count = full_table_count + double_table_count

        return merchant_count

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_current_event()
        merchant_count = self.merchant_table_count()
        panel_count = Panel.objects.filter(event=event).count()
        volunteer_count = Volunteer.objects.filter(event=event).count()
        performer_count = Performer.objects.filter(event=event).count()
        host_count = PartyHost.objects.filter(event=event).count()
        competitor_count = Competitor.objects.filter(event=event).count()
        
        context['merchant_count'] = {
            'count': merchant_count,
            'total': event.max_merchants
        }

        context['panel_count'] = panel_count
        context['volunteer_count'] = volunteer_count
        context['performer_count'] = performer_count
        context['host_count'] = host_count
        context['competitor_count'] = competitor_count

        return context