from rest_framework import serializers
from decimal import Decimal
from .models import Bet, BetSlip
from events.models import Event


class BetSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_id = serializers.IntegerField(source='event.id', read_only=True)
    outcome_name = serializers.CharField(source='outcome.name', read_only=True)
    outcome_id = serializers.IntegerField(source='outcome.id', read_only=True)
    outcome_odds = serializers.DecimalField(source='outcome.odds', max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = Bet
        fields = [
            'id', 'user', 'event', 'event_id', 'event_title', 'outcome', 'outcome_id',
            'outcome_name', 'outcome_odds', 'stake', 'potential_win', 'actual_win', 'status', 
            'is_claimed', 'claimed_at', 'placed_at'
        ]
        read_only_fields = ['id', 'user', 'potential_win', 'actual_win', 'status', 'is_claimed', 'claimed_at', 'placed_at']


class PlaceBetSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    outcome_id = serializers.IntegerField()
    stake = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('1.00'))

    def validate(self, attrs):
        try:
            event = Event.objects.get(id=attrs['event_id'])
        except Event.DoesNotExist:
            raise serializers.ValidationError({'event_id': 'Event not found'})

        if event.status != 'open':
            raise serializers.ValidationError({'event_id': 'Event is not open for betting'})

        from events.models import Outcome
        try:
            outcome = Outcome.objects.get(id=attrs['outcome_id'], event=event)
        except Outcome.DoesNotExist:
            raise serializers.ValidationError({'outcome_id': 'Outcome not found for this event'})

        stake = Decimal(str(attrs['stake']))
        if stake < event.min_bet:
            raise serializers.ValidationError({'stake': f'Minimum bet is {event.min_bet}'})
        if stake > event.max_bet:
            raise serializers.ValidationError({'stake': f'Maximum bet is {event.max_bet}'})

        attrs['event'] = event
        attrs['outcome'] = outcome
        return attrs


class BetSlipSerializer(serializers.ModelSerializer):
    bets_detail = BetSerializer(source='bets', many=True, read_only=True)

    class Meta:
        model = BetSlip
        fields = ['id', 'bets', 'bets_detail', 'total_stake', 'potential_payout', 'is_completed', 'created_at']
        read_only_fields = ['id', 'total_stake', 'potential_payout', 'is_completed', 'created_at']


class SettleBetSerializer(serializers.Serializer):
    bet_id = serializers.UUIDField()
    won = serializers.BooleanField()
