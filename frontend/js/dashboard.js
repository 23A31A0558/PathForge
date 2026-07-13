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
            
            if (!data.onboarding_completed) {
                window.location.href = 'welcome.html';
                return;
            } else {
                // Initialize Shared Journey Manager
                initJourneyManager(async (newRoadmapId) => {
                    fetchDashboardScore();
                });

                // Check if user has placement prep profile and no active career roadmap
                try {
                    const placementResp = await fetch(`${API_BASE_URL}/placement-profile`, {
                        headers: { 'Authorization': `Bearer ${getToken()}` }
                    });
                    if (placementResp.ok && !data.selected_roadmap_id) {
                        const continueBtn = document.querySelector('.progress-container a.btn-primary');
                        if (continueBtn) {
                            continueBtn.setAttribute('href', 'placement_dashboard.html');
                            continueBtn.textContent = 'Continue Placement Prep';
                        }
                        const scoreSub = document.querySelector('.progress-container p');
                        if (scoreSub) {
                            scoreSub.textContent = 'Keep preparing for your upcoming campus placements!';
                        }
                    }
                } catch (pe) {
                    console.error("Error checking placement profile:", pe);
                }
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
