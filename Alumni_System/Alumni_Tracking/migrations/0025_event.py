# Generated by Django 3.0 on 2020-01-19 19:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Alumni_Tracking', '0024_fund_projects_projects'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('about', models.CharField(max_length=300)),
                ('event_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('address', models.CharField(max_length=150, null=True)),
                ('mobile', models.CharField(max_length=10, null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Alumni_Tracking.alumni')),
                ('college', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Alumni_Tracking.college')),
            ],
        ),
    ]
