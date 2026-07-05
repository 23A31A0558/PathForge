// frontend/js/dashboard.js

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById('userDisplay').textContent = data.username;
            document.getElementById('welcomeName').textContent = data.username;
            
            if (!data.questionnaire_completed) {
                window.location.href = 'questionnaire.html';
            } else {
                fetchDashboardScore();
            }
        } else {
            handle401Error(response);
        }
    } catch (error) {
        console.error('Error fetching user:', error);
    }
});

async function fetchDashboardScore() {
    try {
        const response = await fetch(`${API_BASE_URL}/progress/score`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        
        if (handle401Error(response)) return;
        
        if (response.ok) {
            const data = await response.json();
            document.getElementById('dashboardScore').textContent = data.score;
        }
    } catch (error) {
        console.error('Error fetching score:', error);
    }
}
