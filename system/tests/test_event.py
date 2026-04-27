from django.urls import reverse

from .base import SystemViewsTestCase


class EventViewsTests(SystemViewsTestCase):
    def test_event_index_renders_current_event_context(self):
        response = self.client.get(reverse("system:event-index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "system-event-index.html")
        self.assertEqual(response.context["event"], self.current_event)
        self.assertTrue(response.context["is_console"])
