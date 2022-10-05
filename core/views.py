from core.models import get_current_event
from django.shortcuts import render

from .models import Event

# Create your views here.
def index(request):
    event = get_current_event()
    context = {
        'is_home': True,
        'event': event
    }
    return render(request, 'home.html', context)
