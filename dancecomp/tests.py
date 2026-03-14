import datetime
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from core.models import ApplicationState, Event
from dancecomp.forms import CompetitorForm
from dancecomp.models import Competitor


class DanceCompViewsTests(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.event = Event.objects.create(
            event_name="PAWCon",
            event_start=today,
            event_end=today + datetime.timedelta(days=3),
            submissions_end=today + datetime.timedelta(days=1),
            max_merchants=0,
            max_party_rooms=0,
            module_panels_enabled=False,
            module_merchants_enabled=False,
            module_performers_enabled=False,
            module_partyfloor_enabled=False,
            module_competitors_enabled=True,
            voucher_performers="",
            voucher_volunteer="",
        )

    def _valid_post_data(self):
        return {
            "email": "competitor@example.com",
            "legal_name": "Legal Name",
            "fan_name": "Fan Name",
            "competitor_name": "Stage Name",
            "phone_number": "555-123-4567",
            "twitter_handle": "",
            "telegram_handle": "",
            "music_url": "https://example.com/music",
            "is_group": False,
            "performer_two": "",
            "performer_three": "",
            "performer_four": "",
            "performer_five": "",
        }

    def test_index_renders_with_event(self):
        response = self.client.get(reverse("dancecomp:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dancecomp.html")
        self.assertEqual(response.context["event"], self.event)
        self.assertTrue(response.context["is_dancecomp"])

    def test_apply_renders_form(self):
        response = self.client.get(reverse("dancecomp:apply"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dancecomp-apply.html")
        self.assertIn("form", response.context)
        self.assertTrue(response.context["is_dancecomp"])

    def test_confirm_renders(self):
        response = self.client.get(reverse("dancecomp:confirm"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dancecomp-confirm.html")
        self.assertEqual(response.context["event"], self.event)
        self.assertTrue(response.context["is_dancecomp"])

    @patch("dancecomp.views.send_paw_email")
    def test_new_creates_competitor_and_redirects(self, mock_send_email):
        response = self.client.post(reverse("dancecomp:new"), data=self._valid_post_data())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dancecomp:confirm"))

        competitor = Competitor.objects.get(email="competitor@example.com")
        self.assertEqual(competitor.event, self.event)
        self.assertEqual(competitor.competitor_state, ApplicationState.STATE_NEW)
        mock_send_email.assert_called_once()

    @patch("dancecomp.views.send_paw_email")
    def test_new_invalid_rerenders_form(self, mock_send_email):
        data = self._valid_post_data()
        data.pop("email")
        response = self.client.post(reverse("dancecomp:new"), data=data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dancecomp-apply.html")
        self.assertEqual(Competitor.objects.count(), 0)
        mock_send_email.assert_not_called()


class CompetitorFormTests(TestCase):
    def test_optional_fields_are_not_required(self):
        form = CompetitorForm(
            data={
                "email": "competitor@example.com",
                "legal_name": "Legal Name",
                "fan_name": "Fan Name",
                "competitor_name": "Stage Name",
                "phone_number": "555-123-4567",
                "twitter_handle": "",
                "telegram_handle": "",
                "music_url": "https://example.com/music",
                "is_group": False,
                "performer_two": "",
                "performer_three": "",
                "performer_four": "",
                "performer_five": "",
            }
        )
        self.assertTrue(form.is_valid())
