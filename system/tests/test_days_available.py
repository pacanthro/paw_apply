from django.urls import reverse

from core.models import DaysAvailable

from .base import SystemViewsTestCase


class DaysAvailableViewsTests(SystemViewsTestCase):
    def test_days_available_views_create_update_and_delete(self):
        existing = DaysAvailable.objects.create(
            key="THU",
            name="Thursday",
            order=1,
            available_scheduling=True,
            available_party=False,
            party_only=False,
        )

        response = self.client.get(reverse("system:days-list"))

        self.assertEqual(list(response.context["days_available"]), [existing])

        create_response = self.client.post(
            reverse("system:days-create"),
            {
                "key": "SUN",
                "name": "Sunday",
                "order": 2,
                "available_scheduling": "on",
                "available_party": "",
                "party_only": "",
            },
        )

        created = DaysAvailable.objects.get(pk="SUN")
        self.assertRedirects(
            create_response,
            reverse("system:days-edit", args=[created.pk]),
        )

        edit_response = self.client.post(
            reverse("system:days-edit", args=[existing.pk]),
            {
                "name": "Thursday Late",
                "order": 9,
                "available_scheduling": "",
                "available_party": "on",
                "party_only": "on",
            },
        )

        existing.refresh_from_db()
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(existing.name, "Thursday Late")
        self.assertFalse(existing.available_scheduling)
        self.assertTrue(existing.available_party)
        self.assertTrue(existing.party_only)

        delete_response = self.client.get(reverse("system:days-delete", args=[existing.pk]))

        self.assertRedirects(delete_response, reverse("system:days-list"))
        self.assertFalse(DaysAvailable.objects.filter(pk=existing.pk).exists())

    def test_days_available_invalid_posts_rerender_without_saving(self):
        day = DaysAvailable.objects.create(
            key="THU",
            name="Thursday",
            order=1,
            available_scheduling=True,
        )

        invalid_cases = [
            (
                reverse("system:days-create"),
                {"key": "", "name": "Broken", "order": 2},
            ),
            (
                reverse("system:days-edit", args=[day.pk]),
                {"name": "", "order": 2},
            ),
        ]

        for url, data in invalid_cases:
            with self.subTest(url=url):
                response = self.client.post(url, data)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)

        day.refresh_from_db()
        self.assertEqual(day.name, "Thursday")
