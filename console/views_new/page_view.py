from core.models import get_current_event
from django.views.generic.base import TemplateView

class PageView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        event = get_current_event()
        context['is_console'] = True
        context['event'] = event

        if (user.is_superuser):
            context['is_superuser'] = True
        else:
            context['has_merchant_permission'] = user.has_perm('merchants.view_merchant')
            context['has_panels_permission'] = user.has_perm('panels.view_panel')
            context['has_volunteers_permission'] = user.has_perm('volunteers.view_volunteer')
            context['has_performer_permission'] = user.has_perm('performers.view_performer')
            context['has_partyhost_permission'] = user.has_perm('partyfloor.view_partyhost')
            context['has_competitor_permission'] = user.has_perm('competitor.view_competitor')

        return context