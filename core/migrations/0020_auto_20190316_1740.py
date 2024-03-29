# Generated by Django 2.1.7 on 2019-03-16 12:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20190316_1736'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='last_modified',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 3, 16, 17, 40, 1, 963824)),
        ),
        migrations.AlterField(
            model_name='tasks',
            name='last_modified',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 3, 16, 17, 40, 1, 962825)),
        ),
        migrations.AlterField(
            model_name='tasks',
            name='status',
            field=models.CharField(choices=[('planned', 'Planned'), ('in_progress', 'In Progress'), ('done', 'Done')], default='planned', max_length=30),
        ),
    ]
