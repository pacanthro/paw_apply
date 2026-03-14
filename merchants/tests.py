import datetime
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from core.models import Event
from merchants import views as merchant_views
from merchants.forms import MerchantForm
from merchants.models import Merchant, MerchantState, Table


class MerchantTests(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.event = Event.objects.create(
            event_name="Test Event",
            event_start=today,
            event_end=today + datetime.timedelta(days=10),
            submissions_end=today + datetime.timedelta(days=5),
            max_merchants=1,
            module_merchants_enabled=True,
        )
        self.table_full = Table.objects.create(key="FULL", name="Full", order=1, deleted=False)
        self.table_double = Table.objects.create(key="DOUB", name="Double", order=2, deleted=False)

    def _valid_form_data(self, **overrides):
        data = {
            "email": "merchant@example.com",
            "legal_name": "Legal Name",
            "fan_name": "Fan Name",
            "phone_number": "123-456-7890",
            "table_size": self.table_full.pk,
            "business_name": "Business Name",
            "wares_description": "Art and prints",
            "underpaw_interest": False,
            "helper_legal_name": "",
            "helper_fan_name": "",
            "special_requests": "",
        }
        data.update(overrides)
        return data

    def _create_merchant(self, **overrides):
        data = {
            "event": self.event,
            "email": "existing@example.com",
            "legal_name": "Existing Legal",
            "fan_name": "Existing Fan",
            "phone_number": "555-555-5555",
            "table_size": self.table_full,
            "business_name": "Existing Biz",
            "wares_description": "Existing wares",
            "underpaw_interest": False,
            "helper_legal_name": "",
            "helper_fan_name": "",
            "special_requests": "",
        }
        data.update(overrides)
        return Merchant.objects.create(**data)

    def test_form_rejects_duplicate_email(self):
        self._create_merchant(email="dup@example.com")
        form = MerchantForm(data=self._valid_form_data(email="dup@example.com"))

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_accepts_unique_email(self):
        form = MerchantForm(data=self._valid_form_data(email="unique@example.com"))

        self.assertTrue(form.is_valid())

    def test_is_merchants_full_counts_tables_and_excludes_denied_deleted(self):
        self.event.max_merchants = 1
        self.event.save()

        for i in range(10):
            self._create_merchant(email=f"full{i}@example.com", table_size=self.table_full)

        for i in range(6):
            self._create_merchant(email=f"double{i}@example.com", table_size=self.table_double)

        for i in range(3):
            self._create_merchant(
                email=f"denied{i}@example.com",
                table_size=self.table_full,
                merchant_state=MerchantState.STATE_DENIED,
            )

        for i in range(3):
            self._create_merchant(
                email=f"deleted{i}@example.com",
                table_size=self.table_full,
                merchant_state=MerchantState.STATE_DELETED,
            )

        is_merchants_full = merchant_views.__dict__["__is_merchants_full"]
        self.assertTrue(is_merchants_full())

        self.event.max_merchants = 100
        self.event.save()
        self.assertFalse(is_merchants_full())

    def test_denied_deleted_do_not_count_toward_capacity(self):
        self.event.max_merchants = 1
        self.event.save()

        self._create_merchant(
            email="denied@example.com",
            table_size=self.table_full,
            merchant_state=MerchantState.STATE_DENIED,
        )
        self._create_merchant(
            email="deleted@example.com",
            table_size=self.table_double,
            merchant_state=MerchantState.STATE_DELETED,
        )

        is_merchants_full = merchant_views.__dict__["__is_merchants_full"]
        self.assertFalse(is_merchants_full())

    def test_apply_redirects_when_full(self):
        self.event.max_merchants = 0
        self.event.save()

        for i in range(10):
            self._create_merchant(email=f"double{i}@example.com", table_size=self.table_double)

        response = self.client.get(reverse("merchants:apply"))
        self.assertRedirects(response, reverse("merchants:index"))

    @patch("merchants.views.send_paw_email")
    def test_new_creates_merchant_and_sends_email(self, mock_send_email):
        response = self.client.post(reverse("merchants:new"), data=self._valid_form_data())

        self.assertRedirects(response, reverse("merchants:confirm"))
        self.assertEqual(Merchant.objects.count(), 1)
        self.assertEqual(Merchant.objects.first().email, "merchant@example.com")

        mock_send_email.assert_called_once()

    def test_index_renders_template_and_context(self):
        response = self.client.get(reverse("merchants:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "merchants.html")
        self.assertEqual(response.context["event"], self.event)
        self.assertEqual(response.context["merchant_count"], 0)
        self.assertEqual(response.context["max_merchants"], self.event.max_merchants)

    def test_apply_renders_template_when_open(self):
        response = self.client.get(reverse("merchants:apply"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "merch-apply.html")
        self.assertEqual(response.context["event"], self.event)
        self.assertIn("form", response.context)

    def test_confirm_renders_template(self):
        response = self.client.get(reverse("merchants:confirm"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "merch-confirm.html")

    def test_index_with_no_current_event(self):
        self.event.event_end = datetime.date.today() - datetime.timedelta(days=1)
        self.event.save()

        response = self.client.get(reverse("merchants:index"))

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["event"])
        self.assertEqual(response.context["merchant_count"], 0)
        self.assertEqual(response.context["max_merchants"], 0)
