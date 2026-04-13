import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import DaysAvailable, Department, Event
from volunteers.models import TimesAvailable, VolunteerContent
from performers.models import PerformerContent
from partyfloor.models import PartyHostContent
from panels.models import PanelContent


class ConsoleViewBase(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.event = Event.objects.create(
            event_name="Test Event",
            event_start=today,
            event_end=today + datetime.timedelta(days=2),
            submissions_end=today + datetime.timedelta(days=1),
            max_merchants=25,
        )
        self.user = get_user_model().objects.create_superuser(
            username="console-admin",
            email="console-admin@example.com",
            password="secret-pass",
        )
        self.client.force_login(self.user)
        self.day = DaysAvailable.objects.create(
            key="DAY1",
            name="Day 1",
            order=1,
            available_scheduling=True,
        )
        self.department = Department.objects.create(
            department_name="Ops",
            description="Operations",
            order=1,
        )
        self.time_slot = TimesAvailable.objects.create(
            key="AM01",
            name="Morning",
            order=1,
        )
        PerformerContent.objects.create(
            card_title="Performer Card",
            card_body="Card body",
            card_cta="Apply now",
            page_interstitial="Interstitial content",
            page_apply="Apply content",
            page_confirmation="Confirmation content",
            email_submit="Submit email content",
            email_accepted="Accepted email content",
            email_declined="Declined email content",
            email_waitlisted="Waitlisted email content",
            email_assigned="Assigned email content",
        )
        PartyHostContent.objects.create(
            card_title="Party Host Card",
            card_body="Card body",
            card_cta="Apply now",
            page_interstitial="Interstitial content",
            page_apply="Apply content",
            page_confirmation="Confirmation content",
            email_submit="Submit email content",
            email_accepted="Accepted email content",
            email_declined="Declined email content",
            email_waitlisted="Waitlisted email content",
            email_assigned="Assigned email content",
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
        PanelContent.objects.create(
            card_title="Panel Card",
            card_body="Card body",
            card_cta="Apply now",
            page_interstitial="Interstitial content",
            page_apply="Apply content",
            page_confirmation="Confirmation content",
            email_submit="Submit email content",
            email_accepted="Accepted email content",
            email_declined="Declined email content",
            email_waitlisted="Waitlisted email content",
            email_assigned="Assigned email content",
        )
