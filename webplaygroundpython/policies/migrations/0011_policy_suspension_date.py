# Generated by Django 4.1.4 on 2023-01-11 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0010_alter_policy_status_alter_receipt_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='policy',
            name='suspension_date',
            field=models.DateTimeField(null=True, verbose_name='Fecha Suspensión'),
        ),
    ]