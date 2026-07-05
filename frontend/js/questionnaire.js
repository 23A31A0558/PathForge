// frontend/js/questionnaire.js

document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('questionsContainer');
    const submitBtn = document.getElementById('submitBtn');
    const formError = document.getElementById('formError');
    const form = document.getElementById('questionnaireForm');

    // Fetch questions
    try {
        const response = await fetch(`${API_BASE_URL}/questions`, {
            headers: { 
                "Content-Type": "application/json",
                "Authorization": "Bearer " + getToken()
            }
        });

        if (handle401Error(response)) return;

        if (!response.ok) {
            throw new Error('Failed to load questions from backend.');
        }

        const questions = await response.json();
        renderQuestions(questions);
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Error: ${error.message}. Is your backend running at ${API_BASE_URL}?</div>`;
    }

    function renderQuestions(questions) {
        container.innerHTML = '';
        
        questions.forEach((q, index) => {
            const section = document.createElement('div');
            section.className = 'question-section mb-4 p-4 border rounded bg-white shadow-sm';
            
            let optionsHtml = '';
            q.options.forEach(opt => {
                optionsHtml += `
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="radio" name="q_${q.id}" id="opt_${opt.id}" value="${opt.value}">
                        <label class="form-check-label fs-6 text-secondary" for="opt_${opt.id}">
                            ${opt.option_text}
                        </label>
                    </div>
                `;
            });

            section.innerHTML = `
                <h5 class="mb-3 fw-bold">${index + 1}. ${q.question_text}</h5>
                ${optionsHtml}
            `;
            container.appendChild(section);
        });

        submitBtn.classList.remove('d-none');
    }

    // Submit Answers
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        formError.classList.add('d-none');

        const inputs = Array.from(document.querySelectorAll('.question-section'));
        const answers = [];
        let allAnswered = true;

        inputs.forEach(section => {
            const checked = section.querySelector('input[type="radio"]:checked');
            if (checked) {
                const qId = checked.name.split('_')[1];
                answers.push({
                    question_id: parseInt(qId),
                    selected_option: checked.value
                });
            } else {
                allAnswered = false;
            }
        });

        if (!allAnswered) {
            formError.textContent = "Please answer all questions before submitting.";
            formError.classList.remove('d-none');
            formError.scrollIntoView({ behavior: 'smooth' });
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';

        try {
            // POST /answers
            const response = await fetch(`${API_BASE_URL}/answers`, {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + getToken()
                },
                body: JSON.stringify({ answers: answers })
            });

            if (handle401Error(response)) return;

            if (!response.ok) {
                let errorMsg = 'Failed to submit answers.';
                try {
                    const errorData = await response.json();
                    if (errorData.detail) {
                        errorMsg = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
                    }
                } catch(e) {}
                throw new Error(`Backend Error: ${errorMsg}`);
            }

            // Also trigger roadmap generation
            const generateResponse = await fetch(`${API_BASE_URL}/generate-roadmap`, {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + getToken()
                }
            });

            if (handle401Error(generateResponse)) return;
            
            if (!generateResponse.ok) {
                 let genErrorMsg = 'Roadmap generation failed.';
                 try {
                     const genData = await generateResponse.json();
                     if (genData.detail) genErrorMsg = genData.detail;
                 } catch(e) {}
                 throw new Error(genErrorMsg);
            }

            // Redirect to roadmap.html on complete success
            window.location.href = 'roadmap.html';

        } catch (error) {
            formError.textContent = error.message;
            formError.classList.remove('d-none');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Generate My Path';
        }
    });
});
