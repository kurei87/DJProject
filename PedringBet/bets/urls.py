from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BetViewSet, PlaceBetView, SettleBetView, SettleEventBetsView, BetStatsView, ClaimBetView

router = DefaultRouter()
router.register(r'', BetViewSet, basename='bet')

urlpatterns = [
    path('place/', PlaceBetView.as_view(), name='place_bet'),
    path('claim/<uuid:bet_id>/', ClaimBetView.as_view(), name='claim_bet'),
    path('settle/', SettleBetView.as_view(), name='settle_bet'),
    path('settle-event/<int:event_id>/', SettleEventBetsView.as_view(), name='settle_event'),
    path('stats/', BetStatsView.as_view(), name='bet_stats'),
    path('<uuid:pk>/', BetViewSet.as_view({'get': 'retrieve'}), name='bet-detail'),
    path('', include(router.urls)),
]
