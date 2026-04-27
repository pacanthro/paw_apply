from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import RedirectView
from modules.mixins import SuperuserRequiredMixin
from modules.page_view import PageView
from system.forms.times_available import TimesAvailableCreateForm, TimesAvailableEditForm
from volunteers.models import TimesAvailable

class TimesAvailableListView(SuperuserRequiredMixin, PageView):
    template_name = "system-times-available-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['times_available'] = TimesAvailable.objects.order_by('order').all()

        return context

class TimesAvailableEditView(SuperuserRequiredMixin, PageView):
    template_name = "system-times-available-edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slot = get_object_or_404(TimesAvailable, pk=kwargs['times_id'])
        form = TimesAvailableEditForm(instance=slot)

        context['slot'] = slot
        context['form'] = form

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = TimesAvailableEditForm(request.POST, instance=context['slot'])

        context['form'] = form

        if form.is_valid():
            form.save()

        return self.render_to_response(context)

class TimesAvailableCreateView(SuperuserRequiredMixin, PageView):
    template_name = "system-times-available-create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = TimesAvailableCreateForm()

        context['form'] = form

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = TimesAvailableCreateForm(request.POST)

        context['form'] = form

        if form.is_valid():
            times = form.save()

            return HttpResponseRedirect(reverse('system:times-edit', args=[times.key]))

        return self.render_to_response(context)

class TimesAvailableDeleteRedirectView(SuperuserRequiredMixin, RedirectView):
    permanent = False
    pattern_name = 'system:times-list'

    def get_redirect_url(self, *args, **kwargs):
        time_available = get_object_or_404(TimesAvailable, pk=kwargs['times_id'])
        time_available.delete()

        return reverse('system:times-list')
