# Generated by Django 5.2 on 2025-04-21 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map_features', '0005_alter_rsvp_unique_together_chatimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='tags',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
