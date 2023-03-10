# Generated by Django 4.1.4 on 2023-01-11 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0005_policy_receipt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='policy',
            name='policy_number',
        ),
        migrations.RemoveField(
            model_name='receipt',
            name='receipt_number',
        ),
        migrations.AddField(
            model_name='policy',
            name='policy_code',
            field=models.CharField(default='P', max_length=250, unique=True, verbose_name='Número Póliza'),
        ),
        migrations.AddField(
            model_name='receipt',
            name='receipt_code',
            field=models.CharField(default='R', max_length=250, unique=True, verbose_name='Número Recibo'),
        ),
        migrations.AlterField(
            model_name='policystatus',
            name='code',
            field=models.CharField(max_length=2, unique=True, verbose_name='Código'),
        ),
        migrations.AlterField(
            model_name='policystatus',
            name='name',
            field=models.CharField(max_length=250, unique=True, verbose_name='Estado Póliza'),
        ),
        migrations.AlterField(
            model_name='receiptstatus',
            name='code',
            field=models.CharField(max_length=2, unique=True, verbose_name='Código'),
        ),
        migrations.AlterField(
            model_name='receiptstatus',
            name='name',
            field=models.CharField(max_length=250, unique=True, verbose_name='Estado Recibo'),
        ),
    ]
