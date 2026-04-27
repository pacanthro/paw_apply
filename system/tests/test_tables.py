from django.urls import reverse

from merchants.models import Table

from .base import SystemViewsTestCase


class TableViewsTests(SystemViewsTestCase):
    def test_table_views_filter_create_update_and_soft_delete(self):
        visible = Table.objects.create(key="A1", name="Alpha", order=1)
        hidden = Table.objects.create(key="B1", name="Beta", order=2, deleted=True)

        response = self.client.get(reverse("system:tables-list"))

        self.assertEqual(list(response.context["tables"]), [visible])
        self.assertNotIn(hidden, response.context["tables"])

        create_response = self.client.post(
            reverse("system:tables-create"),
            {"key": "C1", "name": "Gamma", "order": 3},
        )

        created = Table.objects.get(pk="C1")
        self.assertRedirects(
            create_response,
            reverse("system:tables-edit", args=[created.pk]),
        )

        edit_response = self.client.post(
            reverse("system:tables-edit", args=[visible.pk]),
            {"name": "Alpha Prime", "order": 10},
        )

        visible.refresh_from_db()
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(visible.name, "Alpha Prime")
        self.assertEqual(visible.order, 10)

        delete_response = self.client.get(
            reverse("system:tables-delete", args=[visible.pk])
        )

        visible.refresh_from_db()
        self.assertRedirects(delete_response, reverse("system:tables-list"))
        self.assertTrue(visible.deleted)

    def test_table_invalid_posts_rerender_without_saving(self):
        table = Table.objects.create(key="A1", name="Alpha", order=1)

        invalid_cases = [
            (
                reverse("system:tables-create"),
                {"key": "", "name": "Broken", "order": 3},
            ),
            (
                reverse("system:tables-edit", args=[table.pk]),
                {"name": "", "order": 4},
            ),
        ]

        for url, data in invalid_cases:
            with self.subTest(url=url):
                response = self.client.post(url, data)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)

        table.refresh_from_db()
        self.assertEqual(table.name, "Alpha")
