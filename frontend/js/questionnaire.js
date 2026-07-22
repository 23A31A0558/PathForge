// frontend/js/questionnaire.js

document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('roadmapQuestionnaireForm');
    const formError = document.getElementById('formError');
    const submitBtn = document.getElementById('submitBtn');

    // 1. References to containers
    const questionnaireContent = document.getElementById('questionnaireContent');
    const aiLoadingContainer = document.getElementById('aiLoadingContainer');
    const aiFailureContainer = document.getElementById('aiFailureContainer');

    // Step configuration
    const stepElements = {
        goals: document.getElementById('step_goals'),
        skills: document.getElementById('step_skills'),
        tech: document.getElementById('step_tech'),
        resources: document.getElementById('step_resources'),
        milestones: document.getElementById('step_milestones'),
        projects: document.getElementById('step_projects'),
        quizzes: document.getElementById('step_quizzes'),
        finalize: document.getElementById('step_finalize')
    };

    const stepIds = ['goals', 'skills', 'tech', 'resources', 'milestones', 'projects', 'quizzes', 'finalize'];
    const stepPercentages = {
        goals: 10,
        skills: 22,
        tech: 35,
        resources: 48,
        milestones: 61,
        projects: 74,
        quizzes: 86,
        finalize: 95
    };

    // State management variables
    let appState = 'IDLE'; // IDLE, QUESTIONNAIRE, SUBMITTING, GENERATING, READY, FAILED
    let animationInterval = null;
    let pollTimeout = null;
    let isPollingActive = false;
    let currentStepIndex = 0;
    let currentProgress = 0;
    let isBackendReady = false;
    let isBackendFailed = false;
    let backendErrorMessage = "";
    let consecutiveErrors = 0;
    let submitAbortController = null;
    let selectedRoadmapId = null;

    // Pre-fill Career Goal from URL query parameter (from Career Discovery Quiz)
    const urlParams = new URLSearchParams(window.location.search);
    const roleParam = urlParams.get('role');
    if (roleParam) {
        const selectGoal = document.getElementById('inputCareerGoal');
        if (selectGoal) {
            let found = false;
            for (let option of selectGoal.options) {
                if (option.value.toLowerCase() === roleParam.toLowerCase()) {
                    selectGoal.value = option.value;
                    found = true;
                    break;
                }
            }
            if (!found) {
                const opt = document.createElement('option');
                opt.value = roleParam;
                opt.text = roleParam;
                selectGoal.appendChild(opt);
                selectGoal.value = roleParam;
            }
        }
    }

    // Set up Option Boxes (Single-select vs Multi-select Cards)
    const optionBoxes = document.querySelectorAll('.option-box');
    optionBoxes.forEach(card => {
        const input = card.querySelector('input');
        if (!input) return;

        card.setAttribute('tabindex', '0');

        if (input.checked) {
            card.classList.add('selected');
            if (input.id === 'lang_none') {
                disableOtherLanguages();
            }
        }

        card.addEventListener('click', (e) => {
            e.preventDefault();

            if (card.classList.contains('disabled')) {
                if (input.name === 'languages' && input.id !== 'lang_none') {
                    const noneInput = document.getElementById('lang_none');
                    const noneCard = noneInput?.closest('.option-box');
                    if (noneInput && noneCard) {
                        noneInput.checked = false;
                        noneCard.classList.remove('selected');
                    }

                    enableAllLanguages();

                    input.checked = true;
                    card.classList.add('selected');
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }
                return;
            }

            if (input.type === 'radio') {
                const wasChecked = input.checked;
                if (wasChecked) {
                    input.checked = false;
                    card.classList.remove('selected');
                } else {
                    const peers = document.querySelectorAll(`input[name="${input.name}"]`);
                    peers.forEach(p => {
                        p.checked = false;
                        p.closest('.option-box')?.classList.remove('selected');
                    });
                    input.checked = true;
                    card.classList.add('selected');
                }
                input.dispatchEvent(new Event('change', { bubbles: true }));
            } else if (input.type === 'checkbox') {
                if (input.id === 'lang_none') {
                    input.checked = !input.checked;
                    if (input.checked) {
                        card.classList.add('selected');
                        disableOtherLanguages();
                    } else {
                        card.classList.remove('selected');
                        enableAllLanguages();
                    }
                } else {
                    input.checked = !input.checked;
                    card.classList.toggle('selected', input.checked);
                }
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });

        input.addEventListener('change', () => {
            card.classList.toggle('selected', input.checked);
        });

        card.addEventListener('keydown', (e) => {
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                card.click();
            }
        });
    });

    function disableOtherLanguages() {
        const otherInputs = document.querySelectorAll("input[name='languages']");
        otherInputs.forEach(otherInput => {
            if (otherInput.id !== 'lang_none') {
                otherInput.checked = false;
                const otherCard = otherInput.closest('.option-box');
                if (otherCard) {
                    otherCard.classList.remove('selected');
                    otherCard.classList.add('disabled');
                    otherInput.disabled = true;
                    otherCard.setAttribute('title', "Disabled because 'I don't know any programming language' is selected.");
                }
            }
        });
    }

    function enableAllLanguages() {
        const otherInputs = document.querySelectorAll("input[name='languages']");
        otherInputs.forEach(otherInput => {
            otherInput.disabled = false;
            const otherCard = otherInput.closest('.option-box');
            if (otherCard) {
                otherCard.classList.remove('disabled');
                otherCard.removeAttribute('title');
            }
        });
    }

    // Modular Functions for State & Views
    function resetFormState() {
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Generate Roadmap Base';
        const inputs = form.querySelectorAll('input, select, textarea, button');
        inputs.forEach(el => el.removeAttribute('disabled'));
        enableAllLanguages();
        form.classList.remove('was-validated');
    }

    function disableFormInputs() {
        const inputs = form.querySelectorAll('input, select, textarea, button');
        inputs.forEach(el => el.setAttribute('disabled', 'true'));
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Saving Profile...`;
    }

    function showView(el) {
        el.classList.remove('d-none');
        el.style.opacity = '1';
    }

    function hideView(el) {
        el.classList.add('d-none');
        el.style.opacity = '0';
    }

    function crossFadeViews(fromEl, toEl) {
        fromEl.style.transition = 'opacity 0.4s ease-in-out';
        toEl.style.transition = 'opacity 0.4s ease-in-out';

        fromEl.style.opacity = '0';
        toEl.classList.remove('d-none');
        toEl.offsetHeight; // Force reflow
        toEl.style.opacity = '1';

        setTimeout(() => {
            fromEl.classList.add('d-none');
        }, 400);
    }

    // State Transition Manager
    function transitionTo(newState, errorMsg = "", force = false) {
        console.log(`Transitioning state: ${appState} -> ${newState} (force=${force})`);
        if (appState === newState) return;

        const allowedTransitions = {
            'IDLE': ['QUESTIONNAIRE', 'GENERATING', 'READY', 'FAILED'],
            'QUESTIONNAIRE': ['SUBMITTING'],
            'SUBMITTING': ['GENERATING', 'FAILED'],
            'GENERATING': ['READY', 'FAILED'],
            'READY': ['QUESTIONNAIRE'],
            'FAILED': ['GENERATING', 'QUESTIONNAIRE']
        };

        const fromState = appState;
        const isAllowed = allowedTransitions[fromState] && allowedTransitions[fromState].includes(newState);

        if (!isAllowed && !force) {
            console.warn(`Blocked invalid transition: ${fromState} -> ${newState}`);
            return;
        }

        appState = newState;

        if (newState === 'QUESTIONNAIRE') {
            stopStatusPolling();
            if (animationInterval) clearInterval(animationInterval);
            resetFormState();
            
            if (previousStateWasActive(fromState)) {
                const fromEl = fromState === 'FAILED' ? aiFailureContainer : aiLoadingContainer;
                crossFadeViews(fromEl, questionnaireContent);
            } else {
                showView(questionnaireContent);
                hideView(aiLoadingContainer);
                hideView(aiFailureContainer);
            }
        } else if (newState === 'SUBMITTING') {
            disableFormInputs();
        } else if (newState === 'GENERATING') {
            if (fromState === 'IDLE') {
                hideView(questionnaireContent);
                showView(aiLoadingContainer);
                hideView(aiFailureContainer);
                startLoadingAnimation();
            } else {
                const fromEl = fromState === 'FAILED' ? aiFailureContainer : questionnaireContent;
                crossFadeViews(fromEl, aiLoadingContainer);
                startLoadingAnimation();
            }
        } else if (newState === 'READY') {
            stopStatusPolling();
            triggerSuccessTransition();
        } else if (newState === 'FAILED') {
            stopStatusPolling();
            triggerFailureTransition(errorMsg, fromState === 'IDLE');
        }
    }

    function previousStateWasActive(state) {
        return state === 'GENERATING' || state === 'FAILED';
    }

    function resetLoadingState() {
        currentStepIndex = 0;
        currentProgress = 0;
        isBackendReady = false;
        isBackendFailed = false;
        backendErrorMessage = "";

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

        const title = document.querySelector('#aiLoadingContainer .loading-title');
        const subtitle = document.querySelector('#aiLoadingContainer .loading-subtitle');
        if (title) title.textContent = "Crafting Your Personalized Learning Journey...";
        if (subtitle) subtitle.textContent = "Our AI is analyzing your profile and building a roadmap designed specifically for you.";

        if (animationInterval) clearInterval(animationInterval);
        stopStatusPolling();
    }

    function startLoadingAnimation() {
        resetLoadingState();

        const focusVal = document.getElementById('currentFocusVal');
        const primaryGoalSelect = document.getElementById('inputCareerGoal');
        const primaryCareerGoal = primaryGoalSelect ? primaryGoalSelect.value : '';
        if (focusVal && primaryCareerGoal) {
            focusVal.textContent = primaryCareerGoal;
        }

        let activeStepId = stepIds[0];
        setActiveStep(activeStepId);
        animateProgressBarTo(stepPercentages[activeStepId]);

        animationInterval = setInterval(() => {
            if (currentStepIndex < stepIds.length - 1) {
                completeStep(stepIds[currentStepIndex]);
                currentStepIndex++;
                const nextStepId = stepIds[currentStepIndex];
                setActiveStep(nextStepId);
                animateProgressBarTo(stepPercentages[nextStepId]);
            } else {
                clearInterval(animationInterval);
                if (isBackendReady) {
                    transitionTo('READY');
                }
            }
        }, 1400);

        startStatusPolling();
    }

    function setActiveStep(id) {
        const el = stepElements[id];
        if (el) {
            el.classList.add('active');
            const iconSpan = el.querySelector('.step-icon');
            if (iconSpan) iconSpan.innerHTML = '<i class="bi bi-arrow-right-short fs-5"></i>';
        }
    }

    function completeStep(id) {
        const el = stepElements[id];
        if (el) {
            el.classList.remove('active');
            el.classList.add('completed');
            const iconSpan = el.querySelector('.step-icon');
            if (iconSpan) iconSpan.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i>';
        }
    }

    function animateProgressBarTo(target) {
        const bar = document.getElementById('loadingProgressBar');
        const percentText = document.getElementById('progressPercent');

        let start = currentProgress;
        const diff = target - start;
        const duration = 600;
        const startTime = performance.now();

        function update(now) {
            const elapsed = now - startTime;
            const progressRatio = Math.min(elapsed / duration, 1);
            const easeRatio = 1 - Math.pow(1 - progressRatio, 3);
            const val = Math.round(start + diff * easeRatio);

            currentProgress = val;
            if (bar) bar.style.width = `${val}%`;
            if (percentText) percentText.textContent = `${val}%`;

            if (progressRatio < 1) {
                requestAnimationFrame(update);
            }
        }
        requestAnimationFrame(update);
    }

    // Status Polling Loop with Exponential Backoff
    async function runPoll() {
        if (!isPollingActive) return;

        try {
            const token = getToken();
            if (!token) {
                transitionTo('QUESTIONNAIRE', '', true);
                return;
            }

            const res = await fetch(`${API_BASE_URL}/roadmap/status`, {
                headers: { "Authorization": "Bearer " + token }
            });

            if (!isPollingActive) return;

            if (handle401Error(res)) {
                transitionTo('QUESTIONNAIRE', '', true);
                return;
            }

            if (res.ok) {
                consecutiveErrors = 0;
                const data = await res.json();

                if (data.status === 'READY') {
                    isBackendReady = true;
                    const verifiedId = await verifyRoadmapMetadata(token);
                    if (!isPollingActive) return;

                    if (verifiedId) {
                        selectedRoadmapId = verifiedId;
                        if (currentStepIndex >= stepIds.length - 2 || !animationInterval) {
                            transitionTo('READY');
                        } else {
                            accelerateSteps();
                        }
                    } else {
                        console.warn("Roadmap READY but metadata verification failed. Retrying in 2 seconds...");
                        scheduleNextPoll(2000);
                    }
                } else if (data.status === 'FAILED') {
                    isBackendFailed = true;
                    backendErrorMessage = data.error_message || "AI Roadmap generation failed.";
                    transitionTo('FAILED', backendErrorMessage);
                } else {
                    scheduleNextPoll(2000);
                }
            } else {
                throw new Error(`Server status code ${res.status}`);
            }
        } catch (err) {
            if (!isPollingActive) return;
            console.error("Polling error caught:", err);
            consecutiveErrors++;
            if (consecutiveErrors >= 5) {
                backendErrorMessage = "Connection lost. Please check your network and try again.";
                transitionTo('FAILED', backendErrorMessage);
            } else {
                const backoffDelay = Math.min(10000, 1000 * Math.pow(2, consecutiveErrors));
                console.log(`Polling temporary failure. Retrying in ${backoffDelay}ms...`);
                scheduleNextPoll(backoffDelay);
            }
        }
    }

    function scheduleNextPoll(delay) {
        if (!isPollingActive) return;
        if (pollTimeout) clearTimeout(pollTimeout);
        pollTimeout = setTimeout(runPoll, delay);
    }

    function startStatusPolling() {
        if (isPollingActive) {
            console.log("Polling already active.");
            return;
        }
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

    async function verifyRoadmapMetadata(token) {
        try {
            const userRes = await fetch(`${API_BASE_URL}/users/me`, {
                headers: { "Authorization": "Bearer " + token }
            });
            if (!userRes.ok) return null;

            const userData = await userRes.json();
            const targetId = userData.selected_roadmap_id;
            if (!targetId) return null;

            const roadmapRes = await fetch(`${API_BASE_URL}/roadmap/${targetId}`, {
                headers: { "Authorization": "Bearer " + token }
            });
            if (roadmapRes.ok) {
                const roadmapData = await roadmapRes.json();
                if (roadmapData && roadmapData.id === targetId) {
                    return targetId;
                }
            }
            return null;
        } catch (e) {
            console.error("Failed to verify roadmap metadata:", e);
            return null;
        }
    }

    function accelerateSteps() {
        if (animationInterval) clearInterval(animationInterval);

        animationInterval = setInterval(() => {
            if (currentStepIndex < stepIds.length - 1) {
                completeStep(stepIds[currentStepIndex]);
                currentStepIndex++;
                const nextStepId = stepIds[currentStepIndex];
                setActiveStep(nextStepId);
                animateProgressBarTo(stepPercentages[nextStepId]);
            } else {
                clearInterval(animationInterval);
                transitionTo('READY');
            }
        }, 300);
    }

    async function triggerSuccessTransition() {
        if (animationInterval) clearInterval(animationInterval);
        stopStatusPolling();

        // Ensure progress bar reaches 100%
        animateProgressBarTo(100);

        // Transition title/subtitle
        const title = document.querySelector('#aiLoadingContainer .loading-title');
        const subtitle = document.querySelector('#aiLoadingContainer .loading-subtitle');
        if (title) title.textContent = "Your Roadmap is Ready!";
        if (subtitle) subtitle.textContent = "Redirecting you to your personalized learning path...";

        // Show success checkmark badge if exists
        const successBadge = document.getElementById('successBadge');
        if (successBadge) {
            successBadge.classList.remove('d-none');
            successBadge.classList.add('animate__animated', 'animate__bounceIn');
        }

        // Retrieve roadmap ID if not set
        let redirectId = selectedRoadmapId;
        if (!redirectId) {
            try {
                const token = getToken();
                if (token) {
                    const userRes = await fetch(`${API_BASE_URL}/users/me`, {
                        headers: { "Authorization": "Bearer " + token }
                    });
                    if (userRes.ok) {
                        const userData = await userRes.json();
                        redirectId = userData.selected_roadmap_id;
                    }
                }
            } catch (err) {
                console.error("Failed to retrieve roadmap ID for success redirect:", err);
            }
        }

        // Redirect after a short delay for visual satisfaction
        setTimeout(() => {
            if (redirectId) {
                window.location.href = `roadmap.html#path=${redirectId}`;
            } else {
                window.location.href = 'roadmap.html';
            }
        }, 2000);
    }

    function triggerFailureTransition(msg, immediate = false) {
        if (animationInterval) clearInterval(animationInterval);
        stopStatusPolling();

        const errMessage = document.getElementById('aiErrorMessage');
        if (errMessage && msg) {
            errMessage.textContent = msg;
        }

        if (immediate) {
            hideView(questionnaireContent);
            hideView(aiLoadingContainer);
            showView(aiFailureContainer);
        } else {
            crossFadeViews(aiLoadingContainer, aiFailureContainer);
        }
    }

    // Failure buttons wiring
    const retryBtn = document.getElementById('retryBtn');
    const backToFormBtn = document.getElementById('backToFormBtn');

    if (retryBtn) {
        retryBtn.onclick = async () => {
            transitionTo('GENERATING', '', true);

            try {
                const response = await fetch(`${API_BASE_URL}/roadmap/generate`, {
                    method: 'POST',
                    headers: { "Authorization": "Bearer " + getToken() }
                });
                if (handle401Error(response)) return;
                if (!response.ok) {
                    const data = await response.json();
                    backendErrorMessage = data.detail || "AI Roadmap generation failed.";
                    transitionTo('FAILED', backendErrorMessage);
                }
            } catch (err) {
                console.error(err);
                backendErrorMessage = "Network error. Please make sure the backend is active.";
                transitionTo('FAILED', backendErrorMessage);
            }
        };
    }

    if (backToFormBtn) {
        backToFormBtn.onclick = () => {
            transitionTo('QUESTIONNAIRE', '', true);
        };
    }

    // Form pre-fill helpers
    function preFillForm(data) {
        if (!data) return;
        if (document.getElementById('inputName') && data.name) document.getElementById('inputName').value = data.name;
        if (document.getElementById('inputCollege') && data.college) document.getElementById('inputCollege').value = data.college;
        if (document.getElementById('inputYear') && data.year) document.getElementById('inputYear').value = data.year;
        if (document.getElementById('inputBranch') && data.branch) document.getElementById('inputBranch').value = data.branch;
        if (document.getElementById('inputCareerGoal') && data.primary_career_goal) document.getElementById('inputCareerGoal').value = data.primary_career_goal;
        if (document.getElementById('inputDailyTime') && data.daily_learning_time) document.getElementById('inputDailyTime').value = data.daily_learning_time;
        if (document.getElementById('inputTimeline') && data.target_timeline) document.getElementById('inputTimeline').value = data.target_timeline;

        if (data.programming_languages) {
            const langs = data.programming_languages.split(',');
            langs.forEach(lang => {
                const checkbox = document.querySelector(`input[name="languages"][value="${lang}"]`);
                if (checkbox) {
                    checkbox.checked = true;
                    checkbox.closest('.option-box')?.classList.add('selected');
                }
            });
            if (langs.includes("I don't know any programming language")) {
                disableOtherLanguages();
            }
        }

        if (data.current_skill_level) {
            const radio = document.querySelector(`input[name="skill_level"][value="${data.current_skill_level}"]`);
            if (radio) {
                radio.checked = true;
                radio.closest('.option-box')?.classList.add('selected');
            }
        }
    }

    // Window and click event bindings for Abort/Stop
    window.addEventListener('beforeunload', () => {
        if (submitAbortController) {
            submitAbortController.abort();
        }
        stopStatusPolling();
    });

    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            if (submitAbortController) {
                submitAbortController.abort();
            }
            stopStatusPolling();
        });
    }

    const backNavBtn = document.querySelector('a[href="welcome.html"]');
    if (backNavBtn) {
        backNavBtn.addEventListener('click', () => {
            if (submitAbortController) {
                submitAbortController.abort();
            }
            stopStatusPolling();
        });
    }

    // 1. Initial State Restoration Check
    const token = getToken();
    if (token) {
        try {
            const [statusRes, questionnaireRes] = await Promise.all([
                fetch(`${API_BASE_URL}/roadmap/status`, { headers: { "Authorization": "Bearer " + token } }),
                fetch(`${API_BASE_URL}/questionnaire`, { headers: { "Authorization": "Bearer " + token } }).catch(() => null)
            ]);

            let questionnaireData = null;
            if (questionnaireRes && questionnaireRes.ok) {
                questionnaireData = await questionnaireRes.json();
                preFillForm(questionnaireData);
            }

            if (statusRes.ok) {
                const statusData = await statusRes.json();
                if (statusData.status === 'GENERATING') {
                    if (questionnaireData && questionnaireData.primary_career_goal) {
                        const focusVal = document.getElementById('currentFocusVal');
                        if (focusVal) focusVal.textContent = questionnaireData.primary_career_goal;
                    }
                    transitionTo('GENERATING', '', true);
                } else if (statusData.status === 'FAILED') {
                    transitionTo('FAILED', statusData.error_message || "Generation failed", true);
                } else if (statusData.status === 'READY') {
                    const isNew = urlParams.get('new') === 'true';
                    const hasRole = urlParams.has('role');
                    if (!isNew && !hasRole) {
                        window.location.href = 'roadmap.html';
                        return;
                    }
                    transitionTo('QUESTIONNAIRE', '', true);
                } else {
                    transitionTo('QUESTIONNAIRE', '', true);
                }
            } else {
                transitionTo('QUESTIONNAIRE', '', true);
            }
        } catch (err) {
            console.error("Initial state restore failed:", err);
            transitionTo('QUESTIONNAIRE', '', true);
        }
    } else {
        transitionTo('QUESTIONNAIRE', '', true);
    }

    // Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        formError.classList.add('d-none');
        formError.textContent = '';
        document.getElementById('skillLevelError').classList.add('d-none');

        const name = document.getElementById('inputName').value.trim();
        const college = document.getElementById('inputCollege').value.trim();
        const year = document.getElementById('inputYear').value;
        const branch = document.getElementById('inputBranch').value.trim();
        const primaryCareerGoal = document.getElementById('inputCareerGoal').value;
        const dailyLearningTime = document.getElementById('inputDailyTime').value;
        const targetTimeline = document.getElementById('inputTimeline').value;

        const selectedLangs = Array.from(document.querySelectorAll("input[name='languages']:checked")).map(el => el.value);
        if (selectedLangs.length === 0) {
            formError.textContent = "Please select at least one programming language option.";
            formError.classList.remove('d-none');
            formError.scrollIntoView({ behavior: 'smooth' });
            return;
        }

        const selectedSkill = document.querySelector("input[name='skill_level']:checked")?.value;
        if (!selectedSkill) {
            document.getElementById('skillLevelError').classList.remove('d-none');
            formError.textContent = "Please select your current skill level.";
            formError.classList.remove('d-none');
            formError.scrollIntoView({ behavior: 'smooth' });
            return;
        }

        if (!form.checkValidity()) {
            e.stopPropagation();
            form.classList.add('was-validated');
            formError.textContent = "Please fill in all required fields.";
            formError.classList.remove('d-none');
            formError.scrollIntoView({ behavior: 'smooth' });
            return;
        }

        form.classList.add('was-validated');

        const payload = {
            name: name,
            college: college,
            year: year,
            branch: branch,
            programming_languages: selectedLangs,
            primary_career_goal: primaryCareerGoal,
            current_skill_level: selectedSkill,
            daily_learning_time: dailyLearningTime,
            target_timeline: targetTimeline
        };

        transitionTo('SUBMITTING');
        transitionTo('GENERATING');

        submitAbortController = new AbortController();
        try {
            const response = await fetch(`${API_BASE_URL}/questionnaire`, {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + getToken()
                },
                body: JSON.stringify(payload),
                signal: submitAbortController.signal
            });

            if (handle401Error(response)) return;

            const responseData = await response.json();
            if (!response.ok) {
                backendErrorMessage = responseData.detail || "An error occurred while saving your questionnaire.";
                transitionTo('FAILED', backendErrorMessage);
            } else {
                if (responseData.status === 'READY') {
                    transitionTo('READY');
                }
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                console.log("Submit request aborted by user leaving or logging out.");
                return;
            }
            backendErrorMessage = "Network error. Please make sure the backend is active.";
            transitionTo('FAILED', backendErrorMessage);
            console.error(error);
        }
    });
});
