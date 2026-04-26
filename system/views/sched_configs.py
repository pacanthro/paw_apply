from core.models import SchedulingConfig
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import RedirectView
from modules.page_view import PageView
from system.forms import SchedulingConfigEditForm, SchedulingConfigCreateForm

class SchedulingConfigListView(PageView):
    template_name = "system-schedconfig-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['sched_configs'] = SchedulingConfig.objects.filter(event=context['event']).all()

        return context
    
class SchedulingConfigEditView(PageView):
    template_name = "system-schedconfig-edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sched_config = get_object_or_404(SchedulingConfig, pk=kwargs['config_id'])
        form = SchedulingConfigEditForm(instance=sched_config)

        context['sched_config'] = sched_config
        context['form'] = form
        
        return context
    
    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = SchedulingConfigEditForm(request.POST, instance=context['sched_config'])

        context['form'] = form

        if form.is_valid():
            form.save()

        return self.render_to_response(context)

class SchedulingConfigCreateView(PageView):
    template_name = "system-schedconfig-create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = SchedulingConfigCreateForm()

        context['form'] = form

        return context
    
    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = SchedulingConfigCreateForm(request.POST)

        context['form'] = form

        if form.is_valid():
            config = form.save(commit=False)
            config.event = context['event']
            config.save()

            return HttpResponseRedirect(reverse('system:schedconfig-edit', args=[config.id]))

        return self.render_to_response(context)

class SchedulingConfighDeleteRedirectView(RedirectView):
    permanent = False
    pattern_name = 'system:departments-list'

    def get_redirect_url(self, *args, **kwargs):
        config = get_object_or_404(SchedulingConfig, pk=kwargs['config_id'])
        config.delete()

        return reverse('system:schedconfig-list')
