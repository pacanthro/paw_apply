import datetime

from django.urls import reverse

from core.models import Event

from .base import SystemViewsTestCase


class EventViewsTests(SystemViewsTestCase):
    def test_event_index_renders_current_event_context(self):
        older_event = Event.objects.create(
            event_name="Older Event",
            event_start=self.past_event.event_start - datetime.timedelta(days=10),
            event_end=self.past_event.event_end - datetime.timedelta(days=10),
            submissions_end=self.past_event.submissions_end - datetime.timedelta(days=10),
            max_merchants=10,
        )

        response = self.client.get(reverse("system:event-index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "system-event-index.html")
        self.assertEqual(response.context["event"], self.current_event)
        self.assertTrue(response.context["is_console"])
        self.assertEqual(
            list(response.context["past_events"]),
            [self.past_event, older_event],
        )

    def test_event_edit_renders_form_for_current_event(self):
        response = self.client.get(reverse("system:event-edit"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "system-event-edit.html")
        self.assertEqual(response.context["form"].instance, self.current_event)

    def test_event_edit_updates_current_event_settings(self):
        response = self.client.post(
            reverse("system:event-edit"),
            {
                "max_merchants": 75,
                "max_party_rooms": 12,
                "submissions_end": self.current_event.submissions_end.isoformat(),
                "module_panels_enabled": "on",
                "module_merchants_enabled": "on",
                "module_performers_enabled": "",
                "module_partyfloor_enabled": "on",
                "module_competitors_enabled": "",
                "voucher_performers": "PERF2026",
                "voucher_volunteer": "VOL2026",
            },
        )

        self.current_event.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.current_event.max_merchants, 75)
        self.assertEqual(self.current_event.max_party_rooms, 12)
        self.assertTrue(self.current_event.module_panels_enabled)
        self.assertTrue(self.current_event.module_merchants_enabled)
        self.assertFalse(self.current_event.module_performers_enabled)
        self.assertTrue(self.current_event.module_partyfloor_enabled)
        self.assertFalse(self.current_event.module_competitors_enabled)
        self.assertEqual(self.current_event.voucher_performers, "PERF2026")
        self.assertEqual(self.current_event.voucher_volunteer, "VOL2026")

    def test_event_edit_invalid_post_rerenders_without_saving(self):
        original_max_merchants = self.current_event.max_merchants

        response = self.client.post(
            reverse("system:event-edit"),
            {
                "max_merchants": "",
                "max_party_rooms": 8,
                "submissions_end": "",
                "voucher_performers": "BROKEN",
                "voucher_volunteer": "BROKEN",
            },
        )

        self.current_event.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(self.current_event.max_merchants, original_max_merchants)
