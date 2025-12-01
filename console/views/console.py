from .page_view import PageView
from console.forms import LoginForm
from core.models import get_current_event, ApplicationState
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.base import RedirectView
from merchants.models import Merchant, MerchantState, Table
from panels.models import Panel
from partyfloor.models import PartyHost
from performers.models import Performer
from volunteers.models import Volunteer
from dancecomp.models import Competitor

decorators = [login_required]

class ConsoleLoginPageView(PageView):
    template_name = 'console-login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = LoginForm()

        context['redirect'] = self.request.GET.get('next', '/console')
        context['form'] = form

        return context
    
    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = LoginForm(data=request.POST)

        context['form'] = form

        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return HttpResponseRedirect(request.GET.get('next', '/console'))

        return self.render_to_response(context)     

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'console-password-reset.html'
    email_template_name = 'console-email-reset-password.html'
    html_email_template_name = 'console-email-reset-password.html'
    subject_template_name = 'console-email-reset-password.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('console:index')
    
    def get_extra_context(*args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = get_current_event()

        return context

class ResetPasswordConfirmView(PasswordResetConfirmView):
    template_name = 'console-password-reset-confirm.html'
    success_url = reverse_lazy('console:forgot-password-complete')

    def get_extra_context(*args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = get_current_event()

        return context
    

class ResetPasswordCompleteView(PasswordResetCompleteView):
    template_name = 'console-password-reset-complete.html'

    def get_extra_context(*args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = get_current_event()

        return context

class ConsoleLogoutRedirect(View):
    def get(self, request, *args, **kwargs):
        auth_logout(self.request)

        return HttpResponseRedirect(reverse('core:index'))



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
        merchants_applied = Merchant.objects.filter(event=event).exclude(merchant_state=MerchantState.STATE_DELETED).count()
        panel_count = Panel.objects.filter(event=event).count()
        volunteer_count = Volunteer.objects.filter(event=event).exclude(volunteer_state=ApplicationState.STATE_DELETED).count()
        performer_count = Performer.objects.filter(event=event).exclude(performer_state=ApplicationState.STATE_DELETED).count()
        host_count = PartyHost.objects.filter(event=event).exclude(host_state=ApplicationState.STATE_DELETED).count()
        competitor_count = Competitor.objects.filter(event=event).exclude(competitor_state=ApplicationState.STATE_DELETED).count()
        
        context['merchants'] = {
            'applied': merchants_applied,
            'tables_count': merchant_count,
            'tables_total': event.max_merchants
        }

        context['panel_count'] = panel_count
        context['volunteer_count'] = volunteer_count
        context['performer_count'] = performer_count
        context['host_count'] = host_count
        context['competitor_count'] = competitor_count

        return context