import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Event
from merchants.models import Merchant, MerchantState, Table


class ConsoleIndexTests(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.event = Event.objects.create(
            event_name="Test Event",
            event_start=today,
            event_end=today + datetime.timedelta(days=2),
            submissions_end=today + datetime.timedelta(days=1),
            max_merchants=25,
        )
        self.full_table = Table.objects.create(key="FULL", name="Full", order=1)
        self.double_table = Table.objects.create(key="DOUB", name="Double", order=2)
        self.user = get_user_model().objects.create_superuser(
            username="console-admin",
            email="console-admin@example.com",
            password="secret-pass",
        )

    def _create_merchant(self, *, state, table):
        return Merchant.objects.create(
            event=self.event,
            email=f"{state.lower()}@example.com",
            legal_name="Legal Name",
            fan_name="Fan Name",
            phone_number="555-0100",
            table_size=table,
            business_name="Business",
            wares_description="Wares",
            merchant_state=state,
        )

    def test_index_requires_login(self):
        response = self.client.get(reverse("console:index"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            f"{reverse('console:login')}?next=/console/",
        )

    def test_index_context_counts_merchants(self):
        self._create_merchant(state=MerchantState.STATE_CONFIRMED, table=self.full_table)
        self._create_merchant(state=MerchantState.STATE_ASSIGNED, table=self.double_table)
        self._create_merchant(state=MerchantState.STATE_DELETED, table=self.full_table)

        self.client.force_login(self.user)
        response = self.client.get(reverse("console:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console.html")

        merchants = response.context["merchants"]
        self.assertEqual(merchants["applied"], 2)
        self.assertEqual(merchants["tables_count"], 3)
        self.assertEqual(merchants["tables_total"], self.event.max_merchants)

        self.assertEqual(response.context["panel_count"], 0)
        self.assertEqual(response.context["volunteer_count"], 0)
        self.assertEqual(response.context["performer_count"], 0)
        self.assertEqual(response.context["host_count"], 0)
        self.assertEqual(response.context["competitor_count"], 0)

    def test_logout_redirects_to_core_index(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("console:logout"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("core:index"))
