# Generated by Django 4.1.5 on 2023-01-18 09:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0019_alter_policy_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policy',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 18, 10, 44, 19, 125773), verbose_name='Fecha Alta'),
        ),
    ]