from core.models import DaysAvailable
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import RedirectView
from modules.mixins import SuperuserRequiredMixin
from modules.page_view import PageView
from system.forms import DaysAvailableEditForm, DaysAvailableCreateForm

class DaysAvailableListView(SuperuserRequiredMixin, PageView):
    template_name = "system-days-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['days_available'] = DaysAvailable.objects.all()

        return context

class DaysAvailableEditView(SuperuserRequiredMixin, PageView):
    template_name = "system-days-edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        day_available = get_object_or_404(DaysAvailable, pk=kwargs['day_id'])
        form = DaysAvailableEditForm(instance=day_available)

        context['day_available'] = day_available
        context['form'] = form

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = DaysAvailableEditForm(request.POST, instance=context['day_available'])
        
        context['form'] = form

        if form.is_valid():
            form.save()

        return self.render_to_response(context)

class DaysAvailableCreateView(SuperuserRequiredMixin, PageView):
    template_name = "system-days-create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = DaysAvailableCreateForm()

        context['form'] = form

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = DaysAvailableCreateForm(request.POST)
        
        context['form'] = form

        if form.is_valid():
            day_available = form.save()

            return HttpResponseRedirect(reverse('system:days-edit', args=[day_available.key]))

        return self.render_to_response(context)

class DayAvailableDeleteRedirectView(SuperuserRequiredMixin, RedirectView):
    permanent = False
    pattern_name = 'system:days-list'

    def get_redirect_url(self, *args, **kwargs):
        day_available = get_object_or_404(DaysAvailable, pk=kwargs['day_id'])
        day_available.delete()

        return reverse('system:days-list')
