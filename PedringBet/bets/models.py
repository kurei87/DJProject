from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid

from events.models import Event, Outcome
from wallets.models import Wallet


class Bet(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bets')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bets')
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE, related_name='bets')
    stake = models.DecimalField(max_digits=10, decimal_places=2)
    potential_win = models.DecimalField(max_digits=10, decimal_places=2)
    actual_win = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_claimed = models.BooleanField(default=False)
    claimed_at = models.DateTimeField(null=True, blank=True)
    placed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bets'
        ordering = ['-placed_at']

    def __str__(self):
        return f"{self.user.email} - {self.event.title} - {self.outcome.name}"

    def calculate_potential_win(self):
        return self.stake * self.outcome.odds

    def settle(self, won: bool):
        if won:
            self.status = 'won'
            self.actual_win = self.potential_win
        else:
            self.status = 'lost'
            self.actual_win = Decimal('0.00')
        self.save()

    def claim(self):
        if self.status != 'won':
            raise ValueError('Can only claim won bets')
        if self.is_claimed:
            raise ValueError('Bet already claimed')
        self.user.wallet.credit(self.actual_win, f'Bet win claimed - {self.event.title}')
        self.is_claimed = True
        from django.utils import timezone
        self.claimed_at = timezone.now()
        self.save()

    def refund(self):
        self.status = 'refunded'
        self.actual_win = self.stake
        self.user.wallet.credit(self.stake, f'Bet refund - {self.event.title}')
        self.save()


class BetSlip(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bet_slips')
    bets = models.ManyToManyField(Bet, related_name='slips')
    total_stake = models.DecimalField(max_digits=10, decimal_places=2)
    potential_payout = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bet_slips'

    def __str__(self):
        return f"BetSlip {self.id} - {self.user.email}"
