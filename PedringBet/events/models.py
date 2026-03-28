from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Event(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('open', 'Open for Betting'),
        ('closed', 'Closed'),
        ('settled', 'Settled'),
        ('cancelled', 'Cancelled'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='events')
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    min_bet = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    max_bet = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    pool_fee = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        ordering = ['-start_time']

    def __str__(self):
        return self.title


class Outcome(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='outcomes')
    name = models.CharField(max_length=255)
    odds = models.DecimalField(max_digits=6, decimal_places=2)
    is_winner = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'outcomes'

    def __str__(self):
        return f"{self.event.title} - {self.name} ({self.odds})"
