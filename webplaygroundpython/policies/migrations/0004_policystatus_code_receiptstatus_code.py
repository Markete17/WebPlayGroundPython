# Generated by Django 4.1.4 on 2023-01-11 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0003_alter_policystatus_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='policystatus',
            name='code',
            field=models.CharField(default='XX', max_length=2, verbose_name='Código'),
        ),
        migrations.AddField(
            model_name='receiptstatus',
            name='code',
            field=models.CharField(default='XX', max_length=2, verbose_name='Código'),
        ),
    ]
