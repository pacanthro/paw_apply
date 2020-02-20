from django.db import models

# Create your models here.
class DaysAvailable(models.Model):
    key = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=20)
    order = models.IntegerField(default=0)
    available_scheduling = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Department(models.Model):
    department_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.department_name

class Event(models.Model):
    event_name = models.CharField(max_length=200)
    event_start = models.DateField()
    event_end = models.DateField()
    max_merchants = models.IntegerField(default=0)

    def __str__(self):
        return self.event_name
