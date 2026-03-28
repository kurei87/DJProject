from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WalletViewSet, DepositView, WithdrawView

router = DefaultRouter()
router.register(r'', WalletViewSet, basename='wallet')

urlpatterns = [
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('', include(router.urls)),
]
