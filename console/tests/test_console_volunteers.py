from datetime import timedelta
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone

from core.models import ApplicationState
from volunteers.models import Volunteer, VolunteerTask

from .base import ConsoleViewBase


class ConsoleVolunteerViewsTests(ConsoleViewBase):
    def _create_volunteer(self, **overrides):
        data = {
            "event": self.event,
            "email": "volunteer@example.com",
            "legal_name": "Legal Name",
            "fan_name": "Fan Name",
            "phone_number": "555-0105",
            "twitter_handle": "handle",
            "telegram_handle": "telegram",
            "volunteer_history": "History",
            "special_skills": "Skills",
            "avail_setup": True,
            "avail_teardown": False,
            "volunteer_state": ApplicationState.STATE_NEW,
        }
        data.update(overrides)
        volunteer = Volunteer.objects.create(**data)
        volunteer.department_interest.add(self.department)
        volunteer.days_available.add(self.day)
        volunteer.time_availble.add(self.time_slot)
        return volunteer

    def test_volunteers_list_view_renders(self):
        volunteer = self._create_volunteer()

        response = self.client.get(reverse("console:volunteers"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console-volunteers-list.html")
        self.assertIn(volunteer, response.context["volunteers"])

    def test_volunteer_detail_view_renders_with_tasks(self):
        volunteer = self._create_volunteer()
        start = timezone.now() - timedelta(hours=2)
        end = timezone.now() - timedelta(hours=1)
        VolunteerTask.objects.create(
            event=self.event,
            volunteer=volunteer,
            recorded_by=self.user,
            task_name="Task",
            task_notes="Notes",
            task_multiplier=2,
            task_start=start,
            task_end=end,
        )

        response = self.client.get(reverse("console:volunteer-detail", args=[volunteer.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console-volunteers-detail.html")
        self.assertEqual(response.context["volunteer"], volunteer)
        self.assertAlmostEqual(
            response.context["total_hours"].total_seconds(),
            timedelta(hours=2).total_seconds(),
            places=3,
        )

    def test_volunteer_csv_download_includes_header(self):
        self._create_volunteer()

        response = self.client.get(reverse("console:volunteer-download"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/csv"))
        body = response.content.decode("utf-8")
        self.assertIn("Fan Name,Email,Legal Name", body)

    @patch("console.views.volunteers.send_mass_paw_email")
    def test_volunteer_mass_email_sends(self, mock_send):
        self._create_volunteer(email="new@example.com", volunteer_state=ApplicationState.STATE_NEW)
        self._create_volunteer(email="accepted@example.com", volunteer_state=ApplicationState.STATE_ACCEPTED)
        self._create_volunteer(email="denied@example.com", volunteer_state=ApplicationState.STATE_DENIED)

        response = self.client.post(
            reverse("console:volunteer-email"),
            data={
                "volunteer_group": "all",
                "subject": "Update",
                "message": "Hello team",
            },
        )

        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once()
        recipients = mock_send.call_args.kwargs["recipient_list"]
        self.assertEqual(set(recipients), {"new@example.com", "accepted@example.com"})

    @patch("console.views.volunteers.send_paw_email")
    def test_volunteer_accept_updates_state(self, mock_send):
        volunteer = self._create_volunteer()

        response = self.client.get(reverse("console:volunteer-accept", args=[volunteer.id]))

        self.assertEqual(response.status_code, 302)
        volunteer.refresh_from_db()
        self.assertEqual(volunteer.volunteer_state, ApplicationState.STATE_ACCEPTED)
        mock_send.assert_called_once()

    @patch("console.views.volunteers.send_paw_email")
    def test_volunteer_decline_updates_state(self, mock_send):
        volunteer = self._create_volunteer()

        response = self.client.get(reverse("console:volunteer-decline", args=[volunteer.id]))

        self.assertEqual(response.status_code, 302)
        volunteer.refresh_from_db()
        self.assertEqual(volunteer.volunteer_state, ApplicationState.STATE_DENIED)
        mock_send.assert_called_once()

    def test_volunteer_delete_updates_state(self):
        volunteer = self._create_volunteer()

        response = self.client.get(reverse("console:volunteer-delete", args=[volunteer.id]))

        self.assertEqual(response.status_code, 302)
        volunteer.refresh_from_db()
        self.assertEqual(volunteer.volunteer_state, ApplicationState.STATE_DELETED)

    def test_volunteer_dashboard_renders(self):
        active = self._create_volunteer(
            email="active@example.com",
            volunteer_state=ApplicationState.STATE_ACCEPTED,
        )
        idle = self._create_volunteer(
            email="idle@example.com",
            volunteer_state=ApplicationState.STATE_ACCEPTED,
        )
        VolunteerTask.objects.create(
            event=self.event,
            volunteer=active,
            recorded_by=self.user,
            task_name="Active Task",
            task_notes="Notes",
            task_multiplier=1,
            task_start=timezone.now() - timedelta(hours=1),
            task_end=None,
        )

        response = self.client.get(reverse("console:volunteer-dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["active_tasks"]), 1)
        self.assertEqual(len(response.context["idle_volunteers"]), 1)
        self.assertEqual(response.context["idle_volunteers"][0]["model"], idle)

    def test_volunteer_task_start_creates_task(self):
        volunteer = self._create_volunteer(
            email="start@example.com",
            volunteer_state=ApplicationState.STATE_ACCEPTED,
        )

        response = self.client.post(
            reverse("console:volunteer-task-start", args=[volunteer.id]),
            data={
                "event": self.event.id,
                "volunteer": volunteer.id,
                "recorded_by": self.user.id,
                "task_name": "Shift",
                "task_notes": "",
                "task_multiplier": 1,
                "task_start": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(VolunteerTask.objects.filter(volunteer=volunteer).count(), 1)

    def test_volunteer_end_task_view_renders(self):
        volunteer = self._create_volunteer()
        task = VolunteerTask.objects.create(
            event=self.event,
            volunteer=volunteer,
            recorded_by=self.user,
            task_name="Task",
            task_notes="Notes",
            task_multiplier=1,
            task_start=timezone.now() - timedelta(hours=1),
            task_end=None,
        )

        response = self.client.get(
            reverse("console:volunteer-task-end", args=[task.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console-volunteer-end-task.html")
        self.assertEqual(response.context["task"], task)

    def test_volunteer_add_and_edit_task(self):
        volunteer = self._create_volunteer()
        start = timezone.localtime(timezone.now() - timedelta(hours=2))
        end = timezone.localtime(timezone.now() - timedelta(hours=1))

        response = self.client.post(
            reverse("console:volunteer-add-task", args=[volunteer.id]),
            data={
                "event": self.event.id,
                "volunteer": volunteer.id,
                "recorded_by": self.user.id,
                "task_name": "Setup",
                "task_notes": "Notes",
                "task_multiplier": 1,
                "task_start": start.strftime("%Y-%m-%d %H:%M:%S"),
                "task_end": end.strftime("%Y-%m-%d %H:%M:%S"),
            },
        )

        self.assertEqual(response.status_code, 302)
        task = VolunteerTask.objects.get(volunteer=volunteer)

        response = self.client.post(
            reverse("console:volunteer-edit-task", args=[volunteer.id, task.id]),
            data={
                "task_name": "Updated",
                "task_notes": "Updated Notes",
                "task_multiplier": 2,
                "task_start": start.strftime("%Y-%m-%d %H:%M:%S"),
                "task_end": end.strftime("%Y-%m-%d %H:%M:%S"),
            },
        )

        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.task_name, "Updated")
        self.assertEqual(task.task_multiplier, 2)

    def test_volunteer_delete_task(self):
        volunteer = self._create_volunteer()
        task = VolunteerTask.objects.create(
            event=self.event,
            volunteer=volunteer,
            recorded_by=self.user,
            task_name="Task",
            task_notes="Notes",
            task_multiplier=1,
            task_start=timezone.now() - timedelta(hours=1),
            task_end=None,
        )

        response = self.client.get(
            reverse("console:volunteer-delete-task", args=[volunteer.id, task.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(VolunteerTask.objects.filter(id=task.id).exists())
