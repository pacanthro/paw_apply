from core.models import Event
from django.db import models

# Create your models her
class Competitor(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    email = models.CharField(max_length=100)
    legal_name = models.CharField(max_length=200)
    fan_name = models.CharField(max_length=200)
    competitor_name = models.CharField(max_length=200,default="")
    phone_number = models.CharField(max_length=15)
    twitter_handle = models.CharField(max_length=30)
    telegram_handle = models.CharField(max_length=30)
    music_url = models.URLField(default="")
    is_group = models.BooleanField(default=False)
    performer_two = models.CharField(max_length=200)
    performer_three = models.CharField(max_length=300)
    performer_four = models.CharField(max_length=300)
    performer_five = models.CharField(max_length=300)
