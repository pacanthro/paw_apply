import datetime
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import ApplicationState, Event
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
            page_interstitial="Interstitial **content**",
            page_apply="Apply *content*",
            page_confirmation="Confirmation _content_",
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
            "captcha_0": "dummy-value",
            "captcha_1": "PASSED",
        }
        data.update(overrides)
        return data

    def test_index_view_renders(self):
        response = self.client.get(reverse("performers:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "performer.html")
        self.assertTrue(response.context["is_djs"])
        self.assertEqual(response.context["event"], self.event)
        self.assertContains(response, "<strong>content</strong>", html=True)
        self.assertContains(response, reverse("performers:apply"))

    def test_index_hides_apply_button_when_submissions_closed(self):
        self.event.submissions_end = datetime.date.today() - datetime.timedelta(days=1)
        self.event.save(update_fields=["submissions_end"])

        response = self.client.get(reverse("performers:index"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse("performers:apply"))

    def test_index_hides_apply_button_when_module_disabled(self):
        self.event.module_performers_enabled = False
        self.event.save(update_fields=["module_performers_enabled"])

        response = self.client.get(reverse("performers:index"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse("performers:apply"))

    def test_apply_view_renders(self):
        response = self.client.get(reverse("performers:apply"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "performer-apply.html")
        self.assertTrue(response.context["is_djs"])
        self.assertEqual(response.context["event"], self.event)
        self.assertIsInstance(response.context["form"], PerformerForm)
        self.assertContains(response, "<em>content</em>", html=True)
        self.assertContains(response, 'action="%s"' % reverse("performers:new"))

    def test_apply_hides_form_when_module_disabled(self):
        self.event.module_performers_enabled = False
        self.event.save(update_fields=["module_performers_enabled"])

        response = self.client.get(reverse("performers:apply"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "performer-apply.html")
        self.assertNotContains(response, "<form", html=False)
        self.assertContains(response, "Sorry DJ Applictions are currently closed.")

    @override_settings(PERFORMERS_EMAIL="performers@example.com")
    @patch("captcha.fields.settings.CAPTCHA_TEST_MODE", True)
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

    @patch("captcha.fields.settings.CAPTCHA_TEST_MODE", True)
    @patch("performers.views.send_paw_email_new")
    def test_new_view_invalid_rerenders(self, send_paw_email_new):
        response = self.client.post(reverse("performers:new"), data=self._valid_post_data(email=""))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "performer-apply.html")
        form = response.context["form"]
        self.assertIn("email", form.errors)
        self.assertEqual(Performer.objects.count(), 0)
        send_paw_email_new.assert_not_called()

    @patch("performers.views.send_paw_email_new")
    def test_new_view_rejects_missing_captcha(self, send_paw_email_new):
        data = self._valid_post_data()
        data.pop("captcha_0")
        data.pop("captcha_1")

        response = self.client.post(reverse("performers:new"), data=data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "performer-apply.html")
        form = response.context["form"]
        self.assertIn("captcha", form.errors)
        self.assertEqual(Performer.objects.count(), 0)
        send_paw_email_new.assert_not_called()

    def test_confirm_view_renders(self):
        response = self.client.get(reverse("performers:confirm"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "performer-confirm.html")
        self.assertContains(response, "<em>content</em>", html=True)


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
            "captcha_0": "dummy-value",
            "captcha_1": "PASSED",
        }
        data.update(overrides)
        return data

    @patch("captcha.fields.settings.CAPTCHA_TEST_MODE", True)
    def test_form_accepts_valid_data(self):
        form = PerformerForm(data=self._valid_form_data(email="valid@example.com"))

        self.assertTrue(form.is_valid(), form.errors)

    @patch("captcha.fields.settings.CAPTCHA_TEST_MODE", True)
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

    @patch("captcha.fields.settings.CAPTCHA_TEST_MODE", True)
    def test_clean_email_allows_duplicate_for_past_event(self):
        past_event = Event.objects.create(
            event_name="Past Event",
            event_start=datetime.date.today() - datetime.timedelta(days=30),
            event_end=datetime.date.today() - datetime.timedelta(days=20),
            submissions_end=datetime.date.today() - datetime.timedelta(days=25),
        )
        Performer.objects.create(
            event=past_event,
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

        self.assertTrue(form.is_valid(), form.errors)

    def test_form_rejects_missing_captcha(self):
        data = self._valid_form_data(email="valid@example.com")
        data.pop("captcha_0")
        data.pop("captcha_1")

        form = PerformerForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("captcha", form.errors)


class PerformerModelTests(TestCase):
    def test_performer_defaults_to_new_state_and_sets_state_changed(self):
        today = datetime.date.today()
        event = Event.objects.create(
            event_name="Test Event",
            event_start=today,
            event_end=today + datetime.timedelta(days=2),
            submissions_end=today + datetime.timedelta(days=1),
        )

        performer = Performer.objects.create(
            event=event,
            email="performer@example.com",
            legal_name="Legal Name",
            fan_name="Fan Name",
            phone_number="555-0101",
            twitter_handle="handle",
            telegram_handle="telehandle",
            biography="Bio",
            dj_history="History",
            set_link="https://example.com/set",
        )

        self.assertEqual(performer.performer_state, ApplicationState.STATE_NEW)
        self.assertEqual(performer.state_changed, today)
        self.assertIsNone(performer.scheduled_day)
        self.assertIsNone(performer.scheduled_time)
