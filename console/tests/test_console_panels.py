from datetime import timedelta
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone

from core.models import ApplicationState, EventRoom, RoomType, SchedulingConfig
from panels.models import Panel, PanelDuration, PanelSlot

from .base import ConsoleViewBase


class ConsolePanelViewsTests(ConsoleViewBase):
    def setUp(self):
        super().setUp()
        self.room = EventRoom.objects.create(
            event=self.event,
            room_name="Panel Room",
            room_type=RoomType.ROOM_PANELS,
        )
        self.panel_duration = PanelDuration.objects.create(key="60MN", name="60 Min", order=1)
        self.panel_slot = PanelSlot.objects.create(key="AM", name="Morning", order=1)
        self.panel_start = timezone.now().replace(minute=0, second=0, microsecond=0)
        SchedulingConfig.objects.create(
            event=self.event,
            day_available=self.day,
            panels_start=self.panel_start,
            panels_end=self.panel_start + timedelta(hours=2),
            performers_start=self.panel_start,
            performers_end=self.panel_start + timedelta(hours=2),
        )
        self.panel = self._create_panel()

    def _create_panel(self, **overrides):
        data = {
            "event": self.event,
            "email": "panel@example.com",
            "legal_name": "Legal Name",
            "fan_name": "Fan Name",
            "phone_number": "555-0102",
            "twitter_handle": "handle",
            "telegram_handle": "telegram",
            "panelist_bio": "Bio",
            "panel_name": "Panel Name",
            "panel_description": "Description",
            "panel_duration": self.panel_duration,
            "equipment_needs": "None",
            "mature_content": False,
            "check_ids": True,
            "panel_state": ApplicationState.STATE_NEW,
        }
        data.update(overrides)
        panel = Panel.objects.create(**data)
        panel.panel_day.add(self.day)
        panel.panel_times.add(self.panel_slot)
        return panel

    def test_panels_list_view_renders(self):
        response = self.client.get(reverse("console:panels"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console-panels-list.html")
        self.assertIn(self.panel, response.context["panels"])

    def test_panel_detail_view_renders(self):
        response = self.client.get(reverse("console:panel-detail", args=[self.panel.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console-panels-detail.html")
        self.assertEqual(response.context["panel"], self.panel)

    @patch("console.views.panels.send_paw_email")
    def test_panel_accept_updates_state(self, mock_send):
        response = self.client.get(reverse("console:panel-accept", args=[self.panel.id]))

        self.assertEqual(response.status_code, 302)
        self.panel.refresh_from_db()
        self.assertEqual(self.panel.panel_state, ApplicationState.STATE_ACCEPTED)
        mock_send.assert_called_once()

    @patch("console.views.panels.send_paw_email")
    def test_panel_waitlist_updates_state(self, mock_send):
        response = self.client.get(reverse("console:panel-waitlist", args=[self.panel.id]))

        self.assertEqual(response.status_code, 302)
        self.panel.refresh_from_db()
        self.assertEqual(self.panel.panel_state, ApplicationState.STATE_WAITLIST)
        mock_send.assert_called_once()

    @patch("console.views.panels.send_paw_email")
    def test_panel_deny_updates_state(self, mock_send):
        response = self.client.get(reverse("console:panel-deny", args=[self.panel.id]))

        self.assertEqual(response.status_code, 302)
        self.panel.refresh_from_db()
        self.assertEqual(self.panel.panel_state, ApplicationState.STATE_DENIED)
        mock_send.assert_called_once()

    def test_panel_delete_updates_state(self):
        response = self.client.get(reverse("console:panel-delete", args=[self.panel.id]))

        self.assertEqual(response.status_code, 302)
        self.panel.refresh_from_db()
        self.assertEqual(self.panel.panel_state, ApplicationState.STATE_DELETED)

    def test_panel_schedule_view_renders(self):
        assigned = self._create_panel(
            email="assigned@example.com",
            panel_state=ApplicationState.STATE_ASSIGNED,
            scheduled_room=self.room,
            scheduled_day=self.day,
            scheduled_time=timezone.now(),
        )

        response = self.client.get(reverse("console:panels-schedule"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console-panels-schedule.html")
        self.assertIn(self.room, response.context["event_rooms"])
        self.assertEqual(len(response.context["schedules"]), 1)
        self.assertEqual(len(response.context["filled_slots"]), 1)
        self.assertEqual(response.context["filled_slots"][0]["panel"], assigned)

    def test_panel_assign_two_step_flow(self):
        response = self.client.post(
            reverse("console:panel-assign", args=[self.panel.id]),
            data={"scheduled_room": self.room.id, "scheduled_day": self.day.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.panel.refresh_from_db()
        self.assertEqual(self.panel.scheduled_day, self.day)
        self.assertIn("scheduled_time", response.context["form"].fields)

        slot_time = timezone.localtime(self.panel_start)
        slot_value = slot_time.strftime("%Y-%m-%dT%H:%M:%S%z")

        with patch("console.views.panels.send_paw_email") as mock_send:
            response = self.client.post(
                reverse("console:panel-assign", args=[self.panel.id]),
                data={"scheduled_time": slot_value},
            )

        self.assertEqual(response.status_code, 302)
        self.panel.refresh_from_db()
        self.assertEqual(self.panel.panel_state, ApplicationState.STATE_ASSIGNED)
        self.assertEqual(response["Location"], reverse("console:panels-schedule"))
        mock_send.assert_called_once()

    def test_panel_unschedule_uses_referer(self):
        self.panel.panel_state = ApplicationState.STATE_ASSIGNED
        self.panel.scheduled_day = self.day
        self.panel.scheduled_room = self.room
        self.panel.scheduled_time = timezone.now()
        self.panel.save()

        response = self.client.get(
            reverse("console:panel-unassign", args=[self.panel.id]),
            HTTP_REFERER=reverse("console:panel-detail", args=[self.panel.id]),
        )

        self.assertEqual(response.status_code, 302)
        self.panel.refresh_from_db()
        self.assertEqual(self.panel.panel_state, ApplicationState.STATE_ACCEPTED)
        self.assertIsNone(self.panel.scheduled_time)
        self.assertEqual(
            response["Location"],
            reverse("console:panel-detail", args=[self.panel.id]),
        )

    def test_panel_cancel_updates_state(self):
        response = self.client.get(
            reverse("console:panel-cancel", args=[self.panel.id]),
            HTTP_REFERER=reverse("console:panels-schedule"),
        )

        self.assertEqual(response.status_code, 302)
        self.panel.refresh_from_db()
        self.assertEqual(self.panel.panel_state, ApplicationState.STATE_CANCELED)
