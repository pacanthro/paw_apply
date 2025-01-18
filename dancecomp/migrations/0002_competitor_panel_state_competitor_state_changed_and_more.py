# Generated by Django 5.0.11 on 2025-01-18 19:21

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dancecomp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='competitor',
            name='panel_state',
            field=models.CharField(choices=[('STATE_NEW', 'New'), ('STATE_ACCEPTED', 'Accepted'), ('STATE_ASSIGNED', 'Assigned'), ('STATE_CANCELED', 'Canceled'), ('STATE_WAITLIST', 'Waitlisted'), ('STATE_DENIED', 'Denied'), ('STATE_DELETED', 'Deleted'), ('STATE_OLD', 'Migrated Data')], default='STATE_NEW', max_length=20),
        ),
        migrations.AddField(
            model_name='competitor',
            name='state_changed',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='competitor',
            name='is_group',
            field=models.BooleanField(default=False, help_text='Check this if you are entering as a group and provide the names of the other competitors below.', verbose_name='Group Performance'),
        ),
        migrations.AlterField(
            model_name='competitor',
            name='music_url',
            field=models.URLField(default='', help_text='Please provide us with a link to the music for your performance. Something like a DropBox or Box link will be fine.'),
        ),
        migrations.AlterField(
            model_name='competitor',
            name='twitter_handle',
            field=models.CharField(max_length=30, verbose_name='Twitter/BSky Handle'),
        ),
    ]
