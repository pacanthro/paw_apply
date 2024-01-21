import csv

from .page_view import PageView
from core.models import get_current_event, ApplicationState
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.base import RedirectView
from modules.email import send_paw_email
from volunteers.models import Volunteer

from datetime import date

decorators = [login_required, permission_required('volunteers.view_volunteer')]

@method_decorator(decorators, name="dispatch")
class VolunteerListPageView(PageView):
    template_name = 'console-volunteers-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_current_event()
        volunteers = Volunteer.objects.filter(event=event).filter(volunteer_state=ApplicationState.STATE_NEW)
        volunteers_accepted = Volunteer.objects.filter(event=event).filter(volunteer_state=ApplicationState.STATE_ACCEPTED)
        volunteers_declined = Volunteer.objects.filter(event=event).filter(volunteer_state=ApplicationState.STATE_DENIED)

        context['volunteers'] = volunteers
        context['volunteers_accepted'] = volunteers_accepted
        context['volunteers_declined'] = volunteers_declined
        
        return context

@method_decorator(decorators, name="dispatch")
class VolunteerCSVDownloadView(View):
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="volunteers.csv"'
        event = get_current_event()
        volunteers = Volunteer.objects.filter(event=event)

        writer = csv.writer(response)
        writer.writerow(["Fan Name", "Email", "Legal Name", "Telegram Handle", "Departments", "Days Available", "Available Setup", "Available Teardown"])
        for volunteer in volunteers:
            departments = volunteer.department_interest.all()
            dept_str = ""
            for department in departments:
                dept_str += department.department_name + ";"
            days = volunteer.days_available.all()
            days_str = ""
            for day in days:
                days_str += day.name + ";"
            writer.writerow([volunteer.fan_name, volunteer.email, volunteer.legal_name, volunteer.telegram_handle, dept_str, days_str, volunteer.avail_setup, volunteer.avail_teardown])

        return response

@method_decorator(decorators, name="dispatch")
class VolunteerDetailsPageView(PageView):
    template_name = 'console-volunteers-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        volunteer = get_object_or_404(Volunteer, pk=kwargs['volunteer_id'])

        context['volunteer'] = volunteer

        return context

@method_decorator(decorators, name="dispatch")
class VolunteerActionAcceptRedirect(RedirectView):
    permanent = False
    pattern_name = 'console:volunteer-detail'

    def get_redirect_url(self, *args, **kwargs):
        volunteer = get_object_or_404(Volunteer, pk=kwargs['volunteer_id'])
        volunteer.volunteer_state = ApplicationState.STATE_ACCEPTED
        volunteer.state_changed = date.today()
        volunteer.save()

         send_paw_email('email-volunteers-accepted.html', {'volunteer': volunteer}, subject='PAWCon Volunteer Application', recipient_list=[volunteer.email], reply_to=settings.VOLUNTEER_EMAIL)

        return super().get_redirect_url(*args, **kwargs)

@method_decorator(decorators, name="dispatch")
class VolunteerActionDeclinedRedirect(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        volunteer = get_object_or_404(Volunteer, pk=kwargs['volunteer_id'])
        volunteer.volunteer_state = ApplicationState.STATE_DENIED
        volunteer.state_changed = date.today()
        volunteer.save()

         send_paw_email('email-volunteers-denied.html', {'volunteer': volunteer}, subject='PAWCon Volunteer Application', recipient_list=[volunteer.email], reply_to=settings.VOLUNTEER_EMAIL)

        return reverse('console:volunteers')
    
@method_decorator(decorators, name="dispatch")
class VolunteerActionDeleteRedirect(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        volunteer = get_object_or_404(Volunteer, pk=kwargs['volunteer_id'])
        volunteer.volunteer_state = ApplicationState.STATE_DELETED
        volunteer.state_changed = date.today()
        volunteer.save()

        return reverse('console:volunteers')