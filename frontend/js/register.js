// frontend/js/register.js

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    if (!registerForm) return;

    const registerMessage = document.getElementById('registerMessage');
    const usernameInput = document.getElementById('registerUsername');
    const emailInput = document.getElementById('registerEmail');
    const passwordInput = document.getElementById('registerPassword');
    const toggleBtn = document.getElementById('toggleRegisterPassword');

    if (toggleBtn && passwordInput) {
        toggleBtn.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            toggleBtn.textContent = type === 'password' ? 'Show' : 'Hide';
        });
    }

    const isValidEmail = (email) => {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    };

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        registerMessage.classList.add('d-none');
        registerMessage.classList.remove('alert-success', 'alert-danger');

        const username = usernameInput.value.trim();
        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!username || !email || !password || !isValidEmail(email)) {
            registerMessage.textContent = 'Please fill out all fields correctly.';
            registerMessage.classList.add('alert-danger');
            registerMessage.classList.remove('d-none');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Registration failed');
            }

            registerMessage.textContent = 'Account created successfully! Redirecting to login...';
            registerMessage.classList.add('alert-success');
            registerMessage.classList.remove('d-none');
            
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 1500);

        } catch (error) {
            registerMessage.textContent = error.message;
            registerMessage.classList.add('alert-danger');
            registerMessage.classList.remove('d-none');
        }
    });
});
