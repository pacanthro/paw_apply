from unittest.mock import patch

from django.urls import reverse

from core.models import ApplicationState
from partyfloor.models import PartyHost

from .base import ConsoleViewBase


class ConsolePartyHostViewsTests(ConsoleViewBase):
    def setUp(self):
        super().setUp()
        self.host = PartyHost.objects.create(
            event=self.event,
            email="host@example.com",
            legal_name="Legal Name",
            fan_name="Fan Name",
            phone_number="555-0104",
            twitter_handle="handle",
            telegram_handle="telegram",
            rbs_certification="cert",
            hotel_primary="Primary",
            hotel_ack_num="ACK123",
            party_name="Party",
            party_description="Desc",
            ack_no_smoking=True,
            ack_amplified_sound=True,
            ack_verify_age=True,
            ack_wristbands=True,
            ack_closure_time=True,
            ack_suspension_policy=True,
            host_state=ApplicationState.STATE_NEW,
        )
        self.host.party_days.add(self.day)

    def test_hosts_list_view_renders(self):
        response = self.client.get(reverse("console:hosts"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console-hosts-list.html")
        self.assertIn(self.host, response.context["new_hosts"])

    def test_host_detail_view_renders(self):
        response = self.client.get(reverse("console:host-detail", args=[self.host.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console-host-detail.html")
        self.assertEqual(response.context["host"], self.host)

    @patch("console.views.partyfloor.send_paw_email_new")
    def test_host_accept_updates_state(self, mock_send):
        response = self.client.get(reverse("console:host-accept", args=[self.host.id]))

        self.assertEqual(response.status_code, 302)
        self.host.refresh_from_db()
        self.assertEqual(self.host.host_state, ApplicationState.STATE_ACCEPTED)
        mock_send.assert_called_once()

    @patch("console.views.partyfloor.send_paw_email_new")
    def test_host_waitlist_updates_state(self, mock_send):
        response = self.client.get(reverse("console:host-waitlist", args=[self.host.id]))

        self.assertEqual(response.status_code, 302)
        self.host.refresh_from_db()
        self.assertEqual(self.host.host_state, ApplicationState.STATE_WAITLIST)
        mock_send.assert_called_once()

    @patch("console.views.partyfloor.send_paw_email_new")
    def test_host_decline_updates_state(self, mock_send):
        response = self.client.get(reverse("console:host-decline", args=[self.host.id]))

        self.assertEqual(response.status_code, 302)
        self.host.refresh_from_db()
        self.assertEqual(self.host.host_state, ApplicationState.STATE_DENIED)
        mock_send.assert_called_once()

    def test_host_delete_updates_state(self):
        response = self.client.get(reverse("console:host-delete", args=[self.host.id]))

        self.assertEqual(response.status_code, 302)
        self.host.refresh_from_db()
        self.assertEqual(self.host.host_state, ApplicationState.STATE_DELETED)

    @patch("console.views.partyfloor.send_paw_email_new")
    def test_host_assign_posts(self, mock_send):
        response = self.client.post(
            reverse("console:host-assign", args=[self.host.id]),
            data={"room_number": 1101},
        )

        self.assertEqual(response.status_code, 302)
        self.host.refresh_from_db()
        self.assertEqual(self.host.room_number, 1101)
        self.assertEqual(self.host.host_state, ApplicationState.STATE_ASSIGNED)
        mock_send.assert_called_once()
