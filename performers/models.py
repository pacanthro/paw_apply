from core.models import Event
from django.db import models

# Create your models here.
class Performer(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    email = models.CharField(max_length=100)
    legal_name = models.CharField(max_length=200)
    fan_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    twitter_handle = models.CharField(max_length=30)
    telegram_handle = models.CharField(max_length=30)
    biography = models.TextField()
    dj_history = models.TextField()
    set_link = models.URLField(help_text="Please provide a link to a set of music from your SoundCloud or other similar service (DropBox, Box, YouTube, etc). It should be at least 30 mins in length and showcase your unique style.")
