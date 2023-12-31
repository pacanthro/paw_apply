import csv, datetime
from core.models import get_current_event
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from modules.email import send_paw_email

from .models import Event, Merchant, Panel, Volunteer, Performer, PartyHost, Competitor
from merchants.models import Table

def __merchant_table_count():
    max_merchants = 0
    merchant_count = 0
    event = get_current_event()
    if (event):
        full_table_count = Merchant.objects.filter(event=event).filter(payment_confirmed=True).filter(table_size=Table.objects.get(key="FULL")).count()
        double_table_count = Merchant.objects.filter(event=event).filter(payment_confirmed=True).filter(table_size=Table.objects.get(key="DOUB")).count() * 2

        merchant_count = full_table_count + double_table_count

    return merchant_count

# Create your views here.
@login_required
def index(request):
    event = get_current_event()
    merchant_count = __merchant_table_count()
    panel_count = Panel.objects.filter(event=event).count()
    volunteer_count = Volunteer.objects.filter(event=event).count()
    performer_count = Performer.objects.filter(event=event).count()
    host_count = PartyHost.objects.filter(event=event).count()
    competitor_count = Competitor.objects.filter(event=event).count()

    context = {
        'is_console': True,
        'merchant_count': {
            'count': merchant_count,
            'total': event.max_merchants
        },
        'panel_count': panel_count,
        'volunteer_count': volunteer_count,
        'performer_count': performer_count,
        'host_count': host_count,
        'competitor_count': competitor_count
    }

    return render(request, 'console.html', __build_context(request.user, context))

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
