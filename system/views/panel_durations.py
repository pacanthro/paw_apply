from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import RedirectView
from modules.mixins import SuperuserRequiredMixin
from modules.page_view import PageView
from panels.models import PanelDuration
from system.forms import PanelDurationCreateForm, PanelDurationEditForm

class PanelDurationListView(SuperuserRequiredMixin, PageView):
    template_name = "system-panel-duration-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['durations'] = PanelDuration.objects.filter(deleted=False).order_by('order').all()

        return context

class PanelDurationEditView(SuperuserRequiredMixin, PageView):
    template_name = "system-panel-duration-edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        duration = get_object_or_404(PanelDuration, pk=kwargs['duration_id'])
        form = PanelDurationEditForm(instance=duration)

        context['duration'] = duration
        context['form'] = form

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = PanelDurationEditForm(request.POST, instance=context['duration'])

        context['form'] = form

        if form.is_valid():
            form.save()

        return self.render_to_response(context)

class PanelDurationCreateView(SuperuserRequiredMixin, PageView):
    template_name = "system-panel-duration-create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = PanelDurationCreateForm()

        context['form'] = form

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = PanelDurationCreateForm(request.POST)

        context['form'] = form

        if form.is_valid():
            duration = form.save()

            return HttpResponseRedirect(reverse('system:duration-edit', args=[duration.key]))

        return self.render_to_response(context)

class PanelDurationDeleteRedirectView(SuperuserRequiredMixin, RedirectView):
    permanent = False
    pattern_name = 'system:slot-list'

    def get_redirect_url(self, *args, **kwargs):
        duration = get_object_or_404(PanelDuration, pk=kwargs['duration_id'])
        duration.deleted = True
        duration.save()

        return reverse('system:duration-list')
