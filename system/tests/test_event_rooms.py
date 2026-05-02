from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from core.models import EventRoom
from system.views.event_rooms import EventRoomsListPageView

from .base import SystemViewsTestCase


class EventRoomViewsTests(SystemViewsTestCase):
    def test_event_rooms_views_scope_to_current_event_and_support_crud(self):
        current_room = EventRoom.objects.create(
            event=self.current_event,
            room_name="Main",
            room_type="ROOM_PANELS",
        )
        other_room = EventRoom.objects.create(
            event=self.past_event,
            room_name="Old",
            room_type="ROOM_PANELS",
        )

        request = self.factory.get(reverse("system:rooms-list"))
        request.user = AnonymousUser()
        view = EventRoomsListPageView()
        view.request = request

        context = view.get_context_data()

        self.assertEqual(list(context["event_rooms"]), [current_room])
        self.assertNotIn(other_room, context["event_rooms"])

        create_response = self.client.post(
            reverse("system:rooms-create"),
            {"room_name": "New Room", "room_type": "ROOM_PANELS"},
        )

        created = EventRoom.objects.get(room_name="New Room")
        self.assertEqual(created.event, self.current_event)
        self.assertRedirects(
            create_response,
            reverse("system:rooms-edit", args=[created.id]),
        )

        invalid_response = self.client.post(
            reverse("system:rooms-create"),
            {"room_name": "", "room_type": "ROOM_PANELS"},
        )

        self.assertEqual(invalid_response.status_code, 200)
        self.assertFalse(EventRoom.objects.filter(room_name="").exists())
        self.assertTrue(invalid_response.context["form"].errors)

        edit_response = self.client.post(
            reverse("system:rooms-edit", args=[current_room.id]),
            {"room_name": "Main Stage", "room_type": "ROOM_PANELS"},
        )

        current_room.refresh_from_db()
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(current_room.room_name, "Main Stage")

        delete_response = self.client.get(
            reverse("system:rooms-delete", args=[current_room.id])
        )

        self.assertRedirects(delete_response, reverse("system:rooms-list"))
        self.assertFalse(EventRoom.objects.filter(pk=current_room.pk).exists())

    def test_event_room_edit_invalid_post_rerenders_without_saving(self):
        room = EventRoom.objects.create(
            event=self.current_event,
            room_name="Main",
            room_type="ROOM_PANELS",
        )

        response = self.client.post(
            reverse("system:rooms-edit", args=[room.id]),
            {"room_name": "", "room_type": "ROOM_PANELS"},
        )

        room.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(room.room_name, "Main")
