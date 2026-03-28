from django.contrib import admin
from .models import Bet, BetSlip


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event', 'outcome', 'stake', 'potential_win', 'actual_win', 'status', 'placed_at']
    list_filter = ['status', 'placed_at', 'event']
    search_fields = ['user__email', 'event__title']
    ordering = ['-placed_at']
    readonly_fields = ['id', 'potential_win']


@admin.register(BetSlip)
class BetSlipAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_stake', 'potential_payout', 'is_completed', 'created_at']
    list_filter = ['is_completed', 'created_at']
    search_fields = ['user__email']
    ordering = ['-created_at']
