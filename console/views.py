import datetime
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from modules.email import send_paw_email

from .models import Event, Merchant

# Create your views here.
@login_required
def index(request):
    return render(request, 'console.html', __build_context(request.user, {'is_console': True}))

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

@login_required
@permission_required('merchants.view_merchant')
def merchants(request):
    event = Event.objects.filter(event_end__gte=datetime.date.today())[:1].get()
    merchants = Merchant.objects.filter(event=event).filter(payment_requested__isnull = True)
    processed = Merchant.objects.filter(event=event).filter(payment_requested = True)
    context = {
        'merchants': merchants,
        'processed': processed
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

@login_required
@permission_required('merchants.view_merchant')
def merchant_payment(request, merchant_id):
    merchant = get_object_or_404(Merchant, pk=merchant_id)
    merchant.payment_requested = True
    merchant.email_sent = datetime.date.today()
    merchant.save()
    send_paw_email('email-merchant-payment.html', {'merchant': merchant}, subject='PAWCon Merchant Cart Ready', recipient_list=[merchant.email], reply_to='merchant@pacanthro.org')
    data = {
        'status': 'Success'
    }
    return JsonResponse(data)

# Private Functions
def __build_context(user, extras):
    context = {
        'is_console': True,
        'user': user,
    }
    if (user.is_superuser):
        context['is_superuser'] = True
    else:
        context['has_merchant_permission'] = user.has_perm('merchants.view_merchant')
        context['has_panels_permission'] = user.has_perm('panels.view_panel')
        context['has_volunteers_permission'] = user.has_perm('volunteers.view_volunteer')

    context.update(extras)
    return context
