import csv, datetime
from core.models import get_current_event
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from modules.email import send_paw_email

from .models import Competitor

# Create your views here.

def login(request):
    if request.method == 'GET':
        context = {
            'is_console': True,
            'redirect': request.GET.get('next', '/console')
        }
        return render(request, 'console-login.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return HttpResponseRedirect(request.POST['redirect'])
        else:
            context = {
                'is_console': True,
                'redirect': request.POST.get('next', '/console'),
                'error': 'Invalid username or password.'
            }
            return render(request, 'console-login.html', context)

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')

# Competitor Views
@login_required
@permission_required('competitors.view_host')
def competitors(request):
    event = get_current_event()
    competitors = Competitor.objects.filter(event=event)

    context = {
        'competitors': competitors
    }
    return render(request, 'console-competitors-list.html', __build_context(request.user, context))

@login_required
@permission_required('competitors.view_host')
def competitor_detail(request, competitor_id):
    competitor = get_object_or_404(Competitor, pk=competitor_id)
    context = {
        'competitor': competitor
    }
    return render(request, 'console-competitor-detail.html', __build_context(request.user, context))

# API Style Methods
# These are meant to be called by AJAX instead of directly by a user.
#

# Private Functions
def __build_context(user, extras):
    event = get_current_event()
    context = {
        'is_console': True,
        'event': event
    }
    if (user.is_superuser):
        context['is_superuser'] = True
    else:
        context['has_merchant_permission'] = user.has_perm('merchants.view_merchant')
        context['has_panels_permission'] = user.has_perm('panels.view_panel')
        context['has_volunteers_permission'] = user.has_perm('volunteers.view_volunteer')
        context['has_performer_permission'] = user.has_perm('performers.view_performer')
        context['has_host_permission'] = user.has_perm('partyhost.view_partyhost')
        context['has_competitor_permission'] = user.has_perm('competitor.view_competitor')

    context.update(extras)
    return context
