from unittest.mock import Mock, patch

from django.urls import reverse

from merchants.models import Merchant, MerchantContent, MerchantState, Table

from .base import ConsoleViewBase


class ConsoleMerchantViewsTests(ConsoleViewBase):
    def setUp(self):
        super().setUp()
        self.full_table = Table.objects.create(key="FULL", name="Full", order=1)
        self.double_table = Table.objects.create(key="DOUB", name="Double", order=2)
        self.merchant = Merchant.objects.create(
            event=self.event,
            email="merchant@example.com",
            legal_name="Legal Name",
            fan_name="Fan Name",
            phone_number="555-0100",
            table_size=self.full_table,
            business_name="Business",
            wares_description="Wares",
            merchant_state=MerchantState.STATE_NEW,
        )
        MerchantContent.objects.create(
            card_title="Merchant Host Card",
            card_body="Card body",
            card_cta="Apply now",
            page_interstitial="Interstitial content",
            page_apply="Apply content",
            page_confirmation="Confirmation content",
            email_submit="Submit email content",
            email_accepted="Accepted email content",
            email_payment_requested="Payment requested email content",
            email_payment_confirmed="Payment confirmed email content",
            email_payment_remind="Payment remind email content",
            email_declined="Declined email content",
            email_waitlisted="Waitlisted email content",
            email_assigned="Assigned email content",
        )

    def test_merchants_list_view_renders(self):
        response = self.client.get(reverse("console:merchants"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console-merchants-list.html")
        self.assertIn(self.merchant, response.context["merchants"])

    def test_merchant_detail_view_renders(self):
        response = self.client.get(
            reverse("console:merchant-detail", args=[self.merchant.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console-merchants-detail.html")
        self.assertEqual(response.context["merchant"], self.merchant)

    def test_merchant_csv_download_excludes_deleted(self):
        deleted = Merchant.objects.create(
            event=self.event,
            email="deleted@example.com",
            legal_name="Deleted",
            fan_name="Deleted",
            phone_number="555-0101",
            table_size=self.full_table,
            business_name="Deleted Biz",
            wares_description="Wares",
            merchant_state=MerchantState.STATE_DELETED,
        )

        response = self.client.get(reverse("console:merchant-download"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/csv"))
        body = response.content.decode("utf-8")
        self.assertIn(self.merchant.business_name, body)
        self.assertNotIn(deleted.business_name, body)

    @patch("console.views.merchants.send_paw_email_new")
    def test_merchant_accept_updates_state(self, mock_send):
        response = self.client.get(
            reverse("console:merchant-accept", args=[self.merchant.id])
        )

        self.assertEqual(response.status_code, 302)
        self.merchant.refresh_from_db()
        self.assertEqual(self.merchant.merchant_state, MerchantState.STATE_ACCEPTED)
        mock_send.assert_called_once()

    @patch("console.views.merchants.send_paw_email_new")
    def test_merchant_payment_request_updates_state(self, mock_send):
        self.merchant.merchant_state = MerchantState.STATE_ACCEPTED
        self.merchant.save()

        response = self.client.get(
            reverse("console:merchant-payment", args=[self.merchant.id])
        )

        self.assertEqual(response.status_code, 302)
        self.merchant.refresh_from_db()
        self.assertEqual(self.merchant.merchant_state, MerchantState.STATE_PAYMENT)
        mock_send.assert_called_once()

    @patch("console.views.merchants.oauth.create_client")
    @patch("console.views.merchants.send_paw_email_new")
    def test_merchant_payment_confirmed_calls_oauth(self, mock_send, mock_client):
        self.merchant.merchant_state = MerchantState.STATE_PAYMENT
        self.merchant.save()

        client = Mock()
        mock_client.return_value = client
        client.fetch_access_token.return_value = "token"
        client.post.return_value.json.return_value = {"data": [{"id": 99}]}
        client.put.return_value = Mock(content=b"ok")

        response = self.client.get(
            reverse("console:merchant-confirm", args=[self.merchant.id])
        )

        self.assertEqual(response.status_code, 302)
        self.merchant.refresh_from_db()
        self.assertEqual(self.merchant.merchant_state, MerchantState.STATE_CONFIRMED)
        mock_send.assert_called_once()
        client.post.assert_called_once()
        client.put.assert_called_once()

    @patch("console.views.merchants.send_paw_email_new")
    def test_merchant_waitlist_updates_state(self, mock_send):
        response = self.client.get(
            reverse("console:merchant-waitlist", args=[self.merchant.id])
        )

        self.assertEqual(response.status_code, 302)
        self.merchant.refresh_from_db()
        self.assertEqual(self.merchant.merchant_state, MerchantState.STATE_WAITLISTED)
        mock_send.assert_called_once()

    def test_merchant_delete_marks_deleted(self):
        response = self.client.get(
            reverse("console:merchant-delete", args=[self.merchant.id])
        )

        self.assertEqual(response.status_code, 302)
        self.merchant.refresh_from_db()
        self.assertEqual(self.merchant.merchant_state, MerchantState.STATE_DELETED)
        self.assertEqual(response["Location"], reverse("console:merchants"))

    @patch("console.views.merchants.send_paw_email_new")
    def test_merchant_assign_table_posts(self, mock_send):
        response = self.client.post(
            reverse("console:merchant-assign", args=[self.merchant.id]),
            data={"table_number": 12},
        )

        self.assertEqual(response.status_code, 302)
        self.merchant.refresh_from_db()
        self.assertEqual(self.merchant.table_number, 12)
        self.assertEqual(self.merchant.merchant_state, MerchantState.STATE_ASSIGNED)
        self.assertEqual(
            response["Location"],
            reverse("console:merchant-detail", args=[self.merchant.id]),
        )
        mock_send.assert_called_once()
