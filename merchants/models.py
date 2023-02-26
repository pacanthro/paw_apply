from core.models import Event
from django.db import models

# Create your models here.
class Table(models.Model):
    key = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=20)
    order = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Merchant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    email = models.CharField(max_length=100)
    legal_name = models.CharField(max_length=200)
    fan_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    table_size = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True)
    business_name = models.CharField(max_length=200)
    wares_description = models.TextField('Description of Wares')
    helper_legal_name = models.CharField(max_length=200, blank=True)
    helper_fan_name = models.CharField(max_length=200, blank=True)
    special_requests = models.TextField(blank=True)
    payment_requested = models.BooleanField(null=True, blank=True)
    payment_confirmed = models.BooleanField(null=True, blank=True)
    waitlisted = models.BooleanField(null=True, blank=False)
    email_sent = models.DateField(null=True, blank=True)
    confirmation_sent = models.DateField(null=True, blank=True)
    waitlist_sent = models.DateField(null=True, blank=True)
    table_number = models.IntegerField(null=True, blank=True)
    table_assigned = models.BooleanField(default=False)

    def __str__(self):
        return "{} ({})".format(self.legal_name, self.business_name)
