from django.shortcuts import render
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import redirect


def custom_404(request, exception):
    return render(request, '404.html', status=404)


def home(request):
    return render(request, 'home.html')


def login_view(request):
    return render(request, 'login.html')


def register_view(request):
    return render(request, 'register.html')


def dashboard(request):
    return render(request, 'dashboard.html')

def events_view(request):
    return render(request, 'events.html')

def create_event(request):
    return render(request, 'create_event.html')


def event_detail(request, event_id):
    try:
        event_id = int(event_id)
    except (ValueError, TypeError):
        return render(request, '404.html', status=404)
    return render(request, 'event_detail.html', {'event_id': event_id})


def wallet_view(request):
    return render(request, 'wallet.html')


def bets_view(request):
    return render(request, 'bets.html')


def profile_view(request):
    return render(request, 'profile.html')


def open_events_view(request):
    return render(request, 'open_events.html')


def logout_view(request):
    django_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


def check_admin_status(request):
    from users.models import User
    token = request.session.get('access_token')
    if not token:
        return False
    try:
        import requests
        resp = requests.get('http://localhost:8000/api/users/profile/',
                           headers={'Authorization': f'Bearer {token}'})
        if resp.status_code == 200:
            return resp.json().get('is_staff', False)
    except:
        pass
    return False
