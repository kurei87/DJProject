from rest_framework import serializers
from decimal import Decimal
from .models import Wallet, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'amount', 'balance_after', 'description', 'reference_id', 'created_at']
        read_only_fields = ['id', 'balance_after', 'created_at']


class WalletSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'user', 'user_email', 'balance', 'currency', 'is_active', 'transactions', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'balance', 'created_at', 'updated_at']


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('1.00'))

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be positive')
        return value


class WithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('1.00'))

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be positive')
        return value
