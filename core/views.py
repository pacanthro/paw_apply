from core.models import get_current_event
from django.shortcuts import render

from .models import Event
from panels.models import PanelContent
from partyfloor.models import PartyHostContent
from performers.models import PerformerContent
from volunteers.models import VolunteerContent

# Create your views here.
def index(request):
    event = get_current_event()
    context = {
        'is_home': True,
        'event': event
    }

    context['volunteer_content'] = VolunteerContent.objects.first()

    if event.module_panels_enabled:
        context['panels_content'] = PanelContent.objects.first()

    if event.module_performers_enabled:
        context['performer_content'] = PerformerContent.objects.first()

    if event.module_partyfloor_enabled:
        context['partyhost_content'] = PartyHostContent.objects.first()

    return render(request, 'home.html', context)
