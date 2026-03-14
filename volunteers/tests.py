import datetime
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import DaysAvailable, Department, Event
from volunteers.forms import VolunteerForm
from volunteers.models import TimesAvailable, Volunteer, VolunteerTask


class VolunteerViewsTests(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.event = Event.objects.create(
            event_name="Test Event",
            event_start=today,
            event_end=today + datetime.timedelta(days=1),
            submissions_end=today + datetime.timedelta(days=1),
        )
        self.department = Department.objects.create(
            department_name="Ops",
            description="Ops Department",
            order=1,
        )
        self.day = DaysAvailable.objects.create(
            key="FRI",
            name="Friday",
            order=1,
            party_only=False,
        )
        self.time = TimesAvailable.objects.create(
            key="AM",
            name="Morning",
            order=1,
        )

    def _valid_post_data(self, **overrides):
        data = {
            "email": "volunteer@example.com",
            "legal_name": "Legal Name",
            "fan_name": "Fan Name",
            "phone_number": "555-0100",
            "twitter_handle": "handle",
            "telegram_handle": "telehandle",
            "department_interest": [self.department.id],
            "volunteer_history": "Some history",
            "special_skills": "Some skills",
            "days_available": [self.day.key],
            "time_availble": [self.time.key],
            "avail_setup": True,
            "avail_teardown": False,
        }
        data.update(overrides)
        return data

    def test_index_view_renders(self):
        response = self.client.get(reverse("volunteers:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "volunteers.html")
        self.assertEqual(response.context["event"], self.event)
        self.assertTrue(response.context["is_volunteers"])

    def test_apply_view_renders(self):
        response = self.client.get(reverse("volunteers:apply"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "volunteer-apply.html")
        self.assertIn("form", response.context)

    @override_settings(VOLUNTEER_EMAIL="volunteer@example.com")
    @mock.patch("volunteers.views.send_paw_email")
    def test_new_view_creates_volunteer_and_redirects(self, send_paw_email):
        response = self.client.post(reverse("volunteers:new"), data=self._valid_post_data())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("volunteers:confirm"))

        volunteer = Volunteer.objects.get(email="volunteer@example.com", event=self.event)
        self.assertEqual(volunteer.legal_name, "Legal Name")
        self.assertEqual(list(volunteer.department_interest.all()), [self.department])
        self.assertEqual(list(volunteer.days_available.all()), [self.day])
        self.assertEqual(list(volunteer.time_availble.all()), [self.time])

        send_paw_email.assert_called_once()

    def test_new_view_invalid_rerenders(self):
        response = self.client.post(
            reverse("volunteers:new"),
            data=self._valid_post_data(email=""),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "volunteer-apply.html")
        self.assertIn("form", response.context)

    def test_confirm_view_renders(self):
        response = self.client.get(reverse("volunteers:confirm"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "volunteer-confirm.html")


class VolunteerFormTests(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.event = Event.objects.create(
            event_name="Test Event",
            event_start=today,
            event_end=today + datetime.timedelta(days=1),
            submissions_end=today + datetime.timedelta(days=1),
        )
        self.department = Department.objects.create(
            department_name="Ops",
            description="Ops Department",
            order=1,
        )
        self.day = DaysAvailable.objects.create(
            key="SAT",
            name="Saturday",
            order=1,
            party_only=False,
        )
        self.time = TimesAvailable.objects.create(
            key="PM",
            name="Afternoon",
            order=1,
        )

    def _valid_form_data(self, **overrides):
        data = {
            "email": "dup@example.com",
            "legal_name": "Legal Name",
            "fan_name": "Fan Name",
            "phone_number": "555-0101",
            "twitter_handle": "handle",
            "telegram_handle": "telehandle",
            "department_interest": [self.department.id],
            "volunteer_history": "History",
            "special_skills": "Skills",
            "days_available": [self.day.key],
            "time_availble": [self.time.key],
            "avail_setup": True,
            "avail_teardown": False,
        }
        data.update(overrides)
        return data

    def test_clean_email_rejects_duplicate_for_current_event(self):
        Volunteer.objects.create(
            event=self.event,
            email="dup@example.com",
            legal_name="Existing",
            fan_name="Existing",
            phone_number="555-0102",
            twitter_handle="existing",
            telegram_handle="existing",
            volunteer_history="",
            special_skills="",
            avail_setup=False,
            avail_teardown=False,
        )
        form = VolunteerForm(data=self._valid_form_data())
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class VolunteerTaskModelTests(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.event = Event.objects.create(
            event_name="Test Event",
            event_start=today,
            event_end=today + datetime.timedelta(days=1),
            submissions_end=today + datetime.timedelta(days=1),
        )
        self.volunteer = Volunteer.objects.create(
            event=self.event,
            email="tasker@example.com",
            legal_name="Tasker",
            fan_name="Tasker",
            phone_number="555-0103",
            twitter_handle="tasker",
            telegram_handle="tasker",
            volunteer_history="",
            special_skills="",
            avail_setup=False,
            avail_teardown=False,
        )
        self.staff_user = self._create_user()

    def _create_user(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.create_user(username="staff", email="staff@example.com", password="testpass")

    def test_task_hours_without_end(self):
        task = VolunteerTask.objects.create(
            event=self.event,
            volunteer=self.volunteer,
            recorded_by=self.staff_user,
            task_name="Setup",
            task_start=datetime.datetime(2026, 1, 1, 9, 0, 0),
        )
        self.assertEqual(task.task_hours(), datetime.timedelta(seconds=0))

    def test_effective_hours_with_multiplier(self):
        task = VolunteerTask.objects.create(
            event=self.event,
            volunteer=self.volunteer,
            recorded_by=self.staff_user,
            task_name="Teardown",
            task_start=datetime.datetime(2026, 1, 1, 9, 0, 0),
            task_end=datetime.datetime(2026, 1, 1, 11, 0, 0),
            task_multiplier=1.5,
        )
        self.assertEqual(task.task_hours(), datetime.timedelta(hours=2))
        self.assertEqual(task.effective_hours(), datetime.timedelta(hours=3))
