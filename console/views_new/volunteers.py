import asyncio
import csv

from .page_view import PageView
from console.forms import VolunteerTaskStartForm, VolunteerTaskEndForm, VolunteerAddTaskForm
from core.models import get_current_event, ApplicationState
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.base import RedirectView
from modules.email import send_paw_email
from volunteers.models import Volunteer, VolunteerTask

from datetime import date
from django.db.models import DurationField, F, ExpressionWrapper, Sum
import sys

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
        tasks = VolunteerTask.objects.filter(volunteer=volunteer).annotate(task_hours=F('task_end') - F('task_start')).annotate(effective_hours=ExpressionWrapper(F('task_hours') * F('task_multiplier'), output_field=DurationField()))
        total_hours = VolunteerTask.objects.filter(volunteer=volunteer).annotate(task_hours=F('task_end') - F('task_start')).annotate(effective_hours=ExpressionWrapper(F('task_hours') * F('task_multiplier'), output_field=DurationField())).aggregate(total_hours=Sum(F('effective_hours')))
        print(total_hours, file=sys.stderr)
        context['volunteer'] = volunteer
        context['tasks'] = tasks
        context['total_hours'] = total_hours

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

@method_decorator(decorators, name="dispatch")
class VolunteerDashboardPageView(PageView):
    template_name = 'console-volunteers-dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_current_event()
        active_tasks = VolunteerTask.objects.filter(event=event).filter(task_end=None)
        idle_volunteers = Volunteer.objects.filter(event=event).filter(volunteer_state=ApplicationState.STATE_ACCEPTED).exclude(id__in=VolunteerTask.objects.filter(task_end=None).values_list('volunteer', flat=True))

        context['active_tasks'] = []
        context['idle_volunteers'] = []

        for task in active_tasks:
            form = VolunteerTaskEndForm(instance=task)
            context['active_tasks'].append({'task': task, 'form': form})

        for volunteer in idle_volunteers:
            form = VolunteerTaskStartForm(volunteer=volunteer, user=self.request.user)
            context['idle_volunteers'].append({'model': volunteer, 'form': form})

        return context
    
@method_decorator(decorators, name="dispatch")
class VolunteerStartTaskRedirect(View):
    permanent = False

    def get_context_data(self, **kwargs):
        context = {}
        event = get_current_event()
        volunteer = get_object_or_404(Volunteer, pk=kwargs['volunteer_id'])
        
        context['event'] = event
        context['volunteer'] = volunteer

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)

        form = VolunteerTaskStartForm(request.POST, volunteer=context['volunteer'], user=request.user)

        if form.is_valid():
            task = form.save(commit=False)
            task.save()

        return HttpResponseRedirect(reverse('console:volunteer-dashboard'))

@method_decorator(decorators, name="dispatch")
class VolunteerEndTaskRedirect(PageView):
    template_name = 'console-volunteer-end-task.html'
    permanent = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = get_object_or_404(VolunteerTask, pk=kwargs['task_id'])
        form = VolunteerTaskEndForm(instance=task)

        context['task'] = task
        context['form'] = form

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)

        form = VolunteerTaskEndForm(request.POST, instance=context['task'])
        
        context['form']  = form

        if form.is_valid():
            task = form.save(commit=False)
            task.save()

            return HttpResponseRedirect(reverse('console:volunteer-dashboard'))

        return self.render_to_response(context)

@method_decorator(decorators, name="dispatch")
class VolunteerAddTaskPageView(PageView):
    template_name = 'console-volunteer-add-task.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        volunteer = get_object_or_404(Volunteer, pk=kwargs['volunteer_id'])

        form = VolunteerAddTaskForm(volunteer=volunteer, user=self.request.user)

        context['form'] = form
        context['volunteer'] = volunteer

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        form = VolunteerAddTaskForm(request.POST, volunteer=context['volunteer'], user=self.request.user)
        context['form'] = form

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('console:volunteer-detail', kwargs={'volunteer_id': context['volunteer'].id}))

        return  self.render_to_response(context)
