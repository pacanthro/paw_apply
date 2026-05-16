import datetime
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import DaysAvailable, Event
from panels.forms import PanelForm
from panels.models import Panel, PanelContent, PanelDuration, PanelSlot

class PanelViewsTests(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.event = Event.objects.create(
            event_name="PAWCon",
            event_start=today,
            event_end=today + datetime.timedelta(days=3),
            submissions_end=today,
            module_panels_enabled=True,
        )
        self.content = PanelContent.objects.create(
            card_title="Panel Card",
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

    def build_valid_payload(self, **overrides):
        day = (
            overrides.pop("day")
            if "day" in overrides
            else DaysAvailable.objects.create(
                key="FRI",
                name="Friday",
                order=1,
                available_scheduling=True,
                party_only=False,
            )
        )
        slot = (
            overrides.pop("slot")
            if "slot" in overrides
            else PanelSlot.objects.create(key="AM", name="Morning", order=1)
        )
        duration = (
            overrides.pop("duration")
            if "duration" in overrides
            else PanelDuration.objects.create(key="30", name="30 Minutes", order=1)
        )

        payload = {
            "email": "panelist@example.com",
            "legal_name": "Panelist Legal",
            "fan_name": "Panelist Fan",
            "phone_number": "555-123-4567",
            "twitter_handle": "panelist",
            "telegram_handle": "panelist",
            "panelist_bio": "Bio text",
            "panel_name": "Awesome Panel",
            "panel_description": "Description text",
            "panel_duration": duration.key,
            "equipment_needs": "Projector",
            "mature_content": "on",
            "panel_day": [day.key],
            "panel_times": [slot.key],
            "check_ids": "on",
            "captcha_0": "test-captcha-key",
            "captcha_1": "passed",
        }
        payload.update(overrides)
        return payload

    def test_index_renders_with_event(self):
        response = self.client.get(reverse("panels:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "panels.html")
        self.assertTrue(response.context["is_panels"])
        self.assertEqual(response.context["event"], self.event)
        self.assertContains(response, "<strong>content</strong>", html=True)
        self.assertContains(response, reverse("panels:apply"))

    def test_index_hides_apply_button_when_submissions_closed(self):
        self.event.submissions_end = datetime.date.today() - datetime.timedelta(days=1)
        self.event.save(update_fields=["submissions_end"])

        response = self.client.get(reverse("panels:index"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse("panels:apply"))

    def test_index_hides_apply_button_when_module_disabled(self):
        self.event.module_panels_enabled = False
        self.event.save(update_fields=["module_panels_enabled"])

        response = self.client.get(reverse("panels:index"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse("panels:apply"))

    def test_apply_renders_form(self):
        response = self.client.get(reverse("panels:apply"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "panels-apply.html")
        self.assertTrue(response.context["is_panels"])
        self.assertEqual(response.context["event"], self.event)
        self.assertIsInstance(response.context["form"], PanelForm)
        self.assertContains(response, "<em>content</em>", html=True)
        self.assertContains(response, 'action="%s"' % reverse("panels:new"))

    def test_apply_hides_form_when_module_disabled(self):
        self.event.module_panels_enabled = False
        self.event.save(update_fields=["module_panels_enabled"])

        response = self.client.get(reverse("panels:apply"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "panels-apply.html")
        self.assertNotContains(response, "<form", html=False)
        self.assertContains(response, "Sorry Applictions for Panels are currently closed.")

    @override_settings(PANEL_EMAIL="panels@example.com")
    @patch("captcha.fields.settings.CAPTCHA_TEST_MODE", True)
    @patch("panels.views.send_paw_email_new")
    def test_new_creates_panel_and_redirects(self, send_paw_email_new):
        day = DaysAvailable.objects.create(
            key="FRI",
            name="Friday",
            order=1,
            available_scheduling=True,
            party_only=False,
        )
        slot = PanelSlot.objects.create(key="AM", name="Morning", order=1)
        duration = PanelDuration.objects.create(key="30", name="30 Minutes", order=1)

        payload = self.build_valid_payload(day=day, slot=slot, duration=duration)

        response = self.client.post(reverse("panels:new"), data=payload)

        self.assertRedirects(response, reverse("panels:confirm"))
        self.assertEqual(Panel.objects.count(), 1)

        panel = Panel.objects.get()
        self.assertEqual(panel.event, self.event)
        self.assertEqual(panel.panel_name, payload["panel_name"])
        self.assertEqual(panel.email, payload["email"])
        self.assertEqual(list(panel.panel_day.all()), [day])
        self.assertEqual(list(panel.panel_times.all()), [slot])

        send_paw_email_new.assert_called_once()
        args, kwargs = send_paw_email_new.call_args
        self.assertEqual(args[0], "Submit email content")
        self.assertEqual(kwargs["subject"], "PAWCon Panel Submission")
        self.assertEqual(kwargs["recipient_list"], [payload["email"]])
        self.assertEqual(kwargs["reply_to"], "panels@example.com")

    @patch("panels.views.send_paw_email_new")
    def test_new_invalid_captcha_renders_error_without_sending_email(self, send_paw_email_new):
        payload = self.build_valid_payload(captcha_1="not-right")

        response = self.client.post(reverse("panels:new"), data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "panels-apply.html")
        self.assertEqual(Panel.objects.count(), 0)
        self.assertFormError(response.context["form"], "captcha", "Invalid CAPTCHA")
        send_paw_email_new.assert_not_called()

    @patch("panels.views.send_paw_email_new")
    def test_new_rejects_party_only_day_choice(self, send_paw_email_new):
        invalid_day = DaysAvailable.objects.create(
            key="PRTY",
            name="Party Only",
            order=1,
            available_scheduling=True,
            party_only=True,
        )
        slot = PanelSlot.objects.create(key="AM", name="Morning", order=1)
        duration = PanelDuration.objects.create(key="30", name="30 Minutes", order=1)
        payload = self.build_valid_payload(
            day=invalid_day,
            slot=slot,
            duration=duration,
            panel_day=[invalid_day.key],
            captcha_1="not-right",
        )

        response = self.client.post(reverse("panels:new"), data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "panels-apply.html")
        self.assertEqual(Panel.objects.count(), 0)
        self.assertFormError(
            response.context["form"],
            "panel_day",
            "Select a valid choice. PRTY is not one of the available choices.",
        )
        send_paw_email_new.assert_not_called()

    @patch("panels.views.send_paw_email_new")
    def test_new_rejects_unschedulable_day_choice(self, send_paw_email_new):
        invalid_day = DaysAvailable.objects.create(
            key="MON",
            name="Monday",
            order=1,
            available_scheduling=False,
            party_only=False,
        )
        payload = self.build_valid_payload(day=invalid_day, panel_day=[invalid_day.key], captcha_1="not-right")

        response = self.client.post(reverse("panels:new"), data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "panels-apply.html")
        self.assertEqual(Panel.objects.count(), 0)
        self.assertFormError(
            response.context["form"],
            "panel_day",
            "Select a valid choice. MON is not one of the available choices.",
        )
        send_paw_email_new.assert_not_called()

    def test_new_invalid_form_renders_errors(self):
        response = self.client.post(reverse("panels:new"), data={})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "panels-apply.html")
        self.assertEqual(Panel.objects.count(), 0)
        self.assertTrue(response.context["form"].errors)

    def test_confirm_renders_confirmation_content(self):
        response = self.client.get(reverse("panels:confirm"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "panels-confirm.html")
        self.assertContains(response, "<em>content</em>", html=True)


class PanelFormTests(TestCase):
    def test_form_queryset_filters_and_orders_days(self):
        DaysAvailable.objects.create(
            key="SUN",
            name="Sunday",
            order=2,
            available_scheduling=True,
            party_only=False,
        )
        DaysAvailable.objects.create(
            key="FRI",
            name="Friday",
            order=1,
            available_scheduling=True,
            party_only=False,
        )
        DaysAvailable.objects.create(
            key="PRTY",
            name="Party Only",
            order=0,
            available_scheduling=True,
            party_only=True,
        )

        form = PanelForm()

        self.assertEqual(
            list(form.fields["panel_day"].queryset.values_list("key", flat=True)),
            ["FRI", "SUN"],
        )

    def test_form_queryset_orders_duration_and_slots(self):
        PanelDuration.objects.create(key="60", name="60 Minutes", order=2)
        PanelDuration.objects.create(key="30", name="30 Minutes", order=1)
        PanelSlot.objects.create(key="PM", name="Afternoon", order=2)
        PanelSlot.objects.create(key="AM", name="Morning", order=1)

        form = PanelForm()

        self.assertEqual(
            list(form.fields["panel_duration"].queryset.values_list("key", flat=True)),
            ["30", "60"],
        )
        self.assertEqual(
            list(form.fields["panel_times"].queryset.values_list("key", flat=True)),
            ["AM", "PM"],
        )

    def test_form_rejects_party_only_day_selection(self):
        invalid_day = DaysAvailable.objects.create(
            key="PRTY",
            name="Party Only",
            order=1,
            available_scheduling=True,
            party_only=True,
        )
        slot = PanelSlot.objects.create(key="AM", name="Morning", order=1)
        duration = PanelDuration.objects.create(key="30", name="30 Minutes", order=1)

        form = PanelForm(
            data={
                "email": "panelist@example.com",
                "legal_name": "Panelist Legal",
                "fan_name": "Panelist Fan",
                "phone_number": "555-123-4567",
                "twitter_handle": "panelist",
                "telegram_handle": "panelist",
                "panelist_bio": "Bio text",
                "panel_name": "Awesome Panel",
                "panel_description": "Description text",
                "panel_duration": duration.key,
                "equipment_needs": "Projector",
                "mature_content": "on",
                "panel_day": [invalid_day.key],
                "panel_times": [slot.key],
                "check_ids": "on",
                "captcha_0": "test-captcha-key",
                "captcha_1": "not-right",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("panel_day", form.errors)


class PanelModelTests(TestCase):
    def test_panel_str(self):
        event = Event.objects.create(
            event_name="PAWCon",
            event_start=datetime.date.today(),
            event_end=datetime.date.today() + datetime.timedelta(days=1),
            submissions_end=datetime.date.today(),
        )
        duration = PanelDuration.objects.create(key="30", name="30 Minutes", order=1)

        panel = Panel.objects.create(
            event=event,
            email="panelist@example.com",
            legal_name="Legal Name",
            fan_name="Fan Name",
            phone_number="555-555-5555",
            twitter_handle="panelist",
            telegram_handle="panelist",
            panelist_bio="Bio",
            panel_name="Panel Name",
            panel_description="Description",
            panel_duration=duration,
            equipment_needs="None",
            mature_content=False,
            check_ids=False,
        )

        self.assertEqual(str(panel), "Panel Name (Legal Name)")
