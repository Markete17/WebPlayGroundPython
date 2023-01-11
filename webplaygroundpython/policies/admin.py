from django.contrib import admin
from .models import PolicyStatus, ReceiptStatus, Policy, Receipt

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated', 'cancellation_date', 'suspension_date', 'policy_code')
    list_display = ('policy_code', 'status')

@admin.register(PolicyStatus)
class PolicyStatusAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')

@admin.register(ReceiptStatus)
class ReceiptStatusAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    readonly_fields = ('payment_date','receipt_code','cancellation_date','payment_date')
    list_display = ('receipt_code', 'amount', 'status')
    
