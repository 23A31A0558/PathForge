// frontend/js/placement_questionnaire.js

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("placementQuestionnaireForm");
    const formError = document.getElementById("formError");
    const submitBtn = document.getElementById("submitBtn");

    const questionnaireContent = document.getElementById('questionnaireContent');
    const aiLoadingContainer = document.getElementById('aiLoadingContainer');
    const aiFailureContainer = document.getElementById('aiFailureContainer');
    const aiErrorMessage = document.getElementById('aiErrorMessage');

    const retryBtn = document.getElementById('retryBtn');
    const backToFormBtn = document.getElementById('backToFormBtn');

    let appState = 'QUESTIONNAIRE'; // QUESTIONNAIRE, GENERATING, FAILED
    let isPollingActive = false;
    let pollTimeout = null;
    let consecutiveErrors = 0;

    let currentStepIndex = 0;
    let currentProgress = 0;
    let animationInterval = null;

    const stepIds = [
        'step_goals',
        'step_skills',
        'step_tech',
        'step_resources',
        'step_milestones',
        'step_projects',
        'step_quizzes',
        'step_finalize'
    ];

    const stepElements = {};
    stepIds.forEach(id => {
        stepElements[id] = document.getElementById(id);
    });

    const stepFocuses = {
        'step_goals': 'Aligning with Target Companies',
        'step_skills': 'Evaluating Aptitude & DSA Competencies',
        'step_tech': 'Ordering Chronologically Easy to Hard',
        'step_resources': 'Matching Curated Placement Resources',
        'step_milestones': 'Structuring Learning Path Phases',
        'step_projects': 'Incorporating Mock Interview Checkpoints',
        'step_quizzes': 'Injecting Assessment Questions',
        'step_finalize': 'Publishing Placement Roadmap'
    };

    function showView(el) {
        if (!el) return;
        el.classList.remove('d-none');
        setTimeout(() => {
            el.style.opacity = '1';
        }, 50);
    }

    function hideView(el) {
        if (!el) return;
        el.style.opacity = '0';
        el.classList.add('d-none');
    }

    function crossFadeViews(fromEl, toEl) {
        if (fromEl) {
            fromEl.style.opacity = '0';
            setTimeout(() => {
                fromEl.classList.add('d-none');
                showView(toEl);
            }, 300);
        } else {
            showView(toEl);
        }
    }

    function transitionTo(newState, errorMsg = '') {
        const fromState = appState;
        appState = newState;

        if (newState === 'QUESTIONNAIRE') {
            stopStatusPolling();
            if (animationInterval) clearInterval(animationInterval);
            submitBtn.disabled = false;
            submitBtn.innerHTML = "Generate Placement Roadmap";
            
            if (fromState === 'GENERATING' || fromState === 'FAILED') {
                const fromEl = fromState === 'FAILED' ? aiFailureContainer : aiLoadingContainer;
                crossFadeViews(fromEl, questionnaireContent);
            } else {
                showView(questionnaireContent);
                hideView(aiLoadingContainer);
                hideView(aiFailureContainer);
            }
        } else if (newState === 'GENERATING') {
            submitBtn.disabled = true;
            if (fromState === 'QUESTIONNAIRE') {
                hideView(questionnaireContent);
                showView(aiLoadingContainer);
                hideView(aiFailureContainer);
                startLoadingAnimation();
            } else {
                const fromEl = fromState === 'FAILED' ? aiFailureContainer : questionnaireContent;
                crossFadeViews(fromEl, aiLoadingContainer);
                startLoadingAnimation();
            }
            startStatusPolling();
        } else if (newState === 'READY') {
            stopStatusPolling();
            // Redirect to roadmap page for placement
            window.location.href = "roadmap.html?type=placement";
        } else if (newState === 'FAILED') {
            stopStatusPolling();
            if (animationInterval) clearInterval(animationInterval);
            if (aiErrorMessage) {
                aiErrorMessage.textContent = errorMsg || "AI Placement Roadmap generation failed.";
            }
            hideView(aiLoadingContainer);
            crossFadeViews(aiLoadingContainer, aiFailureContainer);
        }
    }

    function resetLoadingState() {
        currentStepIndex = 0;
        currentProgress = 0;
        
        stepIds.forEach(id => {
            const el = stepElements[id];
            if (el) {
                el.className = 'step-item';
                const iconSpan = el.querySelector('.step-icon');
                if (iconSpan) iconSpan.innerHTML = '<i class="bi bi-circle"></i>';
            }
        });

        const bar = document.getElementById('loadingProgressBar');
        if (bar) bar.style.width = '0%';
        const percentText = document.getElementById('progressPercent');
        if (percentText) percentText.textContent = '0%';

        if (animationInterval) clearInterval(animationInterval);
        stopStatusPolling();
    }

    function startLoadingAnimation() {
        resetLoadingState();

        // Target progress points for animation milestones
        const progressSteps = [12, 25, 37, 50, 62, 75, 87, 100];
        
        // Mark first step as active
        activeStep(stepIds[0]);

        animationInterval = setInterval(() => {
            if (currentStepIndex >= stepIds.length) {
                clearInterval(animationInterval);
                return;
            }

            const targetProgress = progressSteps[currentStepIndex];
            if (currentProgress < targetProgress) {
                currentProgress += 1;
                const bar = document.getElementById('loadingProgressBar');
                if (bar) bar.style.width = `${currentProgress}%`;
                const percentText = document.getElementById('progressPercent');
                if (percentText) percentText.textContent = `${currentProgress}%`;
            } else {
                // Complete current step
                completeStep(stepIds[currentStepIndex]);
                currentStepIndex++;
                if (currentStepIndex < stepIds.length) {
                    activeStep(stepIds[currentStepIndex]);
                }
            }
        }, 150);
    }

    function activeStep(id) {
        const el = stepElements[id];
        if (el) {
            el.className = 'step-item active';
            const iconSpan = el.querySelector('.step-icon');
            if (iconSpan) iconSpan.innerHTML = '<span class="spinner-border spinner-border-sm text-primary" role="status"></span>';
            
            const focusVal = document.getElementById('currentFocusVal');
            if (focusVal && stepFocuses[id]) {
                focusVal.textContent = stepFocuses[id];
            }
        }
    }

    function completeStep(id) {
        const el = stepElements[id];
        if (el) {
            el.className = 'step-item completed';
            const iconSpan = el.querySelector('.step-icon');
            if (iconSpan) iconSpan.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i>';
        }
    }

    function startStatusPolling() {
        isPollingActive = true;
        consecutiveErrors = 0;
        runPoll();
    }

    function stopStatusPolling() {
        isPollingActive = false;
        if (pollTimeout) {
            clearTimeout(pollTimeout);
            pollTimeout = null;
        }
        consecutiveErrors = 0;
    }

    async function runPoll() {
        if (!isPollingActive) return;

        try {
            const token = getToken();
            if (!token) {
                transitionTo('QUESTIONNAIRE');
                return;
            }

            const res = await fetch(`${API_BASE_URL}/roadmap/status`, {
                headers: { "Authorization": "Bearer " + token }
            });

            if (!isPollingActive) return;

            if (handle401Error(res)) {
                transitionTo('QUESTIONNAIRE');
                return;
            }

            if (res.ok) {
                consecutiveErrors = 0;
                const data = await res.json();

                if (data.status === 'READY') {
                    transitionTo('READY');
                } else if (data.status === 'FAILED') {
                    transitionTo('FAILED', data.error_message || "AI placement roadmap generation failed.");
                } else {
                    scheduleNextPoll(2000);
                }
            } else {
                throw new Error(`Server status code ${res.status}`);
            }
        } catch (err) {
            if (!isPollingActive) return;
            console.error("Polling error:", err);
            consecutiveErrors++;
            if (consecutiveErrors >= 5) {
                transitionTo('FAILED', "Connection lost. Please check your network and try again.");
            } else {
                scheduleNextPoll(3000);
            }
        }
    }

    function scheduleNextPoll(delay) {
        if (!isPollingActive) return;
        if (pollTimeout) clearTimeout(pollTimeout);
        pollTimeout = setTimeout(runPoll, delay);
    }

    async function submitPlacementQuestionnaire() {
        formError.classList.add("d-none");

        // Validate Radio buttons
        const selectedAptitude = document.querySelector("input[name='aptitude_level']:checked")?.value;
        if (!selectedAptitude) {
            document.getElementById("aptError").classList.remove("d-none");
            return;
        }

        const selectedDSA = document.querySelector("input[name='dsa_level']:checked")?.value;
        if (!selectedDSA) {
            document.getElementById("dsaError").classList.remove("d-none");
            return;
        }

        const checkedCompanies = Array.from(document.querySelectorAll("input[name='companies']:checked")).map(el => el.value);
        if (checkedCompanies.length === 0) {
            document.getElementById("companyError").classList.remove("d-none");
            return;
        }

        const selectedTimeline = document.querySelector("input[name='timeline']:checked")?.value;
        if (!selectedTimeline) {
            document.getElementById("timelineError").classList.remove("d-none");
            return;
        }

        // Standard validation check
        if (!form.checkValidity()) {
            form.classList.add("was-validated");
            return;
        }

        form.classList.add("was-validated");

        // Gather variables
        const name = document.getElementById("inputName").value.trim();
        const college = document.getElementById("inputCollege").value.trim();
        const year = document.getElementById("inputYear").value;
        const branch = document.getElementById("inputBranch").value.trim();

        const payload = {
            name: name,
            college: college,
            year: year,
            branch: branch,
            aptitude_level: selectedAptitude,
            dsa_level: selectedDSA,
            target_companies: checkedCompanies,
            timeline: selectedTimeline
        };

        transitionTo('GENERATING');

        try {
            const response = await fetch(`${API_BASE_URL}/placement-profile`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + getToken()
                },
                body: JSON.stringify(payload)
            });

            if (handle401Error(response)) return;

            const data = await response.json();
            if (!response.ok) {
                transitionTo('FAILED', data.detail || "An error occurred while saving placement onboarding details.");
            }
        } catch (error) {
            console.error(error);
            transitionTo('FAILED', "Network error. Please make sure the backend is active.");
        }
    }

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        submitPlacementQuestionnaire();
    });

    if (retryBtn) {
        retryBtn.onclick = () => {
            submitPlacementQuestionnaire();
        };
    }

    if (backToFormBtn) {
        backToFormBtn.onclick = () => {
            transitionTo('QUESTIONNAIRE');
        };
    }

    // Custom Card/Chip Toggling Logic
    const formChecks = document.querySelectorAll(".form-check");
    formChecks.forEach(card => {
        const input = card.querySelector("input");
        if (!input) return;

        card.setAttribute("tabindex", "0");

        if (input.checked) {
            card.classList.add("selected");
        }

        card.addEventListener("click", (e) => {
            e.preventDefault();
            
            if (input.type === "checkbox") {
                input.checked = !input.checked;
                input.dispatchEvent(new Event("change", { bubbles: true }));
            } else if (input.type === "radio") {
                const wasChecked = input.checked;
                if (!wasChecked) {
                    const peers = document.querySelectorAll(`input[name="${input.name}"]`);
                    peers.forEach(p => {
                        p.checked = false;
                        p.closest(".form-check")?.classList.remove("selected");
                    });
                    input.checked = true;
                }
                input.dispatchEvent(new Event("change", { bubbles: true }));
            }
        });

        input.addEventListener("change", () => {
            if (input.type === "checkbox") {
                card.classList.toggle("selected", input.checked);
            } else if (input.type === "radio") {
                const peers = document.querySelectorAll(`input[name="${input.name}"]`);
                peers.forEach(p => {
                    p.closest(".form-check")?.classList.toggle("selected", p.checked);
                });
            }
        });

        card.addEventListener("keydown", (e) => {
            if (e.key === " " || e.key === "Enter") {
                e.preventDefault();
                card.click();
            }
        });
    });
});
