import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Event


class ConsoleLoginTests(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.event = Event.objects.create(
            event_name="Test Event",
            event_start=today,
            event_end=today + datetime.timedelta(days=2),
            submissions_end=today + datetime.timedelta(days=1),
            max_merchants=50,
        )

    def test_login_view_renders(self):
        response = self.client.get(reverse("console:login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console-login.html")
        self.assertIn("form", response.context)
        self.assertEqual(response.context["redirect"], "/console")
        self.assertTrue(response.context["is_console"])
        self.assertEqual(response.context["event"], self.event)

    def test_login_view_redirects_after_valid_login(self):
        user = get_user_model().objects.create_user(
            username="console-user",
            email="console@example.com",
            password="secret-pass",
        )

        response = self.client.post(
            f"{reverse('console:login')}?next=/console/merchants",
            data={"username": user.username, "password": "secret-pass"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/console/merchants")
