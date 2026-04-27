from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import RedirectView
from modules.mixins import SuperuserRequiredMixin
from modules.page_view import PageView
from panels.models import PanelSlot
from system.forms import PanelSlotEditForm, PanelSlotCreateForm

class PanelSlotsListView(SuperuserRequiredMixin, PageView):
    template_name = "system-panel-slot-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['slots'] = PanelSlot.objects.order_by('order').all()

        return context
    
class PanelSlotsEditView(SuperuserRequiredMixin, PageView):
    template_name = "system-panel-slot-edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slot = get_object_or_404(PanelSlot, pk=kwargs['slot_id'])
        form = PanelSlotEditForm(instance=slot)

        context['slot'] = slot
        context['form'] = form

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = PanelSlotEditForm(request.POST, instance=context['slot'])

        context['form'] = form

        if form.is_valid():
            form.save()

        return self.render_to_response(context)

class PanelSlotsCreateView(SuperuserRequiredMixin, PageView):
    template_name = "system-panel-slot-create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = PanelSlotCreateForm()

        context['form'] = form

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = PanelSlotCreateForm(request.POST)

        context['form'] = form

        if form.is_valid():
            slot = form.save()

            return HttpResponseRedirect(reverse('system:slot-edit', args=[slot.key]))

        return self.render_to_response(context)

class PanelSlotDeleteRedirectView(SuperuserRequiredMixin, RedirectView):
    permanent = False
    pattern_name = 'system:slot-list'

    def get_redirect_url(self, *args, **kwargs):
        table = get_object_or_404(PanelSlot, pk=kwargs['slot_id'])
        table.delete()

        return reverse('system:slot-list')
