from rest_framework import serializers
from .models import Category, Event, Outcome
from django.db.models import Sum


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class OutcomeSerializer(serializers.ModelSerializer):
    total_bets = serializers.SerializerMethodField()

    class Meta:
        model = Outcome
        fields = ['id', 'name', 'odds', 'is_winner', 'total_bets']

    def get_total_bets(self, obj):
        from bets.models import Bet
        return float(Bet.objects.filter(outcome=obj, status='pending').aggregate(total=Sum('stake'))['total'] or 0)


class OutcomeDetailSerializer(serializers.ModelSerializer):
    total_bets = serializers.SerializerMethodField()
    bet_count = serializers.SerializerMethodField()

    class Meta:
        model = Outcome
        fields = ['id', 'name', 'odds', 'is_winner', 'total_bets', 'bet_count']

    def get_total_bets(self, obj):
        from bets.models import Bet
        return float(Bet.objects.filter(outcome=obj).aggregate(total=Sum('stake'))['total'] or 0)

    def get_bet_count(self, obj):
        return obj.bets.count()


class EventSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    outcomes = OutcomeDetailSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'category', 'category_name',
            'start_time', 'end_time', 'status', 'min_bet', 'max_bet', 'pool_fee',
            'outcomes', 'created_by', 'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class EventCreateSerializer(serializers.ModelSerializer):
    outcomes = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    start_time = serializers.DateTimeField(required=False, allow_null=True)
    end_time = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'category', 'start_time', 'end_time',
            'min_bet', 'max_bet', 'pool_fee', 'outcomes'
        ]

    def create(self, validated_data):
        outcomes_data = validated_data.pop('outcomes', [])
        validated_data['created_by'] = self.context['request'].user
        event = Event.objects.create(**validated_data)

        for outcome_data in outcomes_data:
            Outcome.objects.create(event=event, **outcome_data)

        return event


class EventUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'start_time', 'end_time', 'status', 'min_bet', 'max_bet', 'pool_fee']
