# Generated by Django 3.0 on 2020-01-18 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alumni_Tracking', '0022_auto_20200118_0414'),
    ]

    operations = [
        migrations.AddField(
            model_name='internships',
            name='added',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
