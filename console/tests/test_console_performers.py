from datetime import timedelta
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone

from core.models import ApplicationState, SchedulingConfig
from performers.models import Performer

from .base import ConsoleViewBase


class ConsolePerformerViewsTests(ConsoleViewBase):
    def setUp(self):
        super().setUp()
        self.performer_start = timezone.now().replace(minute=0, second=0, microsecond=0)
        SchedulingConfig.objects.create(
            event=self.event,
            day_available=self.day,
            panels_start=self.performer_start,
            panels_end=self.performer_start + timedelta(hours=2),
            performers_start=self.performer_start,
            performers_end=self.performer_start + timedelta(hours=3),
        )
        self.performer = Performer.objects.create(
            event=self.event,
            email="performer@example.com",
            legal_name="Legal Name",
            fan_name="Fan Name",
            phone_number="555-0103",
            twitter_handle="handle",
            telegram_handle="telegram",
            biography="Bio",
            dj_history="History",
            set_link="https://example.com/set",
            performer_state=ApplicationState.STATE_NEW,
        )

    def test_performers_list_view_renders(self):
        response = self.client.get(reverse("console:performers"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console-performers-list.html")
        self.assertIn(self.performer, response.context["performers"])

    def test_performer_detail_view_renders(self):
        response = self.client.get(
            reverse("console:performer-detail", args=[self.performer.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console-performer-detail.html")
        self.assertEqual(response.context["performer"], self.performer)

    @patch("console.views.performers.send_paw_email_new")
    def test_performer_accept_updates_state(self, mock_send):
        response = self.client.get(
            reverse("console:performer-accept", args=[self.performer.id])
        )

        self.assertEqual(response.status_code, 302)
        self.performer.refresh_from_db()
        self.assertEqual(self.performer.performer_state, ApplicationState.STATE_ACCEPTED)
        mock_send.assert_called_once()

    @patch("console.views.performers.send_paw_email_new")
    def test_performer_waitlist_updates_state(self, mock_send):
        response = self.client.get(
            reverse("console:performer-waitlist", args=[self.performer.id])
        )

        self.assertEqual(response.status_code, 302)
        self.performer.refresh_from_db()
        self.assertEqual(self.performer.performer_state, ApplicationState.STATE_WAITLIST)
        mock_send.assert_called_once()

    @patch("console.views.performers.send_paw_email_new")
    def test_performer_decline_updates_state(self, mock_send):
        response = self.client.get(
            reverse("console:performer-decline", args=[self.performer.id])
        )

        self.assertEqual(response.status_code, 302)
        self.performer.refresh_from_db()
        self.assertEqual(self.performer.performer_state, ApplicationState.STATE_DENIED)
        mock_send.assert_called_once()

    def test_performer_delete_updates_state(self):
        response = self.client.get(
            reverse("console:performer-delete", args=[self.performer.id])
        )

        self.assertEqual(response.status_code, 302)
        self.performer.refresh_from_db()
        self.assertEqual(self.performer.performer_state, ApplicationState.STATE_DELETED)

    def test_performer_schedule_view_renders(self):
        response = self.client.get(reverse("console:performer-schedule"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console-performers-schedule.html")
        self.assertIn("items", response.context)
        self.assertIn("performers", response.context)

    def test_performer_assign_two_step_flow(self):
        response = self.client.post(
            reverse("console:performer-assign", args=[self.performer.id]),
            data={"scheduled_day": self.day.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.performer.refresh_from_db()
        self.assertEqual(self.performer.scheduled_day, self.day)
        self.assertIn("scheduled_time", response.context["form"].fields)

        slot_time = timezone.localtime(self.performer_start)
        slot_value = slot_time.strftime("%Y-%m-%dT%H:%M:%S%z")

        with patch("console.views.performers.send_paw_email_new") as mock_send:
            response = self.client.post(
                reverse("console:performer-assign", args=[self.performer.id]),
                data={"scheduled_time": slot_value},
            )

        self.assertEqual(response.status_code, 302)
        self.performer.refresh_from_db()
        self.assertEqual(self.performer.performer_state, ApplicationState.STATE_ASSIGNED)
        self.assertEqual(response["Location"], reverse("console:performer-schedule"))
        mock_send.assert_called_once()

    def test_performer_unschedule_uses_referer(self):
        self.performer.performer_state = ApplicationState.STATE_ASSIGNED
        self.performer.scheduled_day = self.day
        self.performer.scheduled_time = timezone.now()
        self.performer.save()

        response = self.client.get(
            reverse("console:performer-unassign", args=[self.performer.id]),
            HTTP_REFERER=reverse("console:performer-detail", args=[self.performer.id]),
        )

        self.assertEqual(response.status_code, 302)
        self.performer.refresh_from_db()
        self.assertEqual(self.performer.performer_state, ApplicationState.STATE_ACCEPTED)
        self.assertIsNone(self.performer.scheduled_time)
        self.assertEqual(
            response["Location"],
            reverse("console:performer-detail", args=[self.performer.id]),
        )
