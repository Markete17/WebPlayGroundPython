from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
import datetime

# Create your models here.
class PolicyStatus(models.Model):

    code = models.CharField(verbose_name='Código', max_length=2,  blank=False, null=False, unique=True)
    name = models.CharField(verbose_name='Estado Póliza', blank=False, null=False, max_length=250, unique=True)

    class Meta:
        verbose_name = ("Estado Póliza")

    def __str__(self):
        return self.name

class ReceiptStatus(models.Model):

    code = models.CharField(verbose_name='Código', max_length=2,  blank=False, null=False, unique=True)
    name = models.CharField(verbose_name='Estado Recibo', blank=False, null=False, max_length=250, unique=True)

    class Meta:
        verbose_name = ("Estado Recibo")

    def __str__(self):
        return self.name
    
class Policy(models.Model):

    policy_code = models.CharField(verbose_name="Número Póliza", null=False, blank=False, max_length=250, unique=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha Alta")
    updated = models.DateTimeField(auto_now=True, verbose_name="Fecha Modificación")
    cancellation_date = models.DateTimeField(verbose_name="Fecha Anulación", null=True)
    suspension_date = models.DateTimeField(verbose_name="Fecha Suspensión", null=True)
    owner = models.ForeignKey(User, null=False, verbose_name="Titular", on_delete=models.CASCADE, related_query_name="policies")
    status = models.ForeignKey(PolicyStatus, on_delete=models.SET_NULL, null=True, verbose_name="Estado Póliza")

    class Meta:
        verbose_name = ("Póliza")
        verbose_name_plural = ("Pólizas")

    def __str__(self):
        return self.policy_code

class Receipt(models.Model):

    receipt_code = models.CharField(verbose_name="Número Recibo", null=False, max_length=250, unique=True)
    start_date = models.DateField(verbose_name="Fecha Inicio", null=False)
    end_date = models.DateField(verbose_name="Fecha Final", null=False)
    payment_date = models.DateField(verbose_name="Fecha Pago", null=True)
    cancellation_date = models.DateField(verbose_name="Fecha Cancelación", null=True)
    amount = models.DecimalField(verbose_name="Importe", max_digits=50, decimal_places=2)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="receipts")
    status = models.ForeignKey(ReceiptStatus, on_delete=models.SET_NULL, null=True, verbose_name="Estado Recibo")

    class Meta:
        verbose_name = ("Recibo")
        verbose_name_plural = ("Recibos")

    def __str__(self):
        return self.receipt_code

def set_cancellation_suspended_date(instance):
    if instance.status.code == 'A':
        instance.cancellation_date = datetime.datetime.now()
        instance.suspension_date = None
    elif instance.status.code == 'S':
        instance.suspension_date = datetime.datetime.now()
        instance.cancellation_date = None
    else:
        instance.suspension_date = None
        instance.cancellation_date = None

def set_payment_cancellation_date(instance):
    if instance.status.code == 'P':
        instance.payment_date = datetime.datetime.now()
        instance.cancellation_date = None
    elif instance.status.code == 'C':
        instance.payment_date = None
        instance.cancellation_date = datetime.datetime.now()
    else:
        instance.payment_date = None
        instance.cancellation_date = None

@receiver(post_save, sender=Policy)
def create_policy_code_number(sender, instance,**kwargs):
    if kwargs.get('created', False):
        instance.policy_code = str(instance.pk).zfill(6)
        set_cancellation_suspended_date(instance)
        instance.save(update_fields=['policy_code', 'cancellation_date', 'suspension_date'])
    else:
        if kwargs.get('update_fields') is None:
            set_cancellation_suspended_date(instance)
            instance.save(update_fields=['cancellation_date','suspension_date'])

@receiver(post_save, sender=Receipt)
def receipt_post_save_receiver(sender, instance, **kwargs):
    if kwargs.get('created', False):
        instance.receipt_code = f'R-{str(instance.pk).zfill(6)}'
        set_payment_cancellation_date(instance)
        instance.save(update_fields=['receipt_code', 'payment_date', 'cancellation_date'])
    else:
        if kwargs.get('update_fields') is None:
            set_payment_cancellation_date(instance)
            instance.save(update_fields=['payment_date', 'cancellation_date'])