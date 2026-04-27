from django.urls import reverse

from volunteers.models import TimesAvailable

from .base import SystemViewsTestCase


class TimesAvailableViewsTests(SystemViewsTestCase):
    def test_times_available_views_are_ordered_and_support_crud(self):
        first = TimesAvailable.objects.create(key="MORN", name="Morning", order=1)
        second = TimesAvailable.objects.create(key="EVE", name="Evening", order=2)

        response = self.client.get(reverse("system:times-list"))

        self.assertEqual(list(response.context["times_available"]), [first, second])

        create_response = self.client.post(
            reverse("system:times-create"),
            {"key": "NITE", "name": "Night", "order": 3},
        )

        created = TimesAvailable.objects.get(pk="NITE")
        self.assertRedirects(
            create_response,
            reverse("system:times-edit", args=[created.pk]),
        )

        edit_response = self.client.post(
            reverse("system:times-edit", args=[first.pk]),
            {"name": "Early", "order": 8},
        )

        first.refresh_from_db()
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(first.name, "Early")
        self.assertEqual(first.order, 8)

        delete_response = self.client.get(
            reverse("system:times-delete", args=[second.pk])
        )

        self.assertRedirects(delete_response, reverse("system:times-list"))
        self.assertFalse(TimesAvailable.objects.filter(pk=second.pk).exists())

    def test_times_available_invalid_posts_rerender_without_saving(self):
        time = TimesAvailable.objects.create(key="MORN", name="Morning", order=1)

        invalid_cases = [
            (
                reverse("system:times-create"),
                {"key": "", "name": "Broken", "order": 2},
            ),
            (
                reverse("system:times-edit", args=[time.pk]),
                {"name": "", "order": 2},
            ),
        ]

        for url, data in invalid_cases:
            with self.subTest(url=url):
                response = self.client.post(url, data)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)

        time.refresh_from_db()
        self.assertEqual(time.name, "Morning")
