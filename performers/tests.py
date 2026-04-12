import datetime
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import Event
from performers.forms import PerformerForm
from performers.models import Performer, PerformerContent


class PerformerViewsTests(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.event = Event.objects.create(
            event_name="Test Event",
            event_start=today,
            event_end=today + datetime.timedelta(days=2),
            submissions_end=today + datetime.timedelta(days=1),
            module_performers_enabled=True,
        )
        self.content = PerformerContent.objects.create(
            card_title="Performer Card",
            card_body="Card body",
            card_cta="Apply now",
            page_interstitial="Interstitial content",
            page_apply="Apply content",
            page_confirmation="Confirmation content",
            email_submit="Submit email content",
            email_accepted="Accepted email content",
            email_declined="Declined email content",
            email_waitlisted="Waitlisted email content",
            email_assigned="Assigned email content",
        )

    def _valid_post_data(self, **overrides):
        data = {
            "email": "performer@example.com",
            "legal_name": "Legal Name",
            "fan_name": "Fan Name",
            "phone_number": "555-0100",
            "twitter_handle": "handle",
            "telegram_handle": "telehandle",
            "biography": "Bio text",
            "dj_history": "History text",
            "set_link": "https://example.com/set",
        }
        data.update(overrides)
        return data

    def test_index_view_renders(self):
        response = self.client.get(reverse("performers:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "performer.html")
        self.assertTrue(response.context["is_djs"])
        self.assertEqual(response.context["event"], self.event)

    def test_apply_view_renders(self):
        response = self.client.get(reverse("performers:apply"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "performer-apply.html")
        self.assertTrue(response.context["is_djs"])
        self.assertEqual(response.context["event"], self.event)
        self.assertIsInstance(response.context["form"], PerformerForm)

    @override_settings(PERFORMERS_EMAIL="performers@example.com")
    @patch("performers.views.send_paw_email_new")
    def test_new_view_creates_performer_and_redirects(self, send_paw_email_new):
        response = self.client.post(reverse("performers:new"), data=self._valid_post_data())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("performers:confirm"))
        self.assertEqual(Performer.objects.count(), 1)

        performer = Performer.objects.get(email="performer@example.com", event=self.event)
        self.assertEqual(performer.legal_name, "Legal Name")
        self.assertEqual(performer.fan_name, "Fan Name")

        send_paw_email_new.assert_called_once()
        args, kwargs = send_paw_email_new.call_args
        self.assertEqual(args[0], self.content.email_submit)
        self.assertEqual(kwargs["subject"], "PAWCon DJ Application")
        self.assertEqual(kwargs["recipient_list"], ["performer@example.com"])
        self.assertEqual(kwargs["reply_to"], "performers@example.com")

    def test_new_view_invalid_rerenders(self):
        response = self.client.post(
            reverse("performers:new"),
            data=self._valid_post_data(email=""),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "performer-apply.html")
        self.assertIn("form", response.context)
        self.assertEqual(Performer.objects.count(), 0)

    def test_confirm_view_renders(self):
        response = self.client.get(reverse("performers:confirm"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "performer-confirm.html")


class PerformerFormTests(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.event = Event.objects.create(
            event_name="Test Event",
            event_start=today,
            event_end=today + datetime.timedelta(days=2),
            submissions_end=today + datetime.timedelta(days=1),
        )

    def _valid_form_data(self, **overrides):
        data = {
            "email": "dup@example.com",
            "legal_name": "Legal Name",
            "fan_name": "Fan Name",
            "phone_number": "555-0101",
            "twitter_handle": "handle",
            "telegram_handle": "telehandle",
            "biography": "Bio text",
            "dj_history": "History text",
            "set_link": "https://example.com/set",
        }
        data.update(overrides)
        return data

    def test_clean_email_rejects_duplicate_for_current_event(self):
        Performer.objects.create(
            event=self.event,
            email="dup@example.com",
            legal_name="Existing",
            fan_name="Existing",
            phone_number="555-0102",
            twitter_handle="existing",
            telegram_handle="existing",
            biography="",
            dj_history="",
            set_link="https://example.com/old",
        )

        form = PerformerForm(data=self._valid_form_data())

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
