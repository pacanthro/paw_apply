# Generated by Django 5.0.11 on 2025-01-19 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partyfloor', '0003_partyhost_party_description_partyhost_party_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partyhost',
            name='twitter_handle',
            field=models.CharField(max_length=30, null=True, verbose_name='Twitter/BSky Handle'),
        ),
    ]
