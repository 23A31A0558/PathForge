// frontend/js/career_quiz.js

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("careerQuizForm");
    const quizSection = document.getElementById("quizSection");
    const resultSection = document.getElementById("resultSection");
    const recommendationsList = document.getElementById("recommendationsList");
    const quizError = document.getElementById("quizError");
    const selectionError = document.getElementById("selectionError");
    
    // Check validation and handle submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        // Hide errors
        document.getElementById("q1Error").classList.add("d-none");
        document.getElementById("q2Error").classList.add("d-none");
        document.getElementById("q3Error").classList.add("d-none");
        quizError.classList.add("d-none");

        // Validate Q1 (Checkboxes)
        const checkedActivities = Array.from(document.querySelectorAll("input[name='activities']:checked")).map(el => el.value);
        if (checkedActivities.length === 0) {
            document.getElementById("q1Error").classList.remove("d-none");
            return;
        }

        // Validate Q2 and Q3 (Radios)
        const selectedSubject = document.querySelector("input[name='subject']:checked")?.value;
        if (!selectedSubject) {
            document.getElementById("q2Error").classList.remove("d-none");
            return;
        }

        const selectedWorkType = document.querySelector("input[name='work_type']:checked")?.value;
        if (!selectedWorkType) {
            document.getElementById("q3Error").classList.remove("d-none");
            return;
        }

        const payload = {
            activities: checkedActivities,
            subject: selectedSubject,
            work_type: selectedWorkType
        };

        const submitBtn = document.getElementById("quizSubmitBtn");
        submitBtn.disabled = true;
        submitBtn.textContent = "Processing Quiz...";

        try {
            const response = await fetch(`${API_BASE_URL}/career-quiz`, {
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
                renderResults(data.recommendations);
            } else {
                quizError.textContent = data.detail || "An error occurred while calculating career suggestions.";
                quizError.classList.remove("d-none");
            }
        } catch (error) {
            quizError.textContent = "Network error. Please make sure the backend is active.";
            quizError.classList.remove("d-none");
            console.error(error);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Calculate Recommendations";
        }
    });

    let selectedCareerName = null;

    function renderResults(recommendations) {
        recommendationsList.innerHTML = "";
        
        recommendations.forEach((rec, idx) => {
            const card = document.createElement("div");
            card.className = "result-card d-flex justify-content-between align-items-center";
            card.dataset.careerName = rec.career;
            
            // Highlight rank
            let rankText = `#${idx + 1}`;
            
            card.innerHTML = `
                <div>
                    <span class="badge bg-primary me-2">${rankText}</span>
                    <strong class="fs-5 text-dark">${rec.career}</strong>
                </div>
                <div class="text-end">
                    <span class="fs-5 fw-bold text-primary">${rec.score_percentage}% Match</span>
                </div>
            `;
            
            card.addEventListener("click", () => {
                // Clear selection
                document.querySelectorAll(".result-card").forEach(c => c.classList.remove("selected"));
                
                // Set selection
                card.classList.add("selected");
                selectedCareerName = rec.career;
                selectionError.classList.add("d-none");
            });

            recommendationsList.appendChild(card);
        });

        // Hide quiz, show results
        quizSection.classList.add("d-none");
        resultSection.classList.remove("d-none");
    }

    const confirmBtn = document.getElementById("confirmCareerBtn");
    confirmBtn.addEventListener("click", () => {
        if (!selectedCareerName) {
            selectionError.classList.remove("d-none");
            return;
        }

        // Redirect to questionnaire with pre-selected career
        window.location.href = `questionnaire.html?role=${encodeURIComponent(selectedCareerName)}`;
    });

    // Custom Card/Chip Toggling Logic for Career Quiz Option Boxes
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

        // Click handler
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

        // Keyboard navigation accessibility
        card.addEventListener("keydown", (e) => {
            if (e.key === " " || e.key === "Enter") {
                e.preventDefault();
                card.click();
            }
        });
    });
});

