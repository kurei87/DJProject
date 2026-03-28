from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('events/', views.events_view, name='events'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<slug:event_id>/', views.event_detail, name='event_detail'),
    path('wallet/', views.wallet_view, name='wallet'),
    path('bets/', views.bets_view, name='bets'),
    path('profile/', views.profile_view, name='profile'),
    path('open-events/', views.open_events_view, name='open_events'),
]
