# Generated by Django 3.0 on 2020-01-13 16:47

import Alumni_Tracking.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alumni_Tracking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumni',
            name='profile_pic',
            field=models.ImageField(blank=True, default='dp/default.png', upload_to=Alumni_Tracking.models.user_instance_pic),
        ),
    ]
