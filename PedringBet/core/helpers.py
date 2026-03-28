import requests
from django.conf import settings


def api_request(method, endpoint, data=None, token=None):
    url = f"{getattr(settings, 'API_BASE_URL', 'http://localhost:8000/api')}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    elif hasattr(settings, 'API_TOKEN'):
        headers['Authorization'] = f'Bearer {settings.API_TOKEN}'
    
    if method.upper() == 'GET':
        response = requests.get(url, headers=headers)
    elif method.upper() == 'POST':
        response = requests.post(url, json=data, headers=headers)
    elif method.upper() == 'PUT':
        response = requests.put(url, json=data, headers=headers)
    elif method.upper() == 'PATCH':
        response = requests.patch(url, json=data, headers=headers)
    elif method.upper() == 'DELETE':
        response = requests.delete(url, headers=headers)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    
    return response
