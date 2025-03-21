# Generated by Django 5.0.9 on 2024-11-16 16:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_eventroom_schedulingconfig'),
        ('performers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='performer',
            name='scheduled_day',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.daysavailable'),
        ),
        migrations.AddField(
            model_name='performer',
            name='scheduled_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='performer',
            name='performer_state',
            field=models.CharField(choices=[('STATE_NEW', 'New'), ('STATE_ACCEPTED', 'Accepted'), ('STATE_ASSIGNED', 'Assigned'), ('STATE_CANCELED', 'Canceled'), ('STATE_WAITLIST', 'Waitlisted'), ('STATE_DENIED', 'Denied'), ('STATE_DELETED', 'Deleted'), ('STATE_OLD', 'Migrated Data')], default='STATE_NEW', max_length=20),
        ),
    ]
