// frontend/js/auth.js

// 1. Reusable function: function getToken() { return localStorage.getItem("token"); }
function getToken() {
    return localStorage.getItem("token");
}

// 2. Handle unauthorized errors (returns true if redirected)
function handle401Error(response) {
    if (response.status === 401) {
        localStorage.removeItem("token");
        window.location.href = "login.html";
        return true;
    }
    return false;
}

// Protect pages logic
document.addEventListener("DOMContentLoaded", () => {
    const token = getToken();
    const currentPath = window.location.pathname;

    const isPublicPage = currentPath.endsWith('login.html') || 
                         currentPath.endsWith('register.html') || 
                         currentPath.endsWith('index.html') ||
                         currentPath === '/';

    // Protect pages: if missing token, redirect to login
    if (!token && !isPublicPage) {
        window.location.href = 'login.html';
        return;
    }

    // Redirect logged-in users away from auth pages to dashboard
    if (token && isPublicPage) {
        window.location.href = 'dashboard.html';
    }

    // Handle logout globally
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('token');
            window.location.href = 'login.html';
        });
    }
});
