from core.models import Event, DaysAvailable, Department
from django.db import models

# Create your models here.
class TimesAvailable(models.Model):
    key = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=20)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Volunteer(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    email = models.CharField(max_length=100,unique=True)
    legal_name = models.CharField(max_length=200)
    fan_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    twitter_handle = models.CharField(max_length=30)
    telegram_handle = models.CharField(max_length=30)
    department_interest = models.ManyToManyField(Department)
    volunteer_history = models.TextField()
    special_skills = models.TextField()
    days_available = models.ManyToManyField(DaysAvailable)
    time_availble = models.ManyToManyField(TimesAvailable)
    avail_setup = models.BooleanField('Available Setup')
    avail_teardown = models.BooleanField('Available Teardown')

    def __str__(self):
        return self.legal_name
