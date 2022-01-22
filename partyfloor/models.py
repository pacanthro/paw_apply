from core.models import DaysAvailable, Event
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
    hotel_primary = models.CharField(max_length=200)
    hotel_ack_num = models.CharField(max_length=50, unique=True)
    party_days = models.ManyToManyField(DaysAvailable)
    ack_no_smoking = models.BooleanField(default=False)
    ack_amplified_sound = models.BooleanField(default=False)
    ack_verify_age = models.BooleanField(default=False)
    ack_wristbands = models.BooleanField(default=False)
    ack_closure_time = models.BooleanField(default=False)
    ack_suspension_policy = models.BooleanField(default=False)
    room_number = models.IntegerField(null=True, blank=True)
    room_assigned = models.BooleanField(default=False)
    confirmation_sent = models.DateField(null=True, blank=True)
    waitlist_sent = models.DateField(null=True, blank=True)
