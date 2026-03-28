from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction as db_transaction
from django.db.models import Sum, Count
from django.utils import timezone
from decimal import Decimal

from .models import Bet, BetSlip
from .serializers import BetSerializer, PlaceBetSerializer, BetSlipSerializer, SettleBetSerializer
from events.models import Event, Outcome
from wallets.models import Wallet


class BetViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bet.objects.filter(user=self.request.user)


class PlaceBetView(APIView):
    permission_classes = [IsAuthenticated]

    def calculate_dynamic_odds(self, event, outcome):
        total_pool = Bet.objects.filter(event=event).aggregate(total=Sum('stake'))['total'] or Decimal('0.00')
        outcome_bets = Bet.objects.filter(event=event, outcome=outcome).aggregate(total=Sum('stake'))['total'] or Decimal('0.00')
        
        if total_pool == 0 or outcome_bets == 0:
            return Decimal(str(outcome.odds))
        
        pool_fee = Decimal(str(event.pool_fee)) / Decimal('100')
        net_pool = total_pool * (Decimal('1') - pool_fee)
        
        dynamic_odds = net_pool / outcome_bets
        return max(Decimal('1.01'), dynamic_odds)

    def recalculate_all_bets_for_event(self, event):
        from events.models import Outcome
        outcomes = Outcome.objects.filter(event=event)
        recalculated_count = 0
        
        for outcome in outcomes:
            dynamic_odds = self.calculate_dynamic_odds(event, outcome)
            pending_bets = Bet.objects.filter(event=event, outcome=outcome, status='pending')
            
            for bet in pending_bets:
                new_potential_win = bet.stake * dynamic_odds
                if bet.potential_win != new_potential_win:
                    bet.potential_win = new_potential_win
                    bet.save()
                    recalculated_count += 1
        
        return recalculated_count

    @db_transaction.atomic
    def post(self, request):
        serializer = PlaceBetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event = serializer.validated_data['event']
        outcome = serializer.validated_data['outcome']
        stake = Decimal(str(serializer.validated_data['stake']))

        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            wallet = Wallet.objects.create(user=request.user)

        if wallet.balance < stake:
            return Response(
                {'error': 'Insufficient balance'},
                status=status.HTTP_400_BAD_REQUEST
            )

        dynamic_odds = self.calculate_dynamic_odds(event, outcome)
        potential_win = stake * dynamic_odds

        wallet.debit(stake, f'Bet placed - {event.title}')

        bet = Bet.objects.create(
            user=request.user,
            event=event,
            outcome=outcome,
            stake=stake,
            potential_win=potential_win
        )

        recalculated = self.recalculate_all_bets_for_event(event)

        return Response(
            {
                'message': 'Bet placed successfully',
                'bet': BetSerializer(bet).data,
                'dynamic_odds_used': str(dynamic_odds),
                'potential_win': str(potential_win),
                'recalculated_bets': recalculated
            },
            status=status.HTTP_201_CREATED
        )


class SettleBetView(APIView):
    permission_classes = [IsAdminUser]

    def calculate_dynamic_odds(self, event, outcome):
        total_pool = Bet.objects.filter(event=event).aggregate(total=Sum('stake'))['total'] or Decimal('0.00')
        outcome_bets = Bet.objects.filter(event=event, outcome=outcome).aggregate(total=Sum('stake'))['total'] or Decimal('0.00')
        
        if total_pool == 0 or outcome_bets == 0:
            return Decimal(str(outcome.odds))
        
        pool_fee = Decimal(str(event.pool_fee)) / Decimal('100')
        net_pool = total_pool * (Decimal('1') - pool_fee)
        dynamic_odds = net_pool / outcome_bets
        
        return max(Decimal('1.01'), dynamic_odds)

    @db_transaction.atomic
    def post(self, request):
        serializer = SettleBetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            bet = Bet.objects.get(id=serializer.validated_data['bet_id'])
        except Bet.DoesNotExist:
            return Response({'error': 'Bet not found'}, status=status.HTTP_404_NOT_FOUND)

        if bet.status != 'pending':
            return Response({'error': 'Bet already settled'}, status=status.HTTP_400_BAD_REQUEST)

        won = serializer.validated_data['won']
        
        dynamic_odds = self.calculate_dynamic_odds(bet.event, bet.outcome)
        
        if won:
            bet.status = 'won'
            bet.actual_win = bet.stake * dynamic_odds
        else:
            bet.status = 'lost'
            bet.actual_win = Decimal('0.00')
        bet.save()

        return Response({
            'message': f'Bet settled as {"won" if won else "lost"}',
            'bet': BetSerializer(bet).data,
            'dynamic_odds_used': str(dynamic_odds)
        })


class SettleEventBetsView(APIView):
    permission_classes = [IsAdminUser]

    def calculate_dynamic_odds(self, event, outcome):
        total_pool = Bet.objects.filter(event=event).aggregate(total=Sum('stake'))['total'] or Decimal('0.00')
        outcome_bets = Bet.objects.filter(event=event, outcome=outcome).aggregate(total=Sum('stake'))['total'] or Decimal('0.00')
        
        if total_pool == 0 or outcome_bets == 0:
            return Decimal(str(outcome.odds))
        
        pool_fee = Decimal(str(event.pool_fee)) / Decimal('100')
        net_pool = total_pool * (Decimal('1') - pool_fee)
        dynamic_odds = net_pool / outcome_bets
        
        return max(Decimal('1.01'), dynamic_odds)

    @db_transaction.atomic
    def post(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

        winner_id = request.data.get('winner_id')
        if not winner_id:
            return Response({'error': 'winner_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            winner_outcome = Outcome.objects.get(id=winner_id, event=event)
        except Outcome.DoesNotExist:
            return Response({'error': 'Winner outcome not found'}, status=status.HTTP_404_NOT_FOUND)

        Outcome.objects.filter(event=event).update(is_winner=False)
        winner_outcome.is_winner = True
        winner_outcome.save()

        pending_bets = Bet.objects.filter(event=event, status='pending')
        
        total_pool = pending_bets.aggregate(total=Sum('stake'))['total'] or Decimal('0.00')
        
        winner_dynamic_odds = self.calculate_dynamic_odds(event, winner_outcome)

        settled_count = 0
        for bet in pending_bets:
            if bet.outcome == winner_outcome:
                bet.status = 'won'
                bet.actual_win = bet.stake * winner_dynamic_odds
            else:
                bet.status = 'lost'
                bet.actual_win = Decimal('0.00')
            bet.save()
            settled_count += 1

        event.status = 'settled'
        event.save()

        return Response({
            'message': f'Settled {settled_count} bets',
            'winner': winner_outcome.name,
            'total_pool': str(total_pool),
            'winner_odds': str(winner_dynamic_odds)
        })


class BetStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        bets = Bet.objects.filter(user=user)

        total_bets = bets.count()
        won_bets = bets.filter(status='won').count()
        lost_bets = bets.filter(status='lost').count()
        pending_bets = bets.filter(status='pending').count()
        unclaimed_wins = bets.filter(status='won', is_claimed=False).count()

        total_wagered = bets.aggregate(total=Sum('stake'))['total'] or Decimal('0.00')
        total_won = bets.aggregate(total=Sum('actual_win'))['total'] or Decimal('0.00')
        unclaimed_amount = bets.filter(status='won', is_claimed=False).aggregate(total=Sum('actual_win'))['total'] or Decimal('0.00')
        profit = total_won - total_wagered

        return Response({
            'total_bets': total_bets,
            'won_bets': won_bets,
            'lost_bets': lost_bets,
            'pending_bets': pending_bets,
            'unclaimed_wins': unclaimed_wins,
            'unclaimed_amount': unclaimed_amount,
            'total_wagered': total_wagered,
            'total_won': total_won,
            'profit': profit,
            'win_rate': (won_bets / total_bets * 100) if total_bets > 0 else 0
        })


class ClaimBetView(APIView):
    permission_classes = [IsAuthenticated]

    @db_transaction.atomic
    def post(self, request, bet_id):
        from uuid import UUID
        try:
            bet_uuid = UUID(str(bet_id))
            bet = Bet.objects.get(id=bet_uuid, user=request.user)
        except (Bet.DoesNotExist, ValueError):
            return Response({'error': 'Bet not found'}, status=status.HTTP_404_NOT_FOUND)

        if bet.status != 'won':
            return Response({'error': 'Can only claim won bets'}, status=status.HTTP_400_BAD_REQUEST)

        if bet.is_claimed:
            return Response({'error': 'Bet already claimed'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            bet.claim()
            return Response({
                'message': 'Bet claimed successfully!',
                'amount_claimed': str(bet.actual_win)
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
