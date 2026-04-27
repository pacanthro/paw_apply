from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import DaysAvailable, Department, EventRoom, SchedulingConfig
from merchants.models import Table
from panels.models import PanelDuration, PanelSlot
from volunteers.models import TimesAvailable

from .base import SystemViewsTestCase


class SystemAccessTests(SystemViewsTestCase):
    def setUp(self):
        super().setUp()
        self.department = Department.objects.create(
            department_name="Ops",
            description="Operations",
            order=1,
        )
        self.room = EventRoom.objects.create(
            event=self.current_event,
            room_name="Main",
            room_type="ROOM_PANELS",
        )
        self.day = DaysAvailable.objects.create(
            key="FRI",
            name="Friday",
            order=1,
            available_scheduling=True,
        )
        self.config = SchedulingConfig.objects.create(
            event=self.current_event,
            day_available=self.day,
            panels_start=self.aware_datetime(2030, 1, 1, 10),
            panels_end=self.aware_datetime(2030, 1, 1, 11),
            performers_start=self.aware_datetime(2030, 1, 1, 12),
            performers_end=self.aware_datetime(2030, 1, 1, 13),
        )
        self.table = Table.objects.create(key="A1", name="Alpha", order=1)
        self.duration = PanelDuration.objects.create(key="030", name="30 min", order=1)
        self.slot = PanelSlot.objects.create(key="AM", name="Morning", order=1)
        self.time = TimesAvailable.objects.create(key="MORN", name="Morning", order=1)

    def system_urls(self):
        return [
            reverse("system:event-index"),
            reverse("system:departments-list"),
            reverse("system:department-edit", args=[self.department.id]),
            reverse("system:department-create"),
            reverse("system:department-delete", args=[self.department.id]),
            reverse("system:rooms-list"),
            reverse("system:rooms-edit", args=[self.room.id]),
            reverse("system:rooms-create"),
            reverse("system:rooms-delete", args=[self.room.id]),
            reverse("system:schedconfig-list"),
            reverse("system:schedconfig-edit", args=[self.config.id]),
            reverse("system:schedconfig-create"),
            reverse("system:schedconfig-delete", args=[self.config.id]),
            reverse("system:tables-list"),
            reverse("system:tables-edit", args=[self.table.pk]),
            reverse("system:tables-create"),
            reverse("system:tables-delete", args=[self.table.pk]),
            reverse("system:days-list"),
            reverse("system:days-edit", args=[self.day.pk]),
            reverse("system:days-create"),
            reverse("system:days-delete", args=[self.day.pk]),
            reverse("system:duration-list"),
            reverse("system:duration-edit", args=[self.duration.pk]),
            reverse("system:duration-create"),
            reverse("system:duration-delete", args=[self.duration.pk]),
            reverse("system:slot-list"),
            reverse("system:slot-edit", args=[self.slot.pk]),
            reverse("system:slot-create"),
            reverse("system:slot-delete", args=[self.slot.pk]),
            reverse("system:times-list"),
            reverse("system:times-edit", args=[self.time.pk]),
            reverse("system:times-create"),
            reverse("system:times-delete", args=[self.time.pk]),
        ]

    def test_all_system_views_redirect_anonymous_users_to_login(self):
        self.client.logout()

        for url in self.system_urls():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(
                    response["Location"],
                    f"{reverse('console:login')}?next={url}",
                )

    def test_all_system_views_forbid_authenticated_non_superusers(self):
        user = get_user_model().objects.create_user(
            username="staffless",
            email="staffless@example.com",
            password="secret-pass",
        )
        self.client.force_login(user)

        for url in self.system_urls():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 403)

    def test_superuser_can_access_system_index(self):
        response = self.client.get(reverse("system:event-index"))

        self.assertEqual(response.status_code, 200)
