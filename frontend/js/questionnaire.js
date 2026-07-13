// frontend/js/questionnaire.js

document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('roadmapQuestionnaireForm');
    const formError = document.getElementById('formError');
    const submitBtn = document.getElementById('submitBtn');

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

        // Make option card keyboard-focusable for accessibility
        card.setAttribute('tabindex', '0');

        // Sync initial state (e.g. on page reload / navigation back)
        if (input.checked) {
            card.classList.add('selected');
            // If the checked input is 'lang_none', trigger its special behavior on load
            if (input.id === 'lang_none') {
                disableOtherLanguages();
            }
        }

        // Card click handler
        card.addEventListener('click', (e) => {
            e.preventDefault(); // Stop native radio/checkbox click triggers to prevent double toggling

            // Check if card is disabled
            if (card.classList.contains('disabled')) {
                // If it is disabled, clicking it should deselect the 'none' option, re-enable all, and select this one
                if (input.name === 'languages' && input.id !== 'lang_none') {
                    const noneInput = document.getElementById('lang_none');
                    const noneCard = noneInput.closest('.option-box');
                    noneInput.checked = false;
                    noneCard.classList.remove('selected');

                    enableAllLanguages();

                    // Select clicked option
                    input.checked = true;
                    card.classList.add('selected');
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }
                return;
            }

            // Normal selection behavior
            if (input.type === 'radio') {
                // Single Select Logic
                const wasChecked = input.checked;
                if (wasChecked) {
                    // Click selected -> deselect
                    input.checked = false;
                    card.classList.remove('selected');
                } else {
                    // Click unselected -> select and clear peers
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
                // Multiple Select Logic
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
                    // Standard multi-select toggle
                    input.checked = !input.checked;
                    card.classList.toggle('selected', input.checked);
                }
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });

        // Sync visual selected state on manual change triggers
        input.addEventListener('change', () => {
            card.classList.toggle('selected', input.checked);
        });

        // Accessibility (Space and Enter keyboard events)
        card.addEventListener('keydown', (e) => {
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                card.click();
            }
        });
    });

    // Helper functions for Programming Languages question exclusivity
    function disableOtherLanguages() {
        const otherInputs = document.querySelectorAll("input[name='languages']");
        otherInputs.forEach(otherInput => {
            if (otherInput.id !== 'lang_none') {
                otherInput.checked = false;
                const otherCard = otherInput.closest('.option-box');
                otherCard.classList.remove('selected');
                otherCard.classList.add('disabled');
                otherInput.disabled = true;
                otherCard.setAttribute('title', "Disabled because 'I don't know any programming language' is selected.");
            }
        });
    }

    function enableAllLanguages() {
        const otherInputs = document.querySelectorAll("input[name='languages']");
        otherInputs.forEach(otherInput => {
            otherInput.disabled = false;
            const otherCard = otherInput.closest('.option-box');
            otherCard.classList.remove('disabled');
            otherCard.removeAttribute('title');
        });
    }

    // Submit Questionnaire Form
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Clear previous error messages
        formError.classList.add('d-none');
        formError.textContent = '';
        document.getElementById('skillLevelError').classList.add('d-none');

        // Form fields resolution
        const name = document.getElementById('inputName').value.trim();
        const college = document.getElementById('inputCollege').value.trim();
        const year = document.getElementById('inputYear').value;
        const branch = document.getElementById('inputBranch').value.trim();
        const primaryCareerGoal = document.getElementById('inputCareerGoal').value;
        const dailyLearningTime = document.getElementById('inputDailyTime').value;
        const targetTimeline = document.getElementById('inputTimeline').value;

        // Custom validation: Programming Languages (Minimum 1 checked, no max restriction)
        const selectedLangs = Array.from(document.querySelectorAll("input[name='languages']:checked")).map(el => el.value);
        if (selectedLangs.length === 0) {
            formError.textContent = "Please select at least one programming language option.";
            formError.classList.remove('d-none');
            formError.scrollIntoView({ behavior: 'smooth' });
            return;
        }

        // Custom validation: Current Skill Level (Radio checked check)
        const selectedSkill = document.querySelector("input[name='skill_level']:checked")?.value;
        if (!selectedSkill) {
            document.getElementById('skillLevelError').classList.remove('d-none');
            formError.textContent = "Please select your current skill level.";
            formError.classList.remove('d-none');
            formError.scrollIntoView({ behavior: 'smooth' });
            return;
        }

        // Bootstrap native field check validation
        if (!form.checkValidity()) {
            e.stopPropagation();
            form.classList.add('was-validated');
            formError.textContent = "Please fill in all required fields.";
            formError.classList.remove('d-none');
            formError.scrollIntoView({ behavior: 'smooth' });
            return;
        }

        form.classList.add('was-validated');

        // Compile payload matching schemas.RoadmapQuestionnaireCreate
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

        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Saving Questionnaire & Generating Paths...`;

        try {
            // POST /questionnaire
            const response = await fetch(`${API_BASE_URL}/questionnaire`, {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + getToken()
                },
                body: JSON.stringify(payload)
            });

            if (handle401Error(response)) return;

            const responseData = await response.json();
            if (response.ok) {
                // Success: Questionnaire saved, background AI generation started!
                // Redirect directly to roadmap dashboard
                window.location.href = 'roadmap.html';
            } else {
                formError.textContent = responseData.detail || "An error occurred while saving your questionnaire.";
                formError.classList.remove('d-none');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Generate Roadmap Base';
            }
        } catch (error) {
            formError.textContent = "Network error. Please make sure the backend is active.";
            formError.classList.remove('d-none');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Generate Roadmap Base';
            console.error(error);
        }
    });
});
