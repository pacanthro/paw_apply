# Generated by Django 5.0.11 on 2025-01-18 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0003_volunteertask'),
    ]

    operations = [
        migrations.AlterField(
            model_name='volunteertask',
            name='task_notes',
            field=models.TextField(blank=True),
        ),
    ]
