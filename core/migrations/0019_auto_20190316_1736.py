# Generated by Django 2.1.7 on 2019-03-16 12:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20190316_1642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='last_modified',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 3, 16, 17, 36, 56, 618556)),
        ),
        migrations.AlterField(
            model_name='tasks',
            name='last_modified',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 3, 16, 17, 36, 56, 617557)),
        ),
        migrations.AlterField(
            model_name='tasks',
            name='status',
            field=models.CharField(choices=[('Planned', 'Planned'), ('In Progress', 'In Progress'), ('Done', 'Done')], default='planned', max_length=30),
        ),
    ]
