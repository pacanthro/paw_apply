# Generated by Django 5.0.11 on 2025-01-18 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dancecomp', '0004_alter_competitor_performer_five_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competitor',
            name='performer_five',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='competitor',
            name='performer_four',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='competitor',
            name='performer_three',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='competitor',
            name='performer_two',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
