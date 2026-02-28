from core.models import Event
from django.db import models

# Create your models here.
class MerchantState(models.TextChoices):
    STATE_NEW = "STATE_NEW", "New",
    STATE_ACCEPTED = "STATE_ACCEPTED", "Accepted"
    STATE_PAYMENT = "STATE_PAYMENT", "Payment Requested"
    STATE_CONFIRMED = "STATE_CONFIRMED", "Payment Confirmed"
    STATE_ASSIGNED = "STATE_ASSIGNED", "Table Assigned"
    STATE_WAITLISTED = "STATE_WAITLISTED", "Waitlisted"
    STATE_DENIED = "STATE_DENIED", "Denied"
    STATE_DELETED = "STATE_DELETED", "Deleted"
    STATE_OLD = "STATE_OLD", "Migrated Data"

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
    underpaw_interest = models.BooleanField("Interested in underPAW", default=False, help_text="underPAW is PAWCon's Night Market. You Can find information <a href=\"https://pacanthro.org/underpaw\">here</a>")
    helper_legal_name = models.CharField(max_length=200, blank=True)
    helper_fan_name = models.CharField(max_length=200, blank=True)
    special_requests = models.TextField(blank=True)
    table_number = models.IntegerField(null=True, blank=True)
    merchant_state = models.CharField(max_length=20, choices=MerchantState, default=MerchantState.STATE_NEW, null=False)
    state_changed = models.DateField(auto_now_add=True)

    def __str__(self):
        return "{} ({})".format(self.legal_name, self.business_name)
