import datetime
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import DaysAvailable, Event
from panels.forms import PanelForm
from panels.models import Panel, PanelDuration, PanelSlot


class PanelViewsTests(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.event = Event.objects.create(
            event_name="PAWCon",
            event_start=today,
            event_end=today + datetime.timedelta(days=3),
            submissions_end=today,
        )

    def test_index_renders_with_event(self):
        response = self.client.get(reverse("panels:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "panels.html")
        self.assertTrue(response.context["is_panels"])
        self.assertEqual(response.context["event"], self.event)

    def test_apply_renders_form(self):
        response = self.client.get(reverse("panels:apply"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "panels-apply.html")
        self.assertTrue(response.context["is_panels"])
        self.assertEqual(response.context["event"], self.event)
        self.assertIsInstance(response.context["form"], PanelForm)

    @override_settings(PANEL_EMAIL="panels@example.com")
    @patch("panels.views.send_paw_email")
    def test_new_creates_panel_and_redirects(self, send_paw_email):
        day = DaysAvailable.objects.create(
            key="FRI",
            name="Friday",
            order=1,
            available_scheduling=True,
            party_only=False,
        )
        slot = PanelSlot.objects.create(key="AM", name="Morning", order=1)
        duration = PanelDuration.objects.create(key="30", name="30 Minutes", order=1)

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
            "mature_content": True,
            "panel_day": [day.key],
            "panel_times": [slot.key],
            "check_ids": True,
        }

        response = self.client.post(reverse("panels:new"), data=payload)

        self.assertRedirects(response, reverse("panels:confirm"))
        self.assertEqual(Panel.objects.count(), 1)

        panel = Panel.objects.get()
        self.assertEqual(panel.event, self.event)
        self.assertEqual(panel.panel_name, payload["panel_name"])
        self.assertEqual(panel.email, payload["email"])
        self.assertEqual(list(panel.panel_day.all()), [day])
        self.assertEqual(list(panel.panel_times.all()), [slot])

        send_paw_email.assert_called_once()
        args, kwargs = send_paw_email.call_args
        self.assertEqual(args[0], "email-panels-confirm.html")
        self.assertEqual(kwargs["subject"], "PAWCon Panel Submission")
        self.assertEqual(kwargs["recipient_list"], [payload["email"]])
        self.assertEqual(kwargs["reply_to"], "panels@example.com")

    def test_new_invalid_form_renders_errors(self):
        response = self.client.post(reverse("panels:new"), data={})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "panels-apply.html")
        self.assertEqual(Panel.objects.count(), 0)
        self.assertTrue(response.context["form"].errors)


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
