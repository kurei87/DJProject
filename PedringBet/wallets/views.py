from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction as db_transaction
from decimal import Decimal

from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer, DepositSerializer, WithdrawSerializer


class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)


class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    @db_transaction.atomic
    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data['amount']
        wallet, created = Wallet.objects.get_or_create(user=request.user)

        tx = wallet.credit(amount, 'Deposit')
        return Response(
            {'message': 'Deposit successful', 'transaction': TransactionSerializer(tx).data},
            status=status.HTTP_201_CREATED
        )


class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    @db_transaction.atomic
    def post(self, request):
        serializer = WithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data['amount']
        wallet = Wallet.objects.get(user=request.user)

        try:
            tx = wallet.debit(amount, 'Withdrawal')
            return Response(
                {'message': 'Withdrawal successful', 'transaction': TransactionSerializer(tx).data},
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
