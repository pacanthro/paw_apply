from core.models import get_current_event
from django.shortcuts import render

from .models import Event
from performers.models import PerformerContent

# Create your views here.
def index(request):
    event = get_current_event()
    context = {
        'is_home': True,
        'event': event
    }

    if event.module_performers_enabled:
        context['performer_content'] = PerformerContent.objects.first()

    return render(request, 'home.html', context)
