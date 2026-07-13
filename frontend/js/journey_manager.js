// frontend/js/journey_manager.js

let userDetails = null;
let roadmapData = [];
let onSwitchCallback = null;

async function initJourneyManager(callback) {
    onSwitchCallback = callback;
    
    // Inject Modals into DOM if they don't exist
    injectModalHTML();
    
    // Setup Top Bar Actions
    setupTopBarActions();
    
    // Initial fetch and build
    await refreshJourneyManager();
}

function setupTopBarActions() {
    const renameBtn = document.getElementById('renameJourneyBtn');
    const deleteBtn = document.getElementById('deleteJourneyBtn');
    const archiveBtn = document.getElementById('archiveJourneyBtn');
    const recoverBtn = document.getElementById('recoverJourneyBtn');
    
    if (renameBtn) {
        renameBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            if (userDetails && userDetails.selected_roadmap_id) {
                const current = roadmapData.find(r => r.id === userDetails.selected_roadmap_id);
                const title = current ? current.title : "";
                await renameJourney(userDetails.selected_roadmap_id, title);
            }
        });
    }
    if (deleteBtn) {
        deleteBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            if (userDetails && userDetails.selected_roadmap_id) {
                const current = roadmapData.find(r => r.id === userDetails.selected_roadmap_id);
                const title = current ? current.title : "";
                await deleteJourney(userDetails.selected_roadmap_id, title);
            }
        });
    }
    if (archiveBtn) {
        archiveBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            if (userDetails && userDetails.selected_roadmap_id) {
                await archiveJourney(userDetails.selected_roadmap_id);
            }
        });
    }
    if (recoverBtn) {
        recoverBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            if (userDetails && userDetails.selected_roadmap_id) {
                await archiveJourney(userDetails.selected_roadmap_id);
            }
        });
    }
}

async function refreshJourneyManager() {
    try {
        const token = getToken();
        if (!token) return;

        // Fetch User and Roadmap list concurrently using the new endpoint `/roadmaps/list`
        const [userResp, roadmapResp] = await Promise.all([
            fetch(`${API_BASE_URL}/users/me`, { headers: { 'Authorization': `Bearer ${token}` } }),
            fetch(`${API_BASE_URL}/roadmaps/list`, { headers: { 'Authorization': `Bearer ${token}` } })
        ]);

        if (userResp.ok && roadmapResp.ok) {
            userDetails = await userResp.json();
            const list = await roadmapResp.json();
            
            // Map the API structure to matching model structure used in JS
            roadmapData = list.map(r => ({
                id: r.id,
                title: r.title,
                description: r.description,
                progress: r.progress,
                is_archived: r.archived_status,
                created_at: r.created_date,
                updated_at: r.updated_date,
                type: r.roadmap_type
            }));
            
            // Empty State Control
            const noJourneyEmptyState = document.getElementById('noJourneyEmptyState');
            const journeyContentContainer = document.getElementById('journeyContentContainer');
            
            if (roadmapData.length === 0) {
                if (noJourneyEmptyState) {
                    noJourneyEmptyState.classList.remove('d-none');
                    noJourneyEmptyState.classList.add('d-flex');
                }
                if (journeyContentContainer) journeyContentContainer.classList.add('d-none');
            } else {
                if (noJourneyEmptyState) {
                    noJourneyEmptyState.classList.remove('d-flex');
                    noJourneyEmptyState.classList.add('d-none');
                }
                if (journeyContentContainer) journeyContentContainer.classList.remove('d-none');
            }
            
            buildDropdownMenu();
            populateManageModal();
            populateArchivedModal();
            updateTopBarActionVisibilities();
        } else {
            console.error("Error fetching journey data");
        }
    } catch (err) {
        console.error("Failed to load journey manager details:", err);
    }
}

function updateTopBarActionVisibilities() {
    const archiveBtn = document.getElementById('archiveJourneyBtn');
    const recoverBtn = document.getElementById('recoverJourneyBtn');
    if (!archiveBtn || !recoverBtn) return;
    
    if (userDetails && userDetails.selected_roadmap_id) {
        const active = roadmapData.find(r => r.id === userDetails.selected_roadmap_id);
        if (active && active.is_archived) {
            archiveBtn.style.display = 'none';
            recoverBtn.style.display = 'block';
        } else {
            archiveBtn.style.display = 'block';
            recoverBtn.style.display = 'none';
        }
    } else {
        archiveBtn.style.display = 'none';
        recoverBtn.style.display = 'none';
    }
}

function buildDropdownMenu() {
    const trackSwitcherBtn = document.getElementById('trackSwitcherBtn');
    const trackSwitcherMenu = document.getElementById('trackSwitcherMenu');
    
    if (!trackSwitcherBtn || !trackSwitcherMenu) return;
    
    trackSwitcherMenu.innerHTML = '';
    
    // Filter active roadmaps (not archived)
    const activeRoadmaps = roadmapData.filter(r => !r.is_archived);
    
    // Determine active selected roadmap
    let activeRoadmap = null;
    if (userDetails && userDetails.selected_roadmap_id) {
        activeRoadmap = roadmapData.find(r => r.id === userDetails.selected_roadmap_id);
    }
    
    // Auto-select fallback if currently active roadmap is archived, deleted, or not set
    if ((!activeRoadmap || activeRoadmap.is_archived) && activeRoadmaps.length > 0) {
        // Fallback to first available active roadmap
        const sortedRoadmaps = [...activeRoadmaps].sort((a, b) => b.id - a.id);
        activeRoadmap = sortedRoadmaps[0];
        selectTrackSilently(activeRoadmap.id);
    }
    
    // Update Button Text
    if (activeRoadmap) {
        trackSwitcherBtn.innerText = `${activeRoadmap.title}`;
    } else {
        trackSwitcherBtn.innerText = "Select Journey";
    }
    
    // Create scrollable container elements
    const scrollLi = document.createElement('li');
    const scrollUl = document.createElement('ul');
    scrollUl.className = 'dropdown-menu-scrollable-list list-unstyled p-0 m-0';
    scrollLi.appendChild(scrollUl);
    trackSwitcherMenu.appendChild(scrollLi);
    
    // Populate active roadmaps list inside scrollUl
    if (activeRoadmaps.length === 0) {
        const li = document.createElement('li');
        li.innerHTML = `<span class="dropdown-item-text text-muted small fw-semibold">No active journeys. Create one!</span>`;
        scrollUl.appendChild(li);
    } else {
        activeRoadmaps.forEach(r => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            const isActive = activeRoadmap && r.id === activeRoadmap.id;
            a.className = `dropdown-item fw-semibold d-flex justify-content-between align-items-center ${isActive ? 'active' : ''}`;
            a.href = '#';
            a.innerHTML = `
                <span>${r.title}</span>
                ${isActive ? '<i class="bi bi-check-lg ms-2"></i>' : ''}
            `;
            
            a.addEventListener('click', async (e) => {
                e.preventDefault();
                await selectTrack(r.id);
            });
            
            li.appendChild(a);
            scrollUl.appendChild(li);
        });
    }
    
    // Setup listener to scroll active item into view when dropdown opens
    const parentDropdown = trackSwitcherBtn.closest('.dropdown');
    if (parentDropdown && !parentDropdown.dataset.dropdownListenerAttached) {
        parentDropdown.addEventListener('shown.bs.dropdown', () => {
            const scrollList = parentDropdown.querySelector('.dropdown-menu-scrollable-list');
            if (scrollList) {
                const activeItem = scrollList.querySelector('.dropdown-item.active');
                if (activeItem) {
                    activeItem.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
                }
            }
        });
        parentDropdown.dataset.dropdownListenerAttached = 'true';
    }
    
    // Add divider directly to main trackSwitcherMenu (outside scrollUl)
    const dividerLi = document.createElement('li');
    dividerLi.innerHTML = `<hr class="dropdown-divider">`;
    trackSwitcherMenu.appendChild(dividerLi);
    
    // Add "➕ Add New Learning Journey" action directly to trackSwitcherMenu
    const addLi = document.createElement('li');
    const addA = document.createElement('a');
    addA.href = 'questionnaire.html';
    
    // Enforce 20-limit check
    if (activeRoadmaps.length >= 20) {
        addA.className = "dropdown-item fw-bold text-muted disabled";
        addA.style.opacity = "0.5";
        addA.style.pointerEvents = "none";
        addA.innerHTML = `<i class="bi bi-plus-circle-fill me-2 text-muted"></i> Add Journey (Limit Reached: 20)`;
        addA.setAttribute('title', "Maximum roadmap limit of 20 reached.");
    } else {
        addA.className = "dropdown-item fw-bold text-primary";
        addA.innerHTML = `<i class="bi bi-plus-circle-fill me-2"></i> Add New Learning Journey`;
    }
    
    addLi.appendChild(addA);
    trackSwitcherMenu.appendChild(addLi);
    
    // Add "📦 Archived Roadmaps" action directly to trackSwitcherMenu
    const archiveLi = document.createElement('li');
    const archiveA = document.createElement('a');
    archiveA.className = "dropdown-item fw-semibold text-secondary";
    archiveA.href = "#";
    archiveA.innerHTML = `<i class="bi bi-archive-fill me-2"></i> Archived Roadmaps`;
    archiveA.addEventListener('click', (e) => {
        e.preventDefault();
        const modal = new bootstrap.Modal(document.getElementById('archivedRoadmapsModal'));
        modal.show();
    });
    archiveLi.appendChild(archiveA);
    trackSwitcherMenu.appendChild(archiveLi);
    
    // Add "⚙ Manage Roadmaps" action directly to trackSwitcherMenu
    const manageLi = document.createElement('li');
    const manageA = document.createElement('a');
    manageA.className = "dropdown-item fw-semibold text-secondary";
    manageA.href = "#";
    manageA.innerHTML = `<i class="bi bi-gear-fill me-2"></i> Manage Roadmaps`;
    manageA.addEventListener('click', (e) => {
        e.preventDefault();
        const modal = new bootstrap.Modal(document.getElementById('manageRoadmapsModal'));
        modal.show();
    });
    manageLi.appendChild(manageA);
    trackSwitcherMenu.appendChild(manageLi);
}

async function selectTrackSilently(roadmapId) {
    try {
        const token = getToken();
        await fetch(`${API_BASE_URL}/roadmap/select/${roadmapId}`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            }
        });
        if (userDetails) {
            userDetails.selected_roadmap_id = roadmapId;
        }
    } catch (e) {
        console.error("Silent track selection failed:", e);
    }
}

async function selectTrack(roadmapId) {
    try {
        const token = getToken();
        const response = await fetch(`${API_BASE_URL}/roadmap/select/${roadmapId}`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            }
        });
        
        if (handle401Error(response)) return;
        
        if (response.ok) {
            if (userDetails) {
                userDetails.selected_roadmap_id = roadmapId;
            }
            await refreshJourneyManager();
            if (onSwitchCallback) {
                await onSwitchCallback(roadmapId);
            }
            
            // Programmatically hide the dropdown
            const trackSwitcherBtn = document.getElementById('trackSwitcherBtn');
            if (trackSwitcherBtn) {
                const dropdownInstance = bootstrap.Dropdown.getInstance(trackSwitcherBtn);
                if (dropdownInstance) {
                    dropdownInstance.hide();
                }
            }
        }
    } catch (error) {
        console.error("Error selecting track:", error);
    }
}

function populateManageModal() {
    const listContainer = document.getElementById('manageRoadmapsList');
    if (!listContainer) return;
    
    listContainer.innerHTML = '';
    const activeRoadmaps = roadmapData.filter(r => !r.is_archived);
    
    if (activeRoadmaps.length === 0) {
        listContainer.innerHTML = `<p class="text-muted text-center py-3">No active learning journeys found.</p>`;
        return;
    }
    
    activeRoadmaps.forEach(r => {
        const card = document.createElement('div');
        card.className = "card border-light shadow-sm p-3 d-flex flex-row justify-content-between align-items-center";
        card.style.borderRadius = "12px";
        
        const dateStr = r.created_at ? new Date(r.created_at).toLocaleDateString() : 'N/A';
        
        card.innerHTML = `
            <div class="text-truncate me-3" style="text-align: left;">
                <h6 class="fw-bold mb-1 text-truncate">${r.title}</h6>
                <small class="text-muted">Created: ${dateStr}</small>
            </div>
            <div class="d-flex gap-1 flex-shrink-0">
                <button class="btn btn-sm btn-outline-primary py-1 px-2 rounded-circle" title="Rename" onclick="renameJourney(${r.id}, '${r.title.replace(/'/g, "\\'")}')">
                    <i class="bi bi-pencil-fill"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary py-1 px-2 rounded-circle" title="Archive" onclick="archiveJourney(${r.id})">
                    <i class="bi bi-archive-fill"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger py-1 px-2 rounded-circle" title="Delete" onclick="deleteJourney(${r.id}, '${r.title.replace(/'/g, "\\'")}')">
                    <i class="bi bi-trash-fill"></i>
                </button>
            </div>
        `;
        listContainer.appendChild(card);
    });
}

function populateArchivedModal() {
    const listContainer = document.getElementById('archivedRoadmapsList');
    if (!listContainer) return;
    
    listContainer.innerHTML = '';
    const archivedRoadmaps = roadmapData.filter(r => r.is_archived);
    
    if (archivedRoadmaps.length === 0) {
        listContainer.innerHTML = `<p class="text-muted text-center py-3">No archived learning journeys found.</p>`;
        return;
    }
    
    archivedRoadmaps.forEach(r => {
        const card = document.createElement('div');
        card.className = "card border-light shadow-sm p-3 d-flex flex-row justify-content-between align-items-center";
        card.style.borderRadius = "12px";
        
        const dateStr = r.created_at ? new Date(r.created_at).toLocaleDateString() : 'N/A';
        
        card.innerHTML = `
            <div class="text-truncate me-3" style="text-align: left;">
                <h6 class="fw-bold mb-1 text-truncate text-secondary">${r.title} <span class="badge bg-secondary text-white ms-1" style="font-size: 0.65rem;">Archived</span></h6>
                <small class="text-muted">Created: ${dateStr}</small>
            </div>
            <div class="d-flex gap-1 flex-shrink-0">
                <button class="btn btn-sm btn-outline-primary py-1 px-2 rounded-circle" title="Rename" onclick="renameJourney(${r.id}, '${r.title.replace(/'/g, "\\'")}')">
                    <i class="bi bi-pencil-fill"></i>
                </button>
                <button class="btn btn-sm btn-outline-success py-1 px-2 rounded-circle" title="Unarchive" onclick="archiveJourney(${r.id})">
                    <i class="bi bi-arrow-up-right-circle-fill"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger py-1 px-2 rounded-circle" title="Delete" onclick="deleteJourney(${r.id}, '${r.title.replace(/'/g, "\\'")}')">
                    <i class="bi bi-trash-fill"></i>
                </button>
            </div>
        `;
        listContainer.appendChild(card);
    });
}

window.renameJourney = async function(id, currentTitle) {
    const newTitle = prompt("Enter new title for this learning journey:", currentTitle);
    if (newTitle === null) return; // Cancelled
    const trimmed = newTitle.trim();
    if (!trimmed) {
        alert("Title cannot be empty!");
        return;
    }
    
    try {
        const token = getToken();
        const response = await fetch(`${API_BASE_URL}/roadmap/rename/${id}`, {
            method: 'PUT',
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({ title: trimmed })
        });
        
        if (response.ok) {
            await refreshJourneyManager();
            if (userDetails && userDetails.selected_roadmap_id === id && onSwitchCallback) {
                await onSwitchCallback(id);
            }
        } else {
            const err = await response.json();
            alert("Error: " + (err.detail || "Failed to rename journey"));
        }
    } catch (e) {
        console.error(e);
        alert("Network error.");
    }
};

window.archiveJourney = async function(id) {
    try {
        const token = getToken();
        const response = await fetch(`${API_BASE_URL}/roadmap/archive/${id}`, {
            method: 'POST',
            headers: {
                "Authorization": "Bearer " + token
            }
        });
        
        if (response.ok) {
            await refreshJourneyManager();
            if (onSwitchCallback) {
                await onSwitchCallback(userDetails.selected_roadmap_id);
            }
        } else {
            alert("Failed to update archive status");
        }
    } catch (e) {
        console.error(e);
        alert("Network error.");
    }
};

window.deleteJourney = async function(id, title) {
    const confirmDelete = confirm(`Are you sure you want to permanently delete the learning journey: "${title}"?\n\nThis action is permanent and cannot be undone.`);
    if (!confirmDelete) return;
    
    try {
        const token = getToken();
        const response = await fetch(`${API_BASE_URL}/roadmap/delete/${id}`, {
            method: 'DELETE',
            headers: {
                "Authorization": "Bearer " + token
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            await refreshJourneyManager();
            if (onSwitchCallback) {
                await onSwitchCallback(data.selected_roadmap_id);
            }
        } else {
            alert("Failed to delete journey");
        }
    } catch (e) {
        console.error(e);
        alert("Network error.");
    }
};

function injectModalHTML() {
    if (document.getElementById('manageRoadmapsModal')) return;
    
    const manageModalHtml = `
        <div class="modal fade" id="manageRoadmapsModal" tabindex="-1" aria-labelledby="manageRoadmapsModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content shadow border-0" style="border-radius: 16px;">
                    <div class="modal-header border-bottom-0 pt-4 px-4">
                        <h5 class="modal-title fw-bold" id="manageRoadmapsModalLabel" style="color: var(--text-color);">
                            <i class="bi bi-gear-fill me-2 text-primary"></i>Manage Learning Journeys
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body px-4 pb-4">
                        <div id="manageRoadmapsList" class="d-flex flex-column gap-3">
                            <!-- Populated dynamically -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    const archivedModalHtml = `
        <div class="modal fade" id="archivedRoadmapsModal" tabindex="-1" aria-labelledby="archivedRoadmapsModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content shadow border-0" style="border-radius: 16px;">
                    <div class="modal-header border-bottom-0 pt-4 px-4">
                        <h5 class="modal-title fw-bold" id="archivedRoadmapsModalLabel" style="color: var(--text-color);">
                            <i class="bi bi-archive-fill me-2 text-secondary"></i>Archived Journeys
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body px-4 pb-4">
                        <div id="archivedRoadmapsList" class="d-flex flex-column gap-3">
                            <!-- Populated dynamically -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    const container = document.createElement('div');
    container.innerHTML = manageModalHtml + archivedModalHtml;
    document.body.appendChild(container);
}
