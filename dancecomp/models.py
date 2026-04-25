from core.models import ApplicationState, Event
from django.db import models

# Create your models her
class Competitor(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    email = models.CharField(max_length=100)
    legal_name = models.CharField(max_length=200)
    fan_name = models.CharField(max_length=200)
    competitor_name = models.CharField(max_length=200,default="")
    phone_number = models.CharField(max_length=15)
    twitter_handle = models.CharField('Twitter/BSky Handle', max_length=30)
    telegram_handle = models.CharField(max_length=30)
    music_url = models.URLField(default="", help_text="Please provide us with a link to the music for your performance. Something like a DropBox or Box link will be fine.")
    is_group = models.BooleanField('Group Performance', default=False, help_text="Check this if you are entering as a group and provide the names of the other competitors below.")
    performer_two = models.CharField(max_length=200, null=True, blank=True)
    performer_three = models.CharField(max_length=300, null=True, blank=True)
    performer_four = models.CharField(max_length=300, null=True, blank=True)
    performer_five = models.CharField(max_length=300, null=True, blank=True)
    competitor_state = models.CharField(max_length=20, null=False, choices=ApplicationState, default=ApplicationState.STATE_NEW)
    state_changed = models.DateField(auto_now_add=True)

class CompetitorContent(models.Model):
    card_title = models.CharField(max_length=100)
    card_body = models.TextField()
    card_cta = models.CharField(max_length=50, verbose_name="Card Call To Action", help_text="Button Text")
    page_interstitial = models.TextField()
    page_apply = models.TextField(verbose_name="Application")
    page_confirmation = models.TextField()
    email_submit = models.TextField()
    email_accepted = models.TextField()
    email_declined = models.TextField()
    email_waitlisted = models.TextField()