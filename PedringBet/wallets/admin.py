from django.contrib import admin
from .models import Wallet, Transaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'currency', 'is_active', 'created_at']
    list_filter = ['is_active', 'currency']
    search_fields = ['user__email', 'user__username']
    ordering = ['-created_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'transaction_type', 'amount', 'balance_after', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['wallet__user__email', 'description', 'reference_id']
    ordering = ['-created_at']
    readonly_fields = ['wallet', 'transaction_type', 'amount', 'balance_after', 'reference_id']
