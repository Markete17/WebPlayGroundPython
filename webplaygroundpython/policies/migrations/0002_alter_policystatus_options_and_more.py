# Generated by Django 4.1.4 on 2023-01-11 08:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='policystatus',
            options={'verbose_name': 'Estado Póliza'},
        ),
        migrations.AlterModelOptions(
            name='receiptstatus',
            options={'verbose_name': 'Estado Recibo'},
        ),
    ]