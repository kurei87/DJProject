from django.db import models
from django.conf import settings
from decimal import Decimal


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='USD')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wallets'

    def __str__(self):
        return f"{self.user.email} - {self.balance} {self.currency}"

    def credit(self, amount, description=''):
        if amount <= 0:
            raise ValueError('Amount must be positive')
        self.balance += amount
        self.save()
        return Transaction.objects.create(
            wallet=self,
            transaction_type='credit',
            amount=amount,
            balance_after=self.balance,
            description=description
        )

    def debit(self, amount, description=''):
        if amount <= 0:
            raise ValueError('Amount must be positive')
        if self.balance < amount:
            raise ValueError('Insufficient balance')
        self.balance -= amount
        self.save()
        return Transaction.objects.create(
            wallet=self,
            transaction_type='debit',
            amount=amount,
            balance_after=self.balance,
            description=description
        )


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('bet', 'Bet Placed'),
        ('win', 'Win'),
        ('refund', 'Refund'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    reference_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} ({self.created_at})"
