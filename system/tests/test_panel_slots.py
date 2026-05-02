from django.urls import reverse

from panels.models import PanelSlot

from .base import SystemViewsTestCase


class PanelSlotViewsTests(SystemViewsTestCase):
    def test_panel_slot_views_are_ordered_and_support_crud(self):
        first = PanelSlot.objects.create(key="AM", name="Morning", order=1)
        second = PanelSlot.objects.create(key="PM", name="Evening", order=2)

        response = self.client.get(reverse("system:slot-list"))

        self.assertEqual(list(response.context["slots"]), [first, second])

        create_response = self.client.post(
            reverse("system:slot-create"),
            {"key": "NT", "name": "Night", "order": 3},
        )

        created = PanelSlot.objects.get(pk="NT")
        self.assertRedirects(
            create_response,
            reverse("system:slot-edit", args=[created.pk]),
        )

        edit_response = self.client.post(
            reverse("system:slot-edit", args=[first.pk]),
            {"name": "Early Morning", "order": 4},
        )

        first.refresh_from_db()
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(first.name, "Early Morning")

        delete_response = self.client.get(reverse("system:slot-delete", args=[second.pk]))

        second.refresh_from_db()
        self.assertRedirects(delete_response, reverse("system:slot-list"))
        self.assertTrue(second.deleted)
        self.assertNotIn(
            second,
            self.client.get(reverse("system:slot-list")).context["slots"],
        )

    def test_panel_slot_invalid_posts_rerender_without_saving(self):
        slot = PanelSlot.objects.create(key="AM", name="Morning", order=1)

        invalid_cases = [
            (
                reverse("system:slot-create"),
                {"key": "", "name": "Broken", "order": 2},
            ),
            (
                reverse("system:slot-edit", args=[slot.pk]),
                {"name": "", "order": 2},
            ),
        ]

        for url, data in invalid_cases:
            with self.subTest(url=url):
                response = self.client.post(url, data)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)

        slot.refresh_from_db()
        self.assertEqual(slot.name, "Morning")
