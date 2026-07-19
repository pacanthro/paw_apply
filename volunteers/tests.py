import datetime
from unittest import mock

from django.test import TestCase, override_settings
from django.utils import timezone
from django.urls import reverse

from core.models import DaysAvailable, Department, Event
from volunteers.forms import VolunteerForm
from volunteers.models import TimesAvailable, Volunteer, VolunteerTask, VolunteerContent


class VolunteerViewsTests(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.event = Event.objects.create(
            event_name="Test Event",
            event_start=today,
            event_end=today + datetime.timedelta(days=1),
            submissions_end=today + datetime.timedelta(days=1),
        )
        VolunteerContent.objects.create(
            card_title="Volunteer Card",
            card_body="Card body",
            card_cta="Apply now",
            page_interstitial="Interstitial content",
            page_apply="Apply content",
            page_confirmation="Confirmation content",
            email_submit="Submit email content",
            email_accepted="Accepted email content",
            email_declined="Declined email content",
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
            "referred_by": "Friend",
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
    @mock.patch("volunteers.views.send_paw_email_new")
    def test_new_view_creates_volunteer_and_redirects(self, send_paw_email_new):
        response = self.client.post(reverse("volunteers:new"), data=self._valid_post_data())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("volunteers:confirm"))

        volunteer = Volunteer.objects.get(email="volunteer@example.com", event=self.event)
        self.assertEqual(volunteer.legal_name, "Legal Name")
        self.assertEqual(volunteer.referred_by, "Friend")
        self.assertEqual(list(volunteer.department_interest.all()), [self.department])
        self.assertEqual(list(volunteer.days_available.all()), [self.day])
        self.assertEqual(list(volunteer.time_availble.all()), [self.time])

        send_paw_email_new.assert_called_once()
        self.assertEqual(send_paw_email_new.call_args.args[0], "Submit email content")
        self.assertEqual(send_paw_email_new.call_args.args[1], {"volunteer": volunteer})
        self.assertEqual(
            send_paw_email_new.call_args.kwargs,
            {
                "subject": "PAWCon Volunteer Application",
                "recipient_list": ["volunteer@example.com"],
                "reply_to": "volunteer@example.com",
            },
        )

    @mock.patch("volunteers.views.send_paw_email_new")
    def test_new_view_invalid_rerenders(self, send_paw_email_new):
        response = self.client.post(
            reverse("volunteers:new"),
            data=self._valid_post_data(email=""),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "volunteer-apply.html")
        self.assertIn("form", response.context)
        self.assertFalse(response.context["form"].is_valid())
        self.assertEqual(Volunteer.objects.count(), 0)
        send_paw_email_new.assert_not_called()

    def test_new_view_rejects_deleted_department(self):
        deleted_department = Department.objects.create(
            department_name="Deleted Ops",
            description="Deleted Department",
            order=2,
            deleted=True,
        )

        response = self.client.post(
            reverse("volunteers:new"),
            data=self._valid_post_data(department_interest=[deleted_department.id]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("department_interest", response.context["form"].errors)
        self.assertEqual(Volunteer.objects.count(), 0)

    def test_new_view_rejects_party_only_day(self):
        party_only_day = DaysAvailable.objects.create(
            key="PARTY",
            name="Party Day",
            order=2,
            party_only=True,
        )

        response = self.client.post(
            reverse("volunteers:new"),
            data=self._valid_post_data(days_available=[party_only_day.key]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("days_available", response.context["form"].errors)
        self.assertEqual(Volunteer.objects.count(), 0)

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
            "referred_by": "Friend",
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
            referred_by="",
            volunteer_history="",
            special_skills="",
            avail_setup=False,
            avail_teardown=False,
        )
        form = VolunteerForm(data=self._valid_form_data())
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_clean_email_allows_duplicate_for_different_event(self):
        previous_event = Event.objects.create(
            event_name="Previous Event",
            event_start=datetime.date.today() - datetime.timedelta(days=10),
            event_end=datetime.date.today() - datetime.timedelta(days=8),
            submissions_end=datetime.date.today() - datetime.timedelta(days=12),
        )
        Volunteer.objects.create(
            event=previous_event,
            email="dup@example.com",
            legal_name="Existing",
            fan_name="Existing",
            phone_number="555-0102",
            twitter_handle="existing",
            telegram_handle="existing",
            referred_by="",
            volunteer_history="",
            special_skills="",
            avail_setup=False,
            avail_teardown=False,
        )

        form = VolunteerForm(data=self._valid_form_data())

        self.assertTrue(form.is_valid(), form.errors)

    def test_form_filters_deleted_departments_and_party_only_days(self):
        deleted_department = Department.objects.create(
            department_name="Deleted Ops",
            description="Deleted Department",
            order=2,
            deleted=True,
        )
        party_only_day = DaysAvailable.objects.create(
            key="PARTY",
            name="Party Day",
            order=2,
            party_only=True,
        )

        form = VolunteerForm()

        self.assertIn(self.department, form.fields["department_interest"].queryset)
        self.assertNotIn(deleted_department, form.fields["department_interest"].queryset)
        self.assertIn(self.day, form.fields["days_available"].queryset)
        self.assertNotIn(party_only_day, form.fields["days_available"].queryset)


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
            referred_by="",
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
            task_start=timezone.make_aware(datetime.datetime(2026, 1, 1, 9, 0, 0)),
        )
        self.assertEqual(task.task_hours(), datetime.timedelta(seconds=0))

    def test_effective_hours_with_multiplier(self):
        task = VolunteerTask.objects.create(
            event=self.event,
            volunteer=self.volunteer,
            recorded_by=self.staff_user,
            task_name="Teardown",
            task_start=timezone.make_aware(datetime.datetime(2026, 1, 1, 9, 0, 0)),
            task_end=timezone.make_aware(datetime.datetime(2026, 1, 1, 11, 0, 0)),
            task_multiplier=1.5,
        )
        self.assertEqual(task.task_hours(), datetime.timedelta(hours=2))
        self.assertEqual(task.effective_hours(), datetime.timedelta(hours=3))
