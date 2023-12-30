from core.models import ApplicationState, DaysAvailable, Event
from django.db import models
from django.utils import timezone

# Create your models here.
class PartyHost(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.CharField(max_length=100)
    legal_name = models.CharField(max_length=200)
    fan_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    twitter_handle = models.CharField(max_length=30)
    telegram_handle = models.CharField(max_length=30)
    hotel_primary = models.CharField('Primary Name On Hotel Reservation', max_length=200)
    hotel_ack_num = models.CharField('Hotel Reservation Number', max_length=50, unique=True)
    party_days = models.ManyToManyField(DaysAvailable)
    ack_no_smoking = models.BooleanField('No Smoking of any kind -inside- the room or on the balcony (this includes vapes)', default=False)
    ack_amplified_sound = models.BooleanField('Amplified sound is not allowed on the balcony (inside rooms at reasonable levels is accepted)', default=False)
    ack_verify_age = models.BooleanField('You must check ID\'s before handing out wristbands.', default=False)
    ack_wristbands = models.BooleanField('Only guests with wristbands indicating drinking age may have alcohol', default=False)
    ack_closure_time = models.BooleanField('The party floor closes to the public at 2AM, and normal hotel rules come into effect.', default=False)
    ack_suspension_policy = models.BooleanField('Failure to bide by Con Staff/Hotel Security requests will result in party suspension (zero tolerance)', default=False)
    room_number = models.IntegerField(null=True, blank=True)
    host_state = models.CharField(max_length=20, choices=ApplicationState, default=ApplicationState.STATE_NEW)
    state_changed = models.DateField(auto_now_add=True)

