from django.test import TestCase
from core.models import ApplicationState, DaysAvailable, Event
from partyfloor.models import PartyHost
from django.utils import timezone
import datetime

class PartyHostTest(TestCase):

    # Setting up event and party host objects to test on.
    def setUp(self):
        
        # Initializing event because the PartyHost object needs an associated event.
        # Only necessary parameters provided.
        self.Event = Event.objects.create(
            event_name = "George Washington's Eagle Pride Party",
            event_start = datetime.date(datetime.MAXYEAR, 1, 2),
            event_end = datetime.date(datetime.MAXYEAR, 1, 3),
            submissions_end = datetime.date(datetime.MAXYEAR, 1, 2)
        )
        
        # Initializing PartyHost object for testing here.
        # Only necessary parameters provided.
        self.PartyHost = PartyHost.objects.create(
            event = self.Event,
            created_at = datetime.date(datetime.MAXYEAR, 1, 1) + " " + timezone.now().time(),
            email = "comments@whitehouse.gov",
            legal_name = "George Washington",
            fan_name = "Bald Eagle",
            phone_number = "202-456-1111",
            twitter_handle = "@whitehouse",
            telegram_handle = "@whitehouse",
            hotel_primary = "George Washington Hotel",
            hotel_ack_num = "1776",
            party_days = DaysAvailable.objects.filter(available_party=True).order_by('order'),
            room_number = 1776,
            state_changed = datetime.date(datetime.MAXYEAR, 1, 1)
        )

    # Test to verify that the information that the party host was created with is still the same.
    def test_partyhost_creation(self):

        # This may need to be changed, unable to test due to DATABASE errors.
        saved_partyhost = PartyHost.objects.get(pk=self.PartyHost.room_number)

        # Verifies that several PartyHost values are the same as how they were when first created.
        self.assertEqual(saved_partyhost.event, self.Event)
        self.assertEqual(saved_partyhost.legal_name, "George Washington")
        self.assertEqual(saved_partyhost.fan_name, "Bald Eagle")
        self.assertEqual(saved_partyhost.hotel_primary, "George Washington Hotel")
        self.assertEqual(saved_partyhost.room_number, 1776)
