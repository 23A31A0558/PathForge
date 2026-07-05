// frontend/js/friends.js

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById('userDisplay').textContent = data.username;
            loadPendingRequests();
            loadFriendsProgress();
        } else {
            handle401Error(response);
        }
    } catch (error) {
        console.error('Error fetching user:', error);
    }
});

document.getElementById('addFriendForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const inputVal = document.getElementById('friendUsername').value.trim();
    const msgDiv = document.getElementById('addFriendMsg');
    
    let payload = {};
    if (!isNaN(inputVal) && inputVal !== "") {
        payload = { receiver_id: parseInt(inputVal) };
    } else {
        payload = { username: inputVal };
    }
    
    try {
        const res = await fetch(`${API_BASE_URL}/friends/request`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify(payload)
        });
        
        if (handle401Error(res)) return;
        
        const data = await res.json();
        if (res.ok) {
            msgDiv.innerHTML = `<span class="text-success">${data.message}</span>`;
            document.getElementById('friendUsername').value = '';
        } else {
            msgDiv.innerHTML = `<span class="text-danger">${data.detail}</span>`;
        }
    } catch (error) {
        msgDiv.innerHTML = `<span class="text-danger">Failed to send request.</span>`;
    }
});

async function loadPendingRequests() {
    const container = document.getElementById('pendingRequestsContainer');
    
    try {
        const res = await fetch(`${API_BASE_URL}/friends/requests`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        
        if (handle401Error(res)) return;
        
        if (res.ok) {
            const requests = await res.json();
            if (requests.length === 0) {
                container.innerHTML = '<div class="text-muted small text-center py-3">No pending requests.</div>';
                return;
            }
            
            let html = '';
            requests.forEach(req => {
                html += `
                    <div class="friend-list-item px-0">
                        <span class="fw-semibold text-dark">${req.username}</span>
                        <div>
                            <button class="btn btn-sm btn-success me-1 fw-medium" onclick="respondRequest(${req.id}, 'accept')">Accept</button>
                            <button class="btn btn-sm btn-outline-danger fw-medium" onclick="respondRequest(${req.id}, 'reject')">Reject</button>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }
    } catch (error) {
        container.innerHTML = '<div class="text-danger small">Error loading requests.</div>';
    }
}

window.respondRequest = async function(requestId, action) {
    try {
        const res = await fetch(`${API_BASE_URL}/friends/respond`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify({ request_id: requestId, action })
        });
        
        if (handle401Error(res)) return;
        
        if (res.ok) {
            loadPendingRequests();
            if (action === 'accept') {
                loadFriendsProgress();
            }
        } else {
            alert('Failed to respond to request.');
        }
    } catch (error) {
        console.error(error);
    }
};

async function loadFriendsProgress() {
    const container = document.getElementById('friendsProgressContainer');
    
    try {
        const res = await fetch(`${API_BASE_URL}/friends/progress`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        
        if (handle401Error(res)) return;
        
        if (res.ok) {
            const friends = await res.json();
            if (friends.length === 0) {
                container.innerHTML = '<tr><td colspan="4" class="text-muted text-center py-5">You have no friends on PathForge yet. Add some to join forces!</td></tr>';
                return;
            }
            
            let html = '';
            friends.forEach(f => {
                html += `
                    <tr>
                        <td class="fw-semibold text-dark">${f.username}</td>
                        <td>
                            <span class="badge bg-light text-dark border px-2 py-1 text-capitalize">${f.roadmap_type}</span>
                        </td>
                        <td>
                            <span class="fw-bold" style="color: var(--accent-color);">${f.score}</span> 
                            <span class="text-muted small">pts</span>
                        </td>
                        <td>
                            <div class="d-flex align-items-center">
                                <div class="progress-bar-custom me-2">
                                    <div class="progress-bar-fill" style="width: ${f.progress_percentage}%"></div>
                                </div>
                                <span class="small fw-medium text-muted">${f.progress_percentage}%</span>
                            </div>
                        </td>
                    </tr>
                `;
            });
            container.innerHTML = html;
        }
    } catch (error) {
        container.innerHTML = '<tr><td colspan="4" class="text-danger text-center py-4">Error loading friends.</td></tr>';
    }
}
