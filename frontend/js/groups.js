// frontend/js/groups.js

let userDetails = null;
let activeGroupId = null;

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Authenticate user
    try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });

        if (response.ok) {
            userDetails = await response.json();
            document.getElementById('sidebarUsername').textContent = userDetails.username;
            loadGroups();
        } else {
            handle401Error(response);
        }
    } catch (error) {
        console.error('Error fetching user:', error);
    }

    // 2. Create Group listener
    const createGroupForm = document.getElementById('createGroupForm');
    if (createGroupForm) {
        createGroupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const group_name = document.getElementById('groupName').value.trim();
            const description = document.getElementById('groupDesc').value.trim();
            await createGroup(group_name, description);
        });
    }

    // 3. Search listener
    const exploreSearch = document.getElementById('exploreSearch');
    if (exploreSearch) {
        exploreSearch.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            document.querySelectorAll('#exploreGroupsList > div').forEach(card => {
                const name = card.querySelector('h5').textContent.toLowerCase();
                const desc = card.querySelector('p').textContent.toLowerCase();
                if (name.includes(query) || desc.includes(query)) {
                    card.classList.remove('d-none');
                } else {
                    card.classList.add('d-none');
                }
            });
        });
    }

    // 4. Leave Group listener
    const leaveGroupBtn = document.getElementById('leaveGroupBtn');
    if (leaveGroupBtn) {
        leaveGroupBtn.addEventListener('click', async () => {
            if (activeGroupId) {
                if (confirm("Are you sure you want to leave this study group?")) {
                    await leaveGroup(activeGroupId);
                }
            }
        });
    }
});

async function loadGroups() {
    const myGroupsList = document.getElementById('myGroupsList');
    const exploreGroupsList = document.getElementById('exploreGroupsList');

    try {
        const response = await fetch(`${API_BASE_URL}/groups`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        if (handle401Error(response)) return;
        if (response.ok) {
            const groups = await response.json();
            
            // Separate into joined (my groups) and unjoined (explore groups)
            const joinedGroups = groups.filter(g => g.is_member);
            const exploreGroups = groups.filter(g => !g.is_member);

            // Render My Groups
            if (joinedGroups.length === 0) {
                myGroupsList.innerHTML = `
                    <div class="col-12 text-center text-muted py-5 w-100">
                        <i class="bi bi-collection-fill fs-2 d-block mb-2 text-primary opacity-50"></i>
                        <span class="fw-bold">No study groups joined yet.</span>
                        <p class="small text-muted mt-1">Explore existing groups or create your own to study together!</p>
                    </div>
                `;
            } else {
                myGroupsList.innerHTML = joinedGroups.map(g => `
                    <div class="col-md-6">
                        <div class="group-card">
                            <span class="badge bg-success bg-opacity-10 text-success group-badge mb-2">My Group</span>
                            <h5 class="fw-bold text-dark text-truncate mb-1">${g.group_name}</h5>
                            <p class="text-muted small mb-3" style="height: 38px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">${g.description || 'No description provided.'}</p>
                            
                            <div class="d-flex align-items-center justify-content-between mb-3" style="font-size: 0.8rem;">
                                <span class="fw-bold text-muted"><i class="bi bi-people-fill"></i> ${g.member_count} members</span>
                                <span class="fw-bold text-success"><i class="bi bi-bar-chart-fill"></i> ${g.average_progress}% avg</span>
                            </div>
                            
                            <button class="btn btn-sm btn-primary w-100 rounded-pill fw-bold text-uppercase" style="font-size: 0.72rem;" onclick="openGroup(${g.id})">Open Group</button>
                        </div>
                    </div>
                `).join('');
            }

            // Render Explore Groups
            if (exploreGroups.length === 0) {
                exploreGroupsList.innerHTML = `
                    <div class="col-12 text-center text-muted py-5 w-100">
                        <i class="bi bi-compass fs-2 d-block mb-2 text-primary opacity-50"></i>
                        <span class="fw-bold">No other groups available.</span>
                        <p class="small text-muted mt-1">Be the first to start a group in this track!</p>
                    </div>
                `;
            } else {
                exploreGroupsList.innerHTML = exploreGroups.map(g => `
                    <div class="col-md-6">
                        <div class="group-card">
                            <span class="badge bg-primary bg-opacity-10 text-primary group-badge mb-2">Explore</span>
                            <h5 class="fw-bold text-dark text-truncate mb-1">${g.group_name}</h5>
                            <p class="text-muted small mb-3" style="height: 38px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">${g.description || 'No description provided.'}</p>
                            
                            <div class="d-flex align-items-center justify-content-between mb-3" style="font-size: 0.8rem;">
                                <span class="fw-bold text-muted"><i class="bi bi-people-fill"></i> ${g.member_count} members</span>
                                <span class="fw-bold text-success"><i class="bi bi-bar-chart-fill"></i> ${g.average_progress}% avg</span>
                            </div>
                            
                            <button class="btn btn-sm btn-outline-primary w-100 rounded-pill fw-bold text-uppercase" style="font-size: 0.72rem;" onclick="joinGroup(${g.id})">Join Group</button>
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Error loading groups:', error);
    }
}

async function createGroup(group_name, description) {
    const msgDiv = document.getElementById('createGroupMsg');
    msgDiv.innerHTML = '<div class="spinner-border text-primary spinner-border-sm"></div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/groups/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify({ group_name, description })
        });
        
        if (handle401Error(response)) return;
        
        if (response.ok) {
            const newGroup = await response.json();
            msgDiv.innerHTML = `<span class="text-success">Study Team created successfully!</span>`;
            document.getElementById('groupName').value = '';
            document.getElementById('groupDesc').value = '';
            
            // Reload lists
            await loadGroups();
            
            // Automatically open created group and select active tab
            setTimeout(() => {
                msgDiv.innerHTML = '';
                const myGroupsTab = document.getElementById('my-groups-tab');
                if (myGroupsTab) myGroupsTab.click();
                openGroup(newGroup.id);
            }, 1000);
        } else {
            const data = await response.json();
            msgDiv.innerHTML = `<span class="text-danger">${data.detail || 'Failed to create group.'}</span>`;
        }
    } catch (error) {
        msgDiv.innerHTML = '<span class="text-danger">Failed to create group. Network error.</span>';
    }
}

async function joinGroup(groupId) {
    try {
        const response = await fetch(`${API_BASE_URL}/groups/join/${groupId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (handle401Error(response)) return;

        if (response.ok) {
            alert('Successfully joined the study team!');
            await loadGroups();
            openGroup(groupId);
        } else {
            const data = await response.json();
            alert(data.detail || 'Failed to join group.');
        }
    } catch (error) {
        alert('Network error. Failed to join group.');
    }
}

async function leaveGroup(groupId) {
    try {
        const response = await fetch(`${API_BASE_URL}/groups/leave/${groupId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (handle401Error(response)) return;

        if (response.ok) {
            alert('Successfully left group!');
            
            // Close active group details panel
            activeGroupId = null;
            document.getElementById('groupActiveState').classList.add('d-none');
            document.getElementById('groupEmptyState').classList.remove('d-none');
            
            await loadGroups();
        } else {
            const data = await response.json();
            alert(data.detail || 'Failed to leave group.');
        }
    } catch (error) {
        alert('Network error. Failed to leave group.');
    }
}

async function openGroup(groupId) {
    activeGroupId = groupId;
    
    // Show active details state in right panel
    document.getElementById('groupEmptyState').classList.add('d-none');
    document.getElementById('groupActiveState').classList.remove('d-none');
    
    // Update active details
    try {
        const response = await fetch(`${API_BASE_URL}/groups/${groupId}`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        if (handle401Error(response)) return;
        if (response.ok) {
            const details = await response.json();
            
            document.getElementById('activeGroupName').textContent = details.group_name;
            document.getElementById('activeGroupOwner').textContent = `Owner: ${details.owner_username}`;
            document.getElementById('activeGroupDesc').textContent = details.description || 'No description provided.';
            document.getElementById('activeGroupProgress').textContent = `${details.average_progress}%`;
            document.getElementById('activeGroupMemberCount').textContent = details.member_count;
            document.getElementById('activeGroupMVP').textContent = details.most_active_member || 'None';
            
            // Roadmap Widget
            const roadmapWidget = document.getElementById('groupRoadmapWidget');
            if (details.shared_roadmap_title) {
                roadmapWidget.classList.remove('d-none');
                document.getElementById('widgetRoadmapTitle').textContent = details.shared_roadmap_title;
                document.getElementById('widgetRoadmapCompletion').textContent = `${details.shared_roadmap_completion}%`;
                document.getElementById('widgetRoadmapProgressBar').style.width = `${details.shared_roadmap_completion}%`;
                document.getElementById('widgetCurrentStage').textContent = details.current_stage || 'N/A';
                document.getElementById('widgetNextStage').textContent = details.next_stage || 'N/A';
            } else {
                roadmapWidget.classList.add('d-none');
            }

            // Load Leaderboard Members
            await loadGroupMembers(groupId, details.owner_id);
        }
    } catch (error) {
        console.error('Error fetching group details:', error);
    }
}

async function loadGroupMembers(groupId, ownerId) {
    const container = document.getElementById('activeGroupLeaderboard');
    container.innerHTML = '<tr><td colspan="5" class="text-center"><div class="spinner-border spinner-border-sm text-primary"></div></td></tr>';

    try {
        const response = await fetch(`${API_BASE_URL}/groups/${groupId}/members`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        if (handle401Error(response)) return;
        if (response.ok) {
            const members = await response.json();
            
            let html = '';
            let rank = 1;
            members.forEach(m => {
                // Owner action button (remove member)
                let actionBtn = '';
                const isCurrentGroupOwner = userDetails && userDetails.id === ownerId;
                const isSelf = userDetails && userDetails.id === m.user_id;

                if (isCurrentGroupOwner && !isSelf) {
                    actionBtn = `
                        <button class="btn btn-sm btn-outline-danger remove-member-btn px-2 py-1 fw-bold" onclick="removeMember(${groupId}, ${m.user_id}, '${m.username}')">
                            <i class="bi bi-person-x"></i>
                        </button>
                    `;
                }
                
                // Show trophy or rank style
                let rankDisplay = `#${rank}`;
                if (rank === 1) rankDisplay = '🥇';
                else if (rank === 2) rankDisplay = '🥈';
                else if (rank === 3) rankDisplay = '🥉';

                html += `
                    <tr>
                        <td class="fw-bold text-center" style="font-size: 0.9rem;">${rankDisplay}</td>
                        <td class="fw-bold text-dark text-truncate small" style="max-width: 100px;">
                            ${m.username} ${isSelf ? '<span class="text-primary small fw-semibold">(You)</span>' : ''}
                        </td>
                        <td class="fw-extrabold text-success small">${m.score}</td>
                        <td>
                            <div class="d-flex align-items-center" style="font-size: 0.72rem;">
                                <div class="progress me-2" style="height: 5px; width: 45px;">
                                    <div class="progress-bar bg-success" role="progressbar" style="width: ${m.progress}%"></div>
                                </div>
                                <span>${m.progress}%</span>
                            </div>
                        </td>
                        <td class="text-end">${actionBtn}</td>
                    </tr>
                `;
                rank++;
            });
            container.innerHTML = html;
        }
    } catch (error) {
        console.error('Error fetching members:', error);
        container.innerHTML = '<tr><td colspan="5" class="text-danger text-center">Failed to load leaderboard.</td></tr>';
    }
}

window.removeMember = async function (groupId, userId, username) {
    if (confirm(`Are you sure you want to remove ${username} from the study group?`)) {
        try {
            const response = await fetch(`${API_BASE_URL}/groups/${groupId}/member/${userId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${getToken()}` }
            });

            if (handle401Error(response)) return;

            if (response.ok) {
                alert(`${username} has been removed successfully.`);
                // Refresh group view
                openGroup(groupId);
            } else {
                const data = await response.json();
                alert(data.detail || 'Failed to remove member.');
            }
        } catch (error) {
            alert('Network error. Failed to remove member.');
        }
    }
}
