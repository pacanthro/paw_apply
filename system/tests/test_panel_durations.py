from django.urls import reverse

from panels.models import PanelDuration

from .base import SystemViewsTestCase


class PanelDurationViewsTests(SystemViewsTestCase):
    def test_panel_duration_views_are_ordered_and_support_crud(self):
        first = PanelDuration.objects.create(key="030", name="30 min", order=1)
        second = PanelDuration.objects.create(key="060", name="60 min", order=2)

        response = self.client.get(reverse("system:duration-list"))

        self.assertEqual(list(response.context["durations"]), [first, second])

        create_response = self.client.post(
            reverse("system:duration-create"),
            {"key": "090", "name": "90 min", "order": 3},
        )

        created = PanelDuration.objects.get(pk="090")
        self.assertRedirects(
            create_response,
            reverse("system:duration-edit", args=[created.pk]),
        )

        edit_response = self.client.post(
            reverse("system:duration-edit", args=[first.pk]),
            {"name": "Half Hour", "order": 5},
        )

        first.refresh_from_db()
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(first.name, "Half Hour")
        self.assertEqual(first.order, 5)

        delete_response = self.client.get(
            reverse("system:duration-delete", args=[second.pk])
        )

        self.assertRedirects(delete_response, reverse("system:slot-list"))
        self.assertFalse(PanelDuration.objects.filter(pk=second.pk).exists())

    def test_panel_duration_invalid_posts_rerender_without_saving(self):
        duration = PanelDuration.objects.create(key="030", name="30 min", order=1)

        invalid_cases = [
            (
                reverse("system:duration-create"),
                {"key": "", "name": "Broken", "order": 2},
            ),
            (
                reverse("system:duration-edit", args=[duration.pk]),
                {"name": "", "order": 2},
            ),
        ]

        for url, data in invalid_cases:
            with self.subTest(url=url):
                response = self.client.post(url, data)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)

        duration.refresh_from_db()
        self.assertEqual(duration.name, "30 min")
