from unittest.mock import patch

from django.urls import reverse

from core.models import ApplicationState
from dancecomp.models import Competitor

from .base import ConsoleViewBase


class ConsoleCompetitorViewsTests(ConsoleViewBase):
    def setUp(self):
        super().setUp()
        self.competitor = Competitor.objects.create(
            event=self.event,
            email="competitor@example.com",
            legal_name="Legal Name",
            fan_name="Fan Name",
            competitor_name="Comp",
            phone_number="555-0106",
            twitter_handle="handle",
            telegram_handle="telegram",
            competitor_state=ApplicationState.STATE_NEW,
        )

    def test_competitors_list_view_renders(self):
        response = self.client.get(reverse("console:competitors"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console-competitors-list.html")
        self.assertIn(self.competitor, response.context["new_competitors"])

    def test_competitor_detail_view_renders(self):
        response = self.client.get(
            reverse("console:competitor-detail", args=[self.competitor.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console-competitor-detail.html")
        self.assertEqual(response.context["competitor"], self.competitor)

    @patch("console.views.competitors.send_paw_email")
    def test_competitor_accept_updates_state(self, mock_send):
        response = self.client.get(
            reverse("console:competitor-accept", args=[self.competitor.id])
        )

        self.assertEqual(response.status_code, 302)
        self.competitor.refresh_from_db()
        self.assertEqual(self.competitor.competitor_state, ApplicationState.STATE_ACCEPTED)
        mock_send.assert_called_once()

    @patch("console.views.competitors.send_paw_email")
    def test_competitor_decline_updates_state(self, mock_send):
        response = self.client.get(
            reverse("console:competitor-decline", args=[self.competitor.id])
        )

        self.assertEqual(response.status_code, 302)
        self.competitor.refresh_from_db()
        self.assertEqual(self.competitor.competitor_state, ApplicationState.STATE_DENIED)
        mock_send.assert_called_once()

    def test_competitor_delete_updates_state(self):
        response = self.client.get(
            reverse("console:competitor-delete", args=[self.competitor.id])
        )

        self.assertEqual(response.status_code, 302)
        self.competitor.refresh_from_db()
        self.assertEqual(self.competitor.competitor_state, ApplicationState.STATE_DELETED)
