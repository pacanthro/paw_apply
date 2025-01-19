from core.models import ApplicationState, Event, DaysAvailable, Department
from django.contrib.auth import get_user_model
from django.db import models

import sys

# Create your models here.
class TimesAvailable(models.Model):
    key = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=20)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Volunteer(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    email = models.CharField(max_length=100)
    legal_name = models.CharField(max_length=200)
    fan_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    twitter_handle = models.CharField('Twitter/BSky Handle', max_length=30)
    telegram_handle = models.CharField(max_length=30)
    department_interest = models.ManyToManyField(Department)
    volunteer_history = models.TextField()
    special_skills = models.TextField()
    days_available = models.ManyToManyField(DaysAvailable)
    time_availble = models.ManyToManyField(TimesAvailable)
    avail_setup = models.BooleanField('Available Setup')
    avail_teardown = models.BooleanField('Available Teardown')
    volunteer_state = models.CharField(max_length=20, choices=ApplicationState, default=ApplicationState.STATE_NEW, null=False)
    state_changed = models.DateField(auto_now_add=True)

    def __str__(self):
        return "{} ({})".format(self.fan_name, self.legal_name)

class VolunteerTask(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    recorded_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    task_name = models.CharField(max_length=200)
    task_notes = models.TextField(blank=True)
    task_multiplier = models.FloatField(default=1)
    task_start = models.DateTimeField()
    task_end = models.DateTimeField(null=True, default=None)
