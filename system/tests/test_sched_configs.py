from django.urls import reverse
from django.utils import timezone

from core.models import DaysAvailable, SchedulingConfig

from .base import SystemViewsTestCase


class SchedulingConfigViewsTests(SystemViewsTestCase):
    def test_sched_config_views_filter_queryset_create_update_and_delete(self):
        allowed_day = DaysAvailable.objects.create(
            key="FRI",
            name="Friday",
            order=1,
            available_scheduling=True,
        )
        blocked_day = DaysAvailable.objects.create(
            key="SAT",
            name="Saturday",
            order=2,
            available_scheduling=False,
        )
        current_config = SchedulingConfig.objects.create(
            event=self.current_event,
            day_available=allowed_day,
            panels_start=self.aware_datetime(2030, 1, 1, 10),
            panels_end=self.aware_datetime(2030, 1, 1, 11),
            performers_start=self.aware_datetime(2030, 1, 1, 12),
            performers_end=self.aware_datetime(2030, 1, 1, 13),
        )
        other_config = SchedulingConfig.objects.create(
            event=self.past_event,
            day_available=allowed_day,
            panels_start=self.aware_datetime(2030, 1, 2, 10),
            panels_end=self.aware_datetime(2030, 1, 2, 11),
            performers_start=self.aware_datetime(2030, 1, 2, 12),
            performers_end=self.aware_datetime(2030, 1, 2, 13),
        )

        list_response = self.client.get(reverse("system:schedconfig-list"))

        self.assertEqual(list(list_response.context["sched_configs"]), [current_config])
        self.assertNotIn(other_config, list_response.context["sched_configs"])

        create_page = self.client.get(reverse("system:schedconfig-create"))
        create_day_choices = list(create_page.context["form"].fields["day_available"].queryset)

        self.assertEqual(create_day_choices, [allowed_day])
        self.assertNotIn(blocked_day, create_day_choices)

        create_response = self.client.post(
            reverse("system:schedconfig-create"),
            {
                "day_available": allowed_day.pk,
                "panels_start": "2030-03-01T09:00",
                "panels_end": "2030-03-01T10:00",
                "performers_start": "2030-03-01T11:00",
                "performers_end": "2030-03-01T12:00",
            },
        )

        created = SchedulingConfig.objects.exclude(pk__in=[current_config.pk, other_config.pk]).get()
        self.assertEqual(created.event, self.current_event)
        self.assertRedirects(
            create_response,
            reverse("system:schedconfig-edit", args=[created.id]),
        )

        invalid_response = self.client.post(
            reverse("system:schedconfig-create"),
            {
                "day_available": "",
                "panels_start": "",
                "panels_end": "",
                "performers_start": "",
                "performers_end": "",
            },
        )

        self.assertEqual(invalid_response.status_code, 200)
        self.assertTrue(invalid_response.context["form"].errors)

        edit_response = self.client.post(
            reverse("system:schedconfig-edit", args=[current_config.id]),
            {
                "panels_start": "2030-01-01T14:00",
                "panels_end": "2030-01-01T15:00",
                "performers_start": "2030-01-01T16:00",
                "performers_end": "2030-01-01T17:00",
            },
        )

        current_config.refresh_from_db()
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(timezone.localtime(current_config.panels_start).hour, 14)
        self.assertEqual(timezone.localtime(current_config.performers_end).hour, 17)

        delete_response = self.client.get(
            reverse("system:schedconfig-delete", args=[current_config.id])
        )

        current_config.refresh_from_db()
        self.assertRedirects(delete_response, reverse("system:schedconfig-list"))
        self.assertTrue(current_config.deleted)
        self.assertNotIn(
            current_config,
            self.client.get(reverse("system:schedconfig-list")).context["sched_configs"],
        )

    def test_sched_config_edit_invalid_post_rerenders_without_saving(self):
        day = DaysAvailable.objects.create(
            key="FRI",
            name="Friday",
            order=1,
            available_scheduling=True,
        )
        config = SchedulingConfig.objects.create(
            event=self.current_event,
            day_available=day,
            panels_start=self.aware_datetime(2030, 1, 1, 10),
            panels_end=self.aware_datetime(2030, 1, 1, 11),
            performers_start=self.aware_datetime(2030, 1, 1, 12),
            performers_end=self.aware_datetime(2030, 1, 1, 13),
        )

        response = self.client.post(
            reverse("system:schedconfig-edit", args=[config.id]),
            {
                "panels_start": "",
                "panels_end": "",
                "performers_start": "",
                "performers_end": "",
            },
        )

        config.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(timezone.localtime(config.panels_start).hour, 10)

    def test_sched_config_create_rejects_end_times_before_or_equal_to_start_times(self):
        day = DaysAvailable.objects.create(
            key="FRI",
            name="Friday",
            order=1,
            available_scheduling=True,
        )

        response = self.client.post(
            reverse("system:schedconfig-create"),
            {
                "day_available": day.pk,
                "panels_start": "2030-03-01T10:00",
                "panels_end": "2030-03-01T10:00",
                "performers_start": "2030-03-01T12:00",
                "performers_end": "2030-03-01T11:00",
            },
        )

        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertIn("panels_end", form.errors)
        self.assertIn("performers_end", form.errors)
        self.assertIn(
            "'Panels End' must be after 'Panels Start'.",
            form.errors["panels_end"],
        )
        self.assertIn(
            "'Performers End' must be after 'Performers Start'",
            form.errors["performers_end"],
        )
        self.assertFalse(
            SchedulingConfig.objects.filter(
                day_available=day,
                event=self.current_event,
            ).exists()
        )

    def test_sched_config_edit_rejects_end_times_before_or_equal_to_start_times(self):
        day = DaysAvailable.objects.create(
            key="FRI",
            name="Friday",
            order=1,
            available_scheduling=True,
        )
        config = SchedulingConfig.objects.create(
            event=self.current_event,
            day_available=day,
            panels_start=self.aware_datetime(2030, 1, 1, 10),
            panels_end=self.aware_datetime(2030, 1, 1, 11),
            performers_start=self.aware_datetime(2030, 1, 1, 12),
            performers_end=self.aware_datetime(2030, 1, 1, 13),
        )

        response = self.client.post(
            reverse("system:schedconfig-edit", args=[config.id]),
            {
                "panels_start": "2030-01-01T10:00",
                "panels_end": "2030-01-01T09:00",
                "performers_start": "2030-01-01T12:00",
                "performers_end": "2030-01-01T12:00",
            },
        )

        config.refresh_from_db()
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertIn("panels_end", form.errors)
        self.assertIn("performers_end", form.errors)
        self.assertEqual(timezone.localtime(config.panels_end).hour, 11)
        self.assertEqual(timezone.localtime(config.performers_end).hour, 13)
