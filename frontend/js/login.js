// frontend/js/login.js

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    const loginError = document.getElementById('loginError');
    const usernameInput = document.getElementById('loginUsername');
    const passwordInput = document.getElementById('loginPassword');
    const toggleBtn = document.getElementById('toggleLoginPassword');

    if (toggleBtn && passwordInput) {
        toggleBtn.addEventListener('click', () => {
             const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
             passwordInput.setAttribute('type', type);
             toggleBtn.textContent = type === 'password' ? 'Show' : 'Hide';
        });
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        loginError.classList.add('d-none');

        const username = usernameInput.value.trim();
        const password = passwordInput.value;

        if (!username || !password) {
            loginError.textContent = "Please enter both username and password.";
            loginError.classList.remove('d-none');
            return;
        }

        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Login failed. Check your credentials.');
            }

            const data = await response.json();
            
            // Store JWT token in localStorage
            localStorage.setItem("token", data.access_token);
            
            // Redirect user to dashboard.html
            window.location.href = 'dashboard.html';

        } catch (error) {
            loginError.textContent = error.message;
            loginError.classList.remove('d-none');
        }
    });
});
