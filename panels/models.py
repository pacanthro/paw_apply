from core.models import ApplicationState, Event, DaysAvailable, EventRoom
from django.db import models

# Create your models here.
class PanelDuration(models.Model):
    key = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=20)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class PanelSlot(models.Model):
    key = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=30)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Panel(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    email = models.CharField(max_length=100)
    legal_name = models.CharField(max_length=200)
    fan_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    twitter_handle = models.CharField(max_length=30)
    telegram_handle = models.CharField(max_length=30)
    panelist_bio = models.TextField('Panelist Bio')
    panel_name = models.CharField(max_length=100)
    panel_description = models.TextField()
    panel_duration = models.ForeignKey(PanelDuration, on_delete=models.SET_NULL, null=True)
    equipment_needs = models.TextField()
    mature_content = models.BooleanField('Does your panel contain mature content?')
    panel_day = models.ManyToManyField(DaysAvailable)
    panel_times = models.ManyToManyField(PanelSlot)
    check_ids = models.BooleanField("I Agree to check ID's")
    panel_state = models.CharField(max_length=20, null=False, choices=ApplicationState, default=ApplicationState.STATE_NEW)
    state_changed = models.DateField(auto_now_add=True)
    scheduled_room = models.ForeignKey(EventRoom, on_delete=models.CASCADE, blank=True, null=True)
    scheduled_day = models.ForeignKey(DaysAvailable, on_delete=models.CASCADE, blank=True, null=True, related_name="scheduled_day")
    scheduled_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "{} ({})".format(self.panel_name, self.legal_name)
