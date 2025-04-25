// Authentication utilities
const AUTH_TOKEN_KEY = 'auth_token';
const USER_DATA_KEY = 'user_data';

// Check if user is authenticated
function isAuthenticated() {
    return localStorage.getItem(AUTH_TOKEN_KEY) !== null;
}

// Get current user data
function getCurrentUser() {
    const userData = localStorage.getItem(USER_DATA_KEY);
    return userData ? JSON.parse(userData) : null;
}

// Save authentication data
function saveAuthData(token, userData) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
    localStorage.setItem(USER_DATA_KEY, JSON.stringify(userData));
}

// Clear authentication data
function clearAuthData() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(USER_DATA_KEY);
}

// Verify session with backend
async function verifySession() {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (!token) return false;

    try {
        const response = await fetch(`/api/verify-session?token=${token}`);
        if (!response.ok) {
            clearAuthData();
            return false;
        }
        const data = await response.json();
        if (data.success) {
            saveAuthData(token, data.user);
            return true;
        }
        return false;
    } catch (error) {
        console.error('Error verifying session:', error);
        return false;
    }
}

// Handle logout
async function logout() {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (token) {
        try {
            await fetch('/api/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token })
            });
        } catch (error) {
            console.error('Error during logout:', error);
        }
    }
    clearAuthData();
    window.location.href = '/';
}

// Update UI based on authentication state
function updateAuthUI() {
    const userMenu = document.getElementById('userMenu');
    const userName = document.getElementById('userName');
    const logoutBtn = document.getElementById('logoutBtn');

    if (isAuthenticated()) {
        const user = getCurrentUser();
        if (userName) userName.textContent = user.email;
        if (logoutBtn) logoutBtn.style.display = 'block';
    } else {
        if (userName) userName.textContent = 'Sign In';
        if (logoutBtn) logoutBtn.style.display = 'none';
    }
}

// Initialize authentication state
async function initAuth() {
    await verifySession();
    updateAuthUI();
}

// Export functions
window.auth = {
    isAuthenticated,
    getCurrentUser,
    saveAuthData,
    clearAuthData,
    verifySession,
    logout,
    updateAuthUI,
    initAuth
}; 