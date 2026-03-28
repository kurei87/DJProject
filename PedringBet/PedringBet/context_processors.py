def user_status(request):
    token = request.session.get('access_token')
    is_admin = False
    if token:
        try:
            import requests
            resp = requests.get('http://localhost:8000/api/users/profile/',
                               headers={'Authorization': f'Bearer {token}'}, timeout=3)
            if resp.status_code == 200:
                is_admin = resp.json().get('is_staff', False)
        except:
            pass
    return {'user_is_admin': is_admin}
