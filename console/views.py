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

# Create your views here.
@login_required
def index(request):
    event = get_current_event()
    merchant_count = Merchant.objects.filter(event=event).count()
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

# Merchant Views
# All of the Merchant Tools
#
@login_required
@permission_required('merchants.view_merchant')
def merchants(request):
    event = get_current_event()
    merchants = Merchant.objects.filter(event=event).filter(payment_requested__isnull=True)
    processed = Merchant.objects.filter(event=event).filter(payment_requested=True).filter(payment_confirmed__isnull=True)
    confirmed = Merchant.objects.filter(event=event).filter(payment_confirmed=True)
    context = {
        'merchants': merchants,
        'processed': processed,
        'confirmed': confirmed,
    }
    return render(request, 'console-merchants-list.html', __build_context(request.user, context))

@login_required
@permission_required('merchants.view_merchant')
def merchant_detail(request, merchant_id):
    merchant = get_object_or_404(Merchant, pk=merchant_id)
    context = {
        'is_console': True,
        'merchant': merchant
    }
    return render(request, 'console-merchants-detail.html', __build_context(request.user, context))

# Panel Views
# All of the Panel Tools
#
@login_required
@permission_required('panels.view_panel')
def panels(request):
    event = get_current_event()
    panels = Panel.objects.filter(event=event)
    context = {
        'panels': panels
    }
    return render(request, 'console-panels-list.html', __build_context(request.user, context))

@login_required
@permission_required('panels.view_panel')
def panel_detail(request, panel_id):
    panel = get_object_or_404(Panel, pk=panel_id)
    context = {
        'panel': panel
    }
    return render(request, 'console-panels-detail.html', __build_context(request.user, context))

# Volunteer Views
# All of the volunteer tools
#
@login_required
@permission_required('volunteers.view_volunteer')
def volunteers(request):
    event = get_current_event()
    volunteers = Volunteer.objects.filter(event=event)
    context = {
        'volunteers': volunteers
    }
    return render(request, 'console-volunteers-list.html', __build_context(request.user, context))

@login_required
@permission_required('volunteers.view_volunteer')
def volunteer_detail(request, volunteer_id):
    volunteer = get_object_or_404(Volunteer, pk=volunteer_id)
    context = {
        'volunteer': volunteer
    }
    return render(request, 'console-volunteers-detail.html', __build_context(request.user, context))

# Performer Views
@login_required
@permission_required('performer.view_performer')
def performers(request):
    event = get_current_event()
    performers = Performer.objects.filter(event=event)
    context = {
        'performers': performers
    }
    return render(request, 'console-performers-list.html', __build_context(request.user, context))

@login_required
@permission_required('performer.view_performer')
def performer_detail(request, performer_id):
    performer = get_object_or_404(Performer, pk=performer_id)
    context = {
        'performer': performer
    }
    return render(request, 'console-performer-detail.html', __build_context(request.user, context))

# Host Views
@login_required
@permission_required('host.view_host')
def hosts(request):
    event = get_current_event()
    hosts = PartyHost.objects.filter(event=event)
    context = {
        'hosts': hosts
    }
    return render(request, 'console-hosts-list.html', __build_context(request.user, context))

@login_required
@permission_required('host.view_host')
def host_detail(request, host_id):
    host = get_object_or_404(PartyHost, pk=host_id)
    context = {
        'host': host
    }
    return render(request, 'console-host-detail.html', __build_context(request.user, context))

@login_required
@permission_required('host.view_host')
def host_assign(request, host_id):
    host = get_object_or_404(PartyHost, pk=host_id)
    context = {
        'host': host
    }
    return render(request, 'console-host-assign.html', __build_context(request.user, context))

@login_required
@permission_required('host.view_host')
def host_confirm(request, host_id):
    host = get_object_or_404(PartyHost, pk=host_id)
    host.room_number = request.POST['room_number']
    host.room_assigned = True
    host.confirmation_sent = datetime.date.today()
    host.save()

    send_paw_email('email-party-assigned.html', {'host': host}, subject='PAWCon Party Floor Confirmation', recipient_list=[host.email], reply_to=settings.HOTEL_EMAIL)

    return HttpResponseRedirect(reverse('console:host-detail', args=[host_id]))



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
@permission_required('host.view_host')
def competitor_detail(request, competitor_id):
    competitor = get_object_or_404(Competitor, pk=competitor_id)
    context = {
        'competitor': competitor
    }
    return render(request, 'console-competitor-detail.html', __build_context(request.user, context))

# API Style Methods
# These are meant to be called by AJAX instead of directly by a user.
#

@login_required
@permission_required('merchants.view_merchant')
def merchant_payment(request, merchant_id):
    merchant = get_object_or_404(Merchant, pk=merchant_id)
    merchant.email_sent = datetime.date.today()
    if merchant.payment_requested is None:
        merchant.payment_requested = True
        merchant.save()
        send_paw_email('email-merchant-payment.html', {'merchant': merchant}, subject='PAWCon Merchant Cart Ready', recipient_list=[merchant.email], reply_to=settings.MERCHANT_EMAIL)
    else:
        merchant.save()
        send_paw_email('email-merchant-payment-remind.html', {'merchant': merchant}, subject='PAWCon Merchant Cart Ready', recipient_list=[merchant.email], reply_to=settings.MERCHANT_EMAIL)

    data = {
        'status': 'Success'
    }
    return JsonResponse(data)

@login_required
@permission_required('merchants.view_merchant')
def merchant_confirmed(request, merchant_id):
    merchant = get_object_or_404(Merchant, pk=merchant_id)
    if merchant.payment_requested is True:
        merchant.payment_confirmed = True
        merchant.confirmation_sent = datetime.date.today()
        merchant.save()
        send_paw_email('email-merchant-payment-confirmed.html', {'merchant': merchant}, subject='PAWCon - Welcome to the shopping District', recipient_list=[merchant.email], reply_to=settings.MERCHANT_EMAIL)
        data = {
            'status': 'Success'
        }
        return JsonResponse(data)
    else:
        return HttpResponseBadRequest()

@login_required
@permission_required('merchants.view_merchant')
def merchant_reg_reminder(request, merchant_id):
    merchant = get_object_or_404(Merchant, pk=merchant_id)
    send_paw_email('email-merchant-confirm.html', {'merchant': merchant}, subject='PAWCon Merchant Application', recipient_list=[merchant.email], reply_to=settings.MERCHANT_EMAIL)

    return JsonResponse({'status': 'success'})

@login_required
@permission_required('merchants.view_merchant')
def merchant_download_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="merchants.csv"'
    event = get_current_event()
    merchants = Merchant.objects.filter(event=event)

    writer = csv.writer(response)

    for merchant in merchants:
        writer.writerow([merchant.business_name, merchant.email, merchant.legal_name, merchant.fan_name])

    return response

@login_required
@permission_required('host.view_host')
def host_waitlist(request, host_id):
    host = get_object_or_404(PartyHost, pk=host_id)
    host.waitlist_sent = datetime.date.today()
    host.save()
    context = {
        'host': host
    }
    send_paw_email('email-party-waitlist.html', {'host': host}, subject='PAWCon Party Floor Waitlist', recipient_list=[host.email], reply_to=settings.HOTEL_EMAIL)
    return JsonResponse({'status': 'success'})

# Private Functions
def __build_context(user, extras):
    context = {
        'is_console': True,
    }
    if (user.is_superuser):
        context['is_superuser'] = True
    else:
        context['has_merchant_permission'] = user.has_perm('merchants.view_merchant')
        context['has_panels_permission'] = user.has_perm('panels.view_panel')
        context['has_volunteers_permission'] = user.has_perm('volunteers.view_volunteer')
        context['has_performer_permission'] = user.has_perm('performer.view_performer')
        context['has_host_permission'] = user.has_perm('partyhost.view_partyhost')
        context['has_competitor_permission'] = user.has_perm('competitor.view_competitor')

    context.update(extras)
    return context
