from core.models import Event
from modules.page_view import PageView
from modules.mixins import SuperuserRequiredMixin
from system.forms import EventEditForm

class EventIndexPageView(SuperuserRequiredMixin, PageView):
    template_name = "system-event-index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['past_events'] = Event.objects.exclude(pk=context['event'].pk).order_by('-event_end').all()

        return context
    
class EventEditPageView(SuperuserRequiredMixin, PageView):
    template_name = "system-event-edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = EventEditForm(instance=context['event'])

        context['form'] = form

        return context
    
    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = EventEditForm(request.POST, instance=context['event'])

        context['form'] = form

        if form.is_valid():
            form.save()

        return self.render_to_response(context)
