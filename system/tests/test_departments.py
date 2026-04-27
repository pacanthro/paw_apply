from django.urls import reverse

from core.models import Department

from .base import SystemViewsTestCase


class DepartmentViewsTests(SystemViewsTestCase):
    def test_department_views_filter_create_update_and_soft_delete(self):
        visible = Department.objects.create(
            department_name="Ops",
            description="Operations",
            order=1,
        )
        hidden = Department.objects.create(
            department_name="Hidden",
            description="Should not show",
            order=2,
            deleted=True,
        )

        response = self.client.get(reverse("system:departments-list"))

        self.assertEqual(list(response.context["departments"]), [visible])
        self.assertNotIn(hidden, response.context["departments"])

        create_response = self.client.post(
            reverse("system:department-create"),
            {
                "department_name": "Tech",
                "description": "Technology",
                "order": 3,
            },
        )

        created = Department.objects.get(department_name="Tech")
        self.assertRedirects(
            create_response,
            reverse("system:department-edit", args=[created.id]),
        )

        invalid_response = self.client.post(
            reverse("system:department-create"),
            {"department_name": "", "description": "Missing name", "order": 4},
        )

        self.assertEqual(invalid_response.status_code, 200)
        self.assertEqual(Department.objects.filter(description="Missing name").count(), 0)
        self.assertTrue(invalid_response.context["form"].errors)

        edit_response = self.client.post(
            reverse("system:department-edit", args=[visible.id]),
            {
                "department_name": "Operations",
                "description": "Updated",
                "order": 10,
            },
        )

        visible.refresh_from_db()
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(visible.department_name, "Operations")
        self.assertEqual(visible.description, "Updated")
        self.assertEqual(visible.order, 10)

        delete_response = self.client.get(
            reverse("system:department-delete", args=[visible.id])
        )

        visible.refresh_from_db()
        self.assertRedirects(delete_response, reverse("system:departments-list"))
        self.assertTrue(visible.deleted)

    def test_department_edit_invalid_post_rerenders_without_saving(self):
        department = Department.objects.create(
            department_name="Ops",
            description="Operations",
            order=1,
        )

        response = self.client.post(
            reverse("system:department-edit", args=[department.id]),
            {
                "department_name": "",
                "description": "Broken",
                "order": 9,
            },
        )

        department.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(department.department_name, "Ops")
        self.assertEqual(department.description, "Operations")
