import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import ApplicationState, DaysAvailable, Department, Event
from dancecomp.models import Competitor
from merchants.models import Merchant, MerchantState, Table
from panels.models import Panel, PanelDuration, PanelSlot
from partyfloor.models import PartyHost
from performers.models import Performer
from volunteers.models import TimesAvailable, Volunteer


class ConsoleIndexTests(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.event = Event.objects.create(
            event_name="Test Event",
            event_start=today,
            event_end=today + datetime.timedelta(days=2),
            submissions_end=today + datetime.timedelta(days=1),
            max_merchants=25,
        )
        self.full_table = Table.objects.create(key="FULL", name="Full", order=1)
        self.double_table = Table.objects.create(key="DOUB", name="Double", order=2)
        self.day = DaysAvailable.objects.create(
            key="DAY1",
            name="Day 1",
            order=1,
            available_scheduling=True,
            available_party=True,
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
        self.panel_duration = PanelDuration.objects.create(
            key="60MN",
            name="60 Min",
            order=1,
        )
        self.panel_slot = PanelSlot.objects.create(
            key="AM",
            name="Morning",
            order=1,
        )
        self.user = get_user_model().objects.create_superuser(
            username="console-admin",
            email="console-admin@example.com",
            password="secret-pass",
        )
        self.previous_event = Event.objects.create(
            event_name="Previous Event",
            event_start=today - datetime.timedelta(days=10),
            event_end=today - datetime.timedelta(days=8),
            submissions_end=today - datetime.timedelta(days=12),
            max_merchants=25,
        )

    def _create_merchant(self, *, state, table):
        return Merchant.objects.create(
            event=self.event,
            email=f"{state.lower()}@example.com",
            legal_name="Legal Name",
            fan_name="Fan Name",
            phone_number="555-0100",
            table_size=table,
            business_name="Business",
            wares_description="Wares",
            merchant_state=state,
        )

    def _create_volunteer(self, *, event=None, state=ApplicationState.STATE_NEW, email=None):
        volunteer = Volunteer.objects.create(
            event=event or self.event,
            email=email or f"{state.lower()}-volunteer@example.com",
            legal_name="Volunteer Legal Name",
            fan_name="Volunteer Fan Name",
            phone_number="555-0105",
            twitter_handle="volunteer-handle",
            telegram_handle="volunteer-telegram",
            referred_by="Friend",
            volunteer_history="History",
            special_skills="Skills",
            avail_setup=True,
            avail_teardown=False,
            volunteer_state=state,
        )
        volunteer.department_interest.add(self.department)
        volunteer.days_available.add(self.day)
        volunteer.time_availble.add(self.time_slot)
        return volunteer

    def _create_performer(self, *, event=None, state=ApplicationState.STATE_NEW, email=None):
        return Performer.objects.create(
            event=event or self.event,
            email=email or f"{state.lower()}-performer@example.com",
            legal_name="Performer Legal Name",
            fan_name="Performer Fan Name",
            phone_number="555-0103",
            twitter_handle="performer-handle",
            telegram_handle="performer-telegram",
            biography="Bio",
            dj_history="History",
            set_link="https://example.com/set",
            performer_state=state,
        )

    def _create_host(self, *, event=None, state=ApplicationState.STATE_NEW, email=None, ack_num=None):
        host = PartyHost.objects.create(
            event=event or self.event,
            email=email or f"{state.lower()}-host@example.com",
            legal_name="Host Legal Name",
            fan_name="Host Fan Name",
            phone_number="555-0104",
            twitter_handle="host-handle",
            telegram_handle="host-telegram",
            rbs_certification="cert",
            hotel_primary="Primary",
            hotel_ack_num=ack_num or f"{state}-ACK",
            party_name="Party",
            party_description="Description",
            ack_no_smoking=True,
            ack_amplified_sound=True,
            ack_verify_age=True,
            ack_wristbands=True,
            ack_closure_time=True,
            ack_suspension_policy=True,
            host_state=state,
        )
        host.party_days.add(self.day)
        return host

    def _create_competitor(self, *, event=None, state=ApplicationState.STATE_NEW, email=None):
        return Competitor.objects.create(
            event=event or self.event,
            email=email or f"{state.lower()}-competitor@example.com",
            legal_name="Competitor Legal Name",
            fan_name="Competitor Fan Name",
            competitor_name="Competitor Name",
            phone_number="555-0106",
            twitter_handle="competitor-handle",
            telegram_handle="competitor-telegram",
            competitor_state=state,
        )

    def _create_panel(self, *, event=None, state=ApplicationState.STATE_NEW, email=None):
        panel = Panel.objects.create(
            event=event or self.event,
            email=email or f"{state.lower()}-panel@example.com",
            legal_name="Panel Legal Name",
            fan_name="Panel Fan Name",
            phone_number="555-0102",
            twitter_handle="panel-handle",
            telegram_handle="panel-telegram",
            panelist_bio="Bio",
            panel_name="Panel Name",
            panel_description="Description",
            panel_duration=self.panel_duration,
            equipment_needs="None",
            mature_content=False,
            check_ids=True,
            panel_state=state,
        )
        panel.panel_day.add(self.day)
        panel.panel_times.add(self.panel_slot)
        return panel

    def test_index_requires_login(self):
        response = self.client.get(reverse("console:index"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            f"{reverse('console:login')}?next=/console/",
        )

    def test_index_context_counts_merchants(self):
        self._create_merchant(state=MerchantState.STATE_CONFIRMED, table=self.full_table)
        self._create_merchant(state=MerchantState.STATE_ASSIGNED, table=self.double_table)
        self._create_merchant(state=MerchantState.STATE_DELETED, table=self.full_table)

        self.client.force_login(self.user)
        response = self.client.get(reverse("console:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "console.html")

        merchants = response.context["merchants"]
        self.assertEqual(merchants["applied"], 2)
        self.assertEqual(merchants["tables_count"], 3)
        self.assertEqual(merchants["tables_total"], self.event.max_merchants)

        self.assertEqual(response.context["panel_count"], 0)
        self.assertEqual(response.context["volunteer_count"], 0)
        self.assertEqual(response.context["performer_count"], 0)
        self.assertEqual(response.context["host_count"], 0)
        self.assertEqual(response.context["competitor_count"], 0)

    def test_index_context_counts_current_event_applications_only(self):
        self._create_merchant(state=MerchantState.STATE_NEW, table=self.full_table)
        self._create_merchant(state=MerchantState.STATE_CONFIRMED, table=self.full_table)
        self._create_merchant(state=MerchantState.STATE_ASSIGNED, table=self.double_table)
        Merchant.objects.create(
            event=self.previous_event,
            email="previous-merchant@example.com",
            legal_name="Previous Merchant",
            fan_name="Previous Merchant",
            phone_number="555-1100",
            table_size=self.double_table,
            business_name="Previous Business",
            wares_description="Wares",
            merchant_state=MerchantState.STATE_ASSIGNED,
        )
        self._create_merchant(state=MerchantState.STATE_DELETED, table=self.full_table)

        self._create_panel(state=ApplicationState.STATE_NEW)
        self._create_panel(state=ApplicationState.STATE_ACCEPTED, email="accepted-panel@example.com")
        self._create_panel(
            event=self.previous_event,
            state=ApplicationState.STATE_ACCEPTED,
            email="previous-panel@example.com",
        )
        self._create_panel(
            state=ApplicationState.STATE_DELETED,
            email="deleted-panel@example.com",
        )

        self._create_volunteer(state=ApplicationState.STATE_NEW)
        self._create_volunteer(
            state=ApplicationState.STATE_ACCEPTED,
            email="accepted-volunteer@example.com",
        )
        self._create_volunteer(
            event=self.previous_event,
            state=ApplicationState.STATE_ACCEPTED,
            email="previous-volunteer@example.com",
        )
        self._create_volunteer(
            state=ApplicationState.STATE_DELETED,
            email="deleted-volunteer@example.com",
        )

        self._create_performer(state=ApplicationState.STATE_NEW)
        self._create_performer(
            state=ApplicationState.STATE_WAITLIST,
            email="waitlisted-performer@example.com",
        )
        self._create_performer(
            event=self.previous_event,
            state=ApplicationState.STATE_ACCEPTED,
            email="previous-performer@example.com",
        )
        self._create_performer(
            state=ApplicationState.STATE_DELETED,
            email="deleted-performer@example.com",
        )

        self._create_host(state=ApplicationState.STATE_NEW, ack_num="CURRENT-ACK-1")
        self._create_host(
            state=ApplicationState.STATE_ASSIGNED,
            email="assigned-host@example.com",
            ack_num="CURRENT-ACK-2",
        )
        self._create_host(
            event=self.previous_event,
            state=ApplicationState.STATE_ACCEPTED,
            email="previous-host@example.com",
            ack_num="PREVIOUS-ACK",
        )
        self._create_host(
            state=ApplicationState.STATE_DELETED,
            email="deleted-host@example.com",
            ack_num="DELETED-ACK",
        )

        self._create_competitor(state=ApplicationState.STATE_NEW)
        self._create_competitor(
            state=ApplicationState.STATE_ACCEPTED,
            email="accepted-competitor@example.com",
        )
        self._create_competitor(
            event=self.previous_event,
            state=ApplicationState.STATE_ACCEPTED,
            email="previous-competitor@example.com",
        )
        self._create_competitor(
            state=ApplicationState.STATE_DELETED,
            email="deleted-competitor@example.com",
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("console:index"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["merchants"]["applied"], 3)
        self.assertEqual(response.context["merchants"]["tables_count"], 3)
        self.assertEqual(response.context["panel_count"], 2)
        self.assertEqual(response.context["volunteer_count"], 2)
        self.assertEqual(response.context["performer_count"], 2)
        self.assertEqual(response.context["host_count"], 2)
        self.assertEqual(response.context["competitor_count"], 2)

    def test_logout_redirects_to_core_index(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("console:logout"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("core:index"))
