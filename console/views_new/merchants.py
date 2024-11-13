import csv
from typing import Any

from .page_view import PageView
from console.forms import MerchantAssignTableForm
from core.models import get_current_event
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import BadRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.base import RedirectView
from merchants.models import Merchant, MerchantState
from modules.email import send_paw_email

from datetime import date

decorators = [login_required, permission_required('merchants.view_merchant')]

@method_decorator(decorators, name="dispatch")
class MerchantsListPageView(PageView):
    template_name = 'console-merchants-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_current_event()
        merchants = Merchant.objects.filter(event=event).filter(merchant_state=MerchantState.STATE_NEW)
        accepted = Merchant.objects.filter(event=event).filter(merchant_state=MerchantState.STATE_ACCEPTED)
        waitlisted = Merchant.objects.filter(event=event).filter(merchant_state=MerchantState.STATE_WAITLISTED)
        processed = Merchant.objects.filter(event=event).filter(merchant_state=MerchantState.STATE_PAYMENT)
        confirmed = Merchant.objects.filter(event=event).filter(merchant_state=MerchantState.STATE_CONFIRMED)
        assigned = Merchant.objects.filter(event=event).filter(merchant_state=MerchantState.STATE_ASSIGNED)
        denied = Merchant.objects.filter(event=event).filter(merchant_state=MerchantState.STATE_DENIED)
        
        context['merchants'] = merchants
        context['accepted'] = accepted
        context['waitlisted'] = waitlisted
        context['processed'] = processed
        context['confirmed'] = confirmed
        context['assigned'] = assigned
        context['denied'] = denied

        return context

@method_decorator(decorators, name="dispatch")
class MerchantCSVDownloadView(View):
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="merchants.csv"'
        event = get_current_event()
        merchants = Merchant.objects.filter(event=event).exclude(merchant_state=MerchantState.STATE_DELETED)

        writer = csv.writer(response)

        for merchant in merchants:
            writer.writerow([merchant.business_name, merchant.email, merchant.legal_name, merchant.fan_name])

        return response

@method_decorator(decorators, name="dispatch")
class MerchantDetailsPageView(PageView):
    template_name = 'console-merchants-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        merchant = get_object_or_404(Merchant, pk=kwargs['merchant_id'])

        context['merchant'] = merchant

        return context

@method_decorator(decorators, name="dispatch")
class MerchantActionAcceptedRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:merchant-detail'

    def get_redirect_url(self, *args, **kwargs):
        merchant = get_object_or_404(Merchant, pk=kwargs['merchant_id'])
        merchant.state_changed = date.today()

        if merchant.merchant_state == MerchantState.STATE_NEW or merchant.merchant_state == MerchantState.STATE_WAITLISTED:
            merchant.merchant_state = MerchantState.STATE_ACCEPTED
            merchant.save()
            send_paw_email('email-merchant-accepted.html', {'merchant': merchant}, subject='PAWCon Merchant Cart Ready', recipient_list=[merchant.email], reply_to=settings.MERCHANT_EMAIL)
        
        return super().get_redirect_url(*args, **kwargs)

@method_decorator(decorators, name="dispatch")
class MerchantActionRequestPaymentRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:merchant-detail'

    def get_redirect_url(self, *args, **kwargs):
        merchant = get_object_or_404(Merchant, pk=kwargs['merchant_id'])
        merchant.state_changed = date.today()

        if merchant.merchant_state == MerchantState.STATE_ACCEPTED or merchant.merchant_state == MerchantState.STATE_WAITLISTED:
            merchant.merchant_state = MerchantState.STATE_PAYMENT
            merchant.save()
            send_paw_email('email-merchant-payment.html', {'merchant': merchant}, subject='PAWCon Merchant Cart Ready', recipient_list=[merchant.email], reply_to=settings.MERCHANT_EMAIL)
        elif merchant.merchant_state == MerchantState.STATE_PAYMENT:
            merchant.save()
            send_paw_email('email-merchant-payment-remind.html', {'merchant': merchant}, subject='PAWCon Merchant Cart Ready', recipient_list=[merchant.email], reply_to=settings.MERCHANT_EMAIL)
        else:
            raise BadRequest("Invalid Merchant State for requesting payment.")
        
        return super().get_redirect_url(*args, **kwargs)
    
@method_decorator(decorators, name="dispatch")
class MerchantActionPaymentConfirmedRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:merchant-detail'

    def get_redirect_url(self, *args, **kwargs):
        merchant = get_object_or_404(Merchant, pk=kwargs['merchant_id'])

        if merchant.merchant_state == MerchantState.STATE_PAYMENT:
            merchant.merchant_state = MerchantState.STATE_CONFIRMED
            merchant.state_changed = date.today()
            merchant.save()

            send_paw_email('email-merchant-payment-confirmed.html', {'merchant': merchant}, subject='PAWCon - Welcome to the shopping District', recipient_list=[merchant.email], reply_to=settings.MERCHANT_EMAIL)
        else:
            raise BadRequest("Invalid Merchant State for Confirming Payment.")

        return super().get_redirect_url(*args, **kwargs)

@method_decorator(decorators, name="dispatch")
class MerchantActionRegistrationReminderRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:merchant-detail'

    def get_redirect_url(self, *args, **kwargs):
        merchant = get_object_or_404(Merchant, pk=kwargs['merchant_id'])
        send_paw_email('email-merchant-accepted.html', {'merchant': merchant}, subject='PAWCon Merchant Application', recipient_list=[merchant.email], reply_to=settings.MERCHANT_EMAIL)

        return super().get_redirect_url(*args, **kwargs)

@method_decorator(decorators, name="dispatch")
class MerchantActionWaitlistRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:merchant-detail'

    def get_redirect_url(self, *args, **kwargs):
        merchant = get_object_or_404(Merchant, pk=kwargs['merchant_id'])

        if merchant.merchant_state != MerchantState.STATE_WAITLISTED:
            merchant.merchant_state = MerchantState.STATE_WAITLISTED
            merchant.state_changed = date.today()
            merchant.save()

            send_paw_email('email-merchant-waitlist.html', {'merchant': merchant}, subject='PAWCon Merchant Waitlist', recipient_list=[merchant.email], reply_to=settings.MERCHANT_EMAIL)
        
        return super().get_redirect_url(*args, **kwargs)
    

@method_decorator(decorators, name="dispatch")
class MerchantActionDeleteRedirect(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        merchant = get_object_or_404(Merchant, pk=kwargs['merchant_id'])
        merchant.merchant_state = MerchantState.STATE_DELETED
        merchant.state_changed = date.today()
        merchant.save()
        
        return reverse('console:merchants')

@method_decorator(decorators, name="dispatch")
class MerchantActionAssignPageView(PageView):
    template_name = 'console-merchants-assign.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        merchant = get_object_or_404(Merchant, pk=kwargs['merchant_id'])
        form = MerchantAssignTableForm(instance=merchant)

        context['merchant'] = merchant
        context['form'] = form

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = MerchantAssignTableForm(request.POST, instance=context['merchant'])

        context['form'] = form

        if form.is_valid():
            merchant = form.save(commit=False)
            merchant.merchant_state = MerchantState.STATE_ASSIGNED
            merchant.state_changed = date.today()
            merchant.save();

            send_paw_email('email-merchant-table-assigned.html', {'merchant': merchant}, subject='PAWCon Merchant Table Assigned', recipient_list=[merchant.email], reply_to=settings.MERCHANT_EMAIL)

            return HttpResponseRedirect(reverse('console:merchant-detail', args=[merchant.id]))
        
        return self.render_to_response(context)
        