// frontend/js/welcome.js

document.addEventListener("DOMContentLoaded", async () => {
    const token = getToken();
    if (!token) {
        window.location.href = "login.html";
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users/status`, {
            headers: { "Authorization": "Bearer " + token }
        });

        if (response.ok) {
            const data = await response.json();
            if (data.onboarding_completed) {
                // If onboarding is already completed, check if they have a placement profile
                const pResp = await fetch(`${API_BASE_URL}/placement-profile`, {
                    headers: { "Authorization": "Bearer " + token }
                });
                if (pResp.ok) {
                    window.location.href = "placement_dashboard.html";
                } else {
                    window.location.href = "dashboard.html";
                }
            }
        } else {
            handle401Error(response);
        }
    } catch (error) {
        console.error("Error checking onboarding status:", error);
    }
});
