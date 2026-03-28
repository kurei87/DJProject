"""PedringBet URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from core.views import custom_404

#handler404 = custom_404

urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/events/', include('events.urls')),
    path('api/bets/', include('bets.urls')),
    path('api/wallets/', include('wallets.urls')),
]
