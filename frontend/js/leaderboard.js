// frontend/js/leaderboard.js

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById('userDisplay').textContent = data.username;
            loadLeaderboard('global');
        } else {
            handle401Error(response);
        }
    } catch (error) {
        console.error('Error fetching user:', error);
    }
});

// Event listeners for radio buttons
document.getElementById('btnGlobal').addEventListener('click', () => switchLeaderboard('global'));
document.getElementById('btnBackend').addEventListener('click', () => switchLeaderboard('roadmap/backend'));
document.getElementById('btnFrontend').addEventListener('click', () => switchLeaderboard('roadmap/frontend'));
document.getElementById('btnAI').addEventListener('click', () => switchLeaderboard('roadmap/ai'));

window.switchLeaderboard = function(type) {
    loadLeaderboard(type);
};

async function loadLeaderboard(type) {
    const tableBody = document.getElementById('leaderboardBody');
    const loadingIndicator = document.getElementById('loadingIndicator');
    
    tableBody.innerHTML = '';
    loadingIndicator.classList.remove('d-none');
    
    try {
        const response = await fetch(`${API_BASE_URL}/leaderboard/${type}`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        
        loadingIndicator.classList.add('d-none');
        
        if (handle401Error(response)) return;
        
        if (response.ok) {
            const data = await response.json();
            renderTable(data);
        } else {
            console.error('Failed to fetch leaderboard data');
            tableBody.innerHTML = '<tr><td colspan="4" class="text-danger py-4">Failed to load data.</td></tr>';
        }
    } catch (error) {
        loadingIndicator.classList.add('d-none');
        console.error('Error:', error);
        tableBody.innerHTML = '<tr><td colspan="4" class="text-danger py-4">Error loading data.</td></tr>';
    }
}

function renderTable(data) {
    const tableBody = document.getElementById('leaderboardBody');
    tableBody.innerHTML = '';
    
    if (!data || data.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="4" class="text-muted py-4">No users found.</td></tr>';
        return;
    }
    
    data.forEach(user => {
        let rankClass = 'rank-other';
        if (user.rank === 1) rankClass = 'rank-1';
        else if (user.rank === 2) rankClass = 'rank-2';
        else if (user.rank === 3) rankClass = 'rank-3';
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <span class="rank-badge ${rankClass}">${user.rank}</span>
            </td>
            <td class="fw-semibold text-dark fs-5">${user.username}</td>
            <td>
                <span class="fw-bold" style="color: var(--accent-color); font-size: 1.1rem;">${user.score}</span> 
                <span class="text-muted small">pts</span>
            </td>
            <td>
                <div class="d-flex align-items-center justify-content-center">
                    <div class="progress-bar-custom flex-grow-1 mx-3">
                        <div class="progress-bar-fill" style="width: 0%;" data-width="${user.progress_percentage}%"></div>
                    </div>
                    <span class="text-muted small fw-medium" style="min-width: 45px">${user.progress_percentage}%</span>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });

    // Trigger animation for progress bars
    setTimeout(() => {
        document.querySelectorAll('.progress-bar-fill').forEach(bar => {
            bar.style.width = bar.getAttribute('data-width');
        });
    }, 50);
}
