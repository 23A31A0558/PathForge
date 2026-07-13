// frontend/js/placement_questionnaire.js

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("placementQuestionnaireForm");
    const formError = document.getElementById("formError");
    const submitBtn = document.getElementById("submitBtn");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Clear previous custom error messages
        formError.classList.add("d-none");
        document.getElementById("aptError").classList.add("d-none");
        document.getElementById("dsaError").classList.add("d-none");
        document.getElementById("companyError").classList.add("d-none");
        document.getElementById("timelineError").classList.add("d-none");

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
            e.stopPropagation();
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

        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Saving Placement Profile...`;

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
            if (response.ok) {
                // Success: Redirect to placement dashboard
                window.location.href = "placement_dashboard.html";
            } else {
                formError.textContent = data.detail || "An error occurred while saving placement onboarding details.";
                formError.classList.remove("d-none");
                formError.scrollIntoView({ behavior: "smooth" });
                submitBtn.disabled = false;
                submitBtn.textContent = "Save Placement Profile";
            }
        } catch (error) {
            formError.textContent = "Network error. Please make sure the backend is active.";
            formError.classList.remove("d-none");
            formError.scrollIntoView({ behavior: "smooth" });
            submitBtn.disabled = false;
            submitBtn.textContent = "Save Placement Profile";
            console.error(error);
        }
    });

    // Custom Card/Chip Toggling Logic
    const formChecks = document.querySelectorAll(".form-check");
    formChecks.forEach(card => {
        const input = card.querySelector("input");
        if (!input) return;

        // Make card focusable for keyboard navigation
        card.setAttribute("tabindex", "0");

        // Sync initial checked states
        if (input.checked) {
            card.classList.add("selected");
        }

        // Forward click to input and handle custom toggles
        card.addEventListener("click", (e) => {
            e.preventDefault(); // Prevent duplicate click event and browser default check behavior
            
            if (input.type === "checkbox") {
                input.checked = !input.checked;
                input.dispatchEvent(new Event("change", { bubbles: true }));
            } else if (input.type === "radio") {
                const wasChecked = input.checked;
                if (wasChecked) {
                    // Deselect on clicking again
                    input.checked = false;
                } else {
                    // Selecting new radio: clear peers
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

        // Toggle styling on change event
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

        // Accessibility (Space and Enter keyboard events)
        card.addEventListener("keydown", (e) => {
            if (e.key === " " || e.key === "Enter") {
                e.preventDefault();
                card.click();
            }
        });
    });
});
