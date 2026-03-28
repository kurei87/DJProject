const API_BASE = '/api';

let authToken = localStorage.getItem('accessToken');
let refreshToken = localStorage.getItem('refreshToken');

async function apiCall(endpoint, method = 'GET', body = null) {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    const options = { method, headers };
    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        let response = await fetch(`${API_BASE}${endpoint}`, options);
        
        if (response.status === 401 && refreshToken) {
            const refreshed = await refreshAccessToken();
            if (refreshed) {
                headers['Authorization'] = `Bearer ${authToken}`;
                response = await fetch(`${API_BASE}${endpoint}`, options);
            }
        }

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || data.message || 'An error occurred');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

async function refreshAccessToken() {
    try {
        const response = await fetch(`${API_BASE}/users/token/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken })
        });
        
        if (response.ok) {
            const data = await response.json();
            authToken = data.access;
            localStorage.setItem('accessToken', authToken);
            return true;
        }
        return false;
    } catch {
        logout();
        return false;
    }
}

function setTokens(access, refresh) {
    authToken = access;
    refreshToken = refresh;
    localStorage.setItem('accessToken', access);
    localStorage.setItem('refreshToken', refresh);
}

function logout() {
    authToken = null;
    refreshToken = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    window.location.href = '/login/';
}

function isAuthenticated() {
    return !!authToken;
}

async function getWalletBalance() {
    try {
        const data = await apiCall('/wallets/');
        return data.results?.[0]?.balance || '0.00';
    } catch {
        return '0.00';
    }
}

async function getUserProfile() {
    return await apiCall('/users/profile/');
}

function showLoading() {
    document.getElementById('loading')?.classList.add('show');
}

function hideLoading() {
    document.getElementById('loading')?.classList.remove('show');
}
