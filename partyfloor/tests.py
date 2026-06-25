import datetime
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from core.models import ApplicationState, DaysAvailable, Event
from partyfloor.forms import HostForm
from partyfloor.models import PartyHost, PartyHostContent


class PartyfloorTests(TestCase):
    def setUp(self):
        self.today = datetime.date.today()
        self.event = Event.objects.create(
            event_name="Test Event",
            event_start=self.today,
            event_end=self.today + datetime.timedelta(days=30),
            max_merchants=0,
            max_party_rooms=0,
            submissions_end=self.today + datetime.timedelta(days=10),
            module_panels_enabled=False,
            module_merchants_enabled=False,
            module_performers_enabled=False,
            module_partyfloor_enabled=True,
            module_competitors_enabled=False,
            voucher_performers="",
            voucher_volunteer="",
        )
        self.party_day = DaysAvailable.objects.create(
            key="FRI",
            name="Friday",
            order=1,
            available_party=True,
        )
        PartyHostContent.objects.create(
            card_title="Party Host Card",
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

    def _host_payload(self, **overrides):
        payload = {
            "email": "host@example.com",
            "legal_name": "Legal Name",
            "fan_name": "Fan Name",
            "phone_number": "555-0101",
            "twitter_handle": "",
            "telegram_handle": "",
            "rbs_certification": "",
            "hotel_primary": "Primary Name",
            "hotel_ack_num": "RES-123",
            "party_days": [self.party_day.key],
            "party_name": "Party Name",
            "party_description": "Party description.",
            "ack_no_smoking": True,
            "ack_amplified_sound": True,
            "ack_verify_age": True,
            "ack_wristbands": True,
            "ack_closure_time": True,
            "ack_suspension_policy": True,
            "captcha_0": "dummy-value",
            "captcha_1": "PASSED",
        }
        payload.update(overrides)
        return payload

    def _create_host(self, **overrides):
        data = self._host_payload(**overrides)
        host = PartyHost.objects.create(
            event=self.event,
            email=data["email"],
            legal_name=data["legal_name"],
            fan_name=data["fan_name"],
            phone_number=data["phone_number"],
            twitter_handle=data["twitter_handle"] or None,
            telegram_handle=data["telegram_handle"] or None,
            rbs_certification=data["rbs_certification"] or None,
            hotel_primary=data["hotel_primary"],
            hotel_ack_num=data["hotel_ack_num"],
            party_name=data["party_name"] or None,
            party_description=data["party_description"] or None,
            ack_no_smoking=data["ack_no_smoking"],
            ack_amplified_sound=data["ack_amplified_sound"],
            ack_verify_age=data["ack_verify_age"],
            ack_wristbands=data["ack_wristbands"],
            ack_closure_time=data["ack_closure_time"],
            ack_suspension_policy=data["ack_suspension_policy"],
            host_state=overrides.get("host_state", ApplicationState.STATE_NEW),
        )
        host.party_days.add(self.party_day)
        return host

    def test_index_shows_not_full_when_empty(self):
        response = self.client.get(reverse("partyfloor:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partyfloor.html")
        self.assertTrue(response.context["is_partyfloor"])
        self.assertEqual(response.context["event"], self.event)
        self.assertFalse(response.context["is_partyfloor_full"])
        self.assertContains(response, "Interstitial content")

    def test_index_marks_partyfloor_full_at_capacity(self):
        for i in range(5):
            self._create_host(
                email=f"host{i}@example.com",
                hotel_ack_num=f"RES-{i}",
            )

        response = self.client.get(reverse("partyfloor:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_partyfloor_full"])
        self.assertContains(response, "Party Floor is currently full.")

    def test_index_does_not_count_inactive_hosts_toward_capacity(self):
        inactive_states = [
            ApplicationState.STATE_DENIED,
            ApplicationState.STATE_DELETED,
            ApplicationState.STATE_OLD,
        ]
        for i, host_state in enumerate(inactive_states):
            self._create_host(
                email=f"inactive{i}@example.com",
                hotel_ack_num=f"INACTIVE-{i}",
                host_state=host_state,
            )

        response = self.client.get(reverse("partyfloor:index"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["is_partyfloor_full"])

    def test_apply_renders_form_when_partyfloor_open(self):
        response = self.client.get(reverse("partyfloor:apply"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partyfloor-apply.html")
        self.assertTrue(response.context["is_partyfloor"])
        self.assertEqual(response.context["event"], self.event)
        self.assertIsInstance(response.context["form"], HostForm)
        self.assertContains(response, "Apply content")
        self.assertContains(response, 'action="%s"' % reverse("partyfloor:new"))

    def test_apply_hides_form_when_module_disabled(self):
        self.event.module_partyfloor_enabled = False
        self.event.save(update_fields=["module_partyfloor_enabled"])

        response = self.client.get(reverse("partyfloor:apply"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partyfloor-apply.html")
        self.assertNotContains(response, "<form", html=False)
        self.assertContains(response, "Sorry Applictions for the Party Floor are currently closed.")

    def test_apply_redirects_when_partyfloor_full(self):
        for i in range(5):
            self._create_host(
                email=f"host{i}@example.com",
                hotel_ack_num=f"RES-{i}",
            )

        response = self.client.get(reverse("partyfloor:apply"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("partyfloor:index"))

    def test_new_creates_host_sends_email_and_redirects(self):
        payload = self._host_payload()
        with patch("partyfloor.views.send_paw_email_new") as send_email:
            response = self.client.post(reverse("partyfloor:new"), data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("partyfloor:confirm"))
        self.assertEqual(PartyHost.objects.count(), 1)
        host = PartyHost.objects.get()
        self.assertEqual(host.party_days.count(), 1)
        send_email.assert_called_once()

    def test_email_must_be_unique_for_current_event(self):
        self._create_host(email="dupe@example.com", hotel_ack_num="RES-999")
        payload = self._host_payload(email="dupe@example.com", hotel_ack_num="RES-1000")
        with patch("partyfloor.views.send_paw_email_new") as send_email:
            response = self.client.post(reverse("partyfloor:new"), data=payload)

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("Email already exists", form.errors["email"])
        self.assertEqual(PartyHost.objects.count(), 1)
        send_email.assert_not_called()

    def test_email_can_match_past_event_host(self):
        past_event = Event.objects.create(
            event_name="Past Event",
            event_start=self.today - datetime.timedelta(days=60),
            event_end=self.today - datetime.timedelta(days=30),
            max_merchants=0,
            max_party_rooms=0,
            submissions_end=self.today - datetime.timedelta(days=45),
            module_panels_enabled=False,
            module_merchants_enabled=False,
            module_performers_enabled=False,
            module_partyfloor_enabled=True,
            module_competitors_enabled=False,
            voucher_performers="",
            voucher_volunteer="",
        )
        self._create_host(email="returning@example.com", hotel_ack_num="PAST-999")
        PartyHost.objects.filter(email="returning@example.com").update(event=past_event)
        payload = self._host_payload(email="returning@example.com", hotel_ack_num="RES-1000")

        with patch("partyfloor.views.send_paw_email_new") as send_email:
            response = self.client.post(reverse("partyfloor:new"), data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("partyfloor:confirm"))
        self.assertEqual(PartyHost.objects.filter(event=self.event).count(), 1)
        send_email.assert_called_once()

    def test_new_rejects_missing_required_acknowledgement(self):
        payload = self._host_payload()
        payload.pop("ack_no_smoking")

        with patch("partyfloor.views.send_paw_email_new") as send_email:
            response = self.client.post(reverse("partyfloor:new"), data=payload)

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("ack_no_smoking", form.errors)
        self.assertEqual(PartyHost.objects.count(), 0)
        send_email.assert_not_called()

    def test_new_rejects_missing_captcha(self):
        payload = self._host_payload()
        payload.pop("captcha_0")
        payload.pop("captcha_1")

        with patch("partyfloor.views.send_paw_email_new") as send_email:
            response = self.client.post(reverse("partyfloor:new"), data=payload)

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("captcha", form.errors)
        self.assertEqual(PartyHost.objects.count(), 0)
        send_email.assert_not_called()

    def test_new_rejects_unavailable_party_day(self):
        unavailable_day = DaysAvailable.objects.create(
            key="SAT",
            name="Saturday",
            order=2,
            available_party=False,
        )
        payload = self._host_payload(party_days=[unavailable_day.key])

        with patch("partyfloor.views.send_paw_email_new") as send_email:
            response = self.client.post(reverse("partyfloor:new"), data=payload)

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("party_days", form.errors)
        self.assertEqual(PartyHost.objects.count(), 0)
        send_email.assert_not_called()
