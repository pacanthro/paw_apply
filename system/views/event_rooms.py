from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.base import RedirectView
from modules.page_view import PageView
from panels.models import EventRoom

from system.forms import EventRoomEditForm

class EventRoomsListPageView(PageView):
    template_name = "system-event-rooms-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_rooms = EventRoom.objects.filter(event=context['event']).all()

        context['event_rooms'] = event_rooms

        return context
    
class EventRoomsCreatePageView(PageView):
    template_name = "system-event-rooms-create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = EventRoomEditForm()

        context['form'] = form

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = EventRoomEditForm(request.POST,)

        context['form'] = form

        if form.is_valid():
            event_room = form.save(commit=False)
            event_room.event = context['event']
            event_room.save()

            return HttpResponseRedirect(reverse('system:rooms-edit', args=[event_room.id]))

        return self.render_to_response(context)

class EventRoomsEditPageView(PageView):
    template_name = "system-event-rooms-edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_room = get_object_or_404(EventRoom, pk=kwargs['event_room_id'])
        form = EventRoomEditForm(instance=event_room)

        context['event_room'] = event_room
        context['form'] = form

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = EventRoomEditForm(request.POST, instance=context['event_room'])

        context['form'] = form

        if form.is_valid():
            form.save()

        return self.render_to_response(context)

class EventRoomsDeleteRedirectView(RedirectView):
    permanent = False
    pattern_name = 'system:rooms-list'

    def get_redirect_url(self, *args, **kwargs):
        event_room = get_object_or_404(EventRoom, pk=kwargs['event_room_id'])
        event_room.delete()

        return reverse('system:rooms-list')