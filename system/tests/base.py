import datetime

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone

from core.models import Event


class SystemViewsTestCase(TestCase):
    def setUp(self):
        super().setUp()
        today = datetime.date.today()
        self.factory = RequestFactory()
        self.timezone = timezone.get_current_timezone()
        self.superuser = get_user_model().objects.create_superuser(
            username="root",
            email="root@example.com",
            password="secret-pass",
        )
        self.client.force_login(self.superuser)
        self.current_event = Event.objects.create(
            event_name="Current Event",
            event_start=today,
            event_end=today + datetime.timedelta(days=2),
            submissions_end=today + datetime.timedelta(days=1),
            max_merchants=50,
        )
        self.past_event = Event.objects.create(
            event_name="Past Event",
            event_start=today - datetime.timedelta(days=10),
            event_end=today - datetime.timedelta(days=5),
            submissions_end=today - datetime.timedelta(days=7),
            max_merchants=20,
        )

    def aware_datetime(self, year, month, day, hour, minute=0):
        return timezone.make_aware(
            datetime.datetime(year, month, day, hour, minute),
            self.timezone,
        )
