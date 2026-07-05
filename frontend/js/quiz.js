// frontend/js/quiz.js

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const microStepId = parseInt(urlParams.get('micro_step_id'));

    if (!microStepId) {
        alert("Invalid micro step ID. Redirecting to roadmap...");
        window.location.href = "roadmap.html";
        return;
    }

    const quizLoader = document.getElementById('quizLoader');
    const quizCard = document.getElementById('quizCard');
    const resultsCard = document.getElementById('resultsCard');
    const topicBadge = document.getElementById('topicBadge');
    const quizTimer = document.getElementById('quizTimer');
    const quizProgressBar = document.getElementById('quizProgressBar');
    const questionCounter = document.getElementById('questionCounter');
    const questionText = document.getElementById('questionText');
    const optionsContainer = document.getElementById('optionsContainer');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const retryBtn = document.getElementById('retryBtn');

    // State Variables
    let quizData = [];
    let topicName = "Roadmap Quiz";
    let currentIdx = 0;
    let userAnswers = {}; // { question_id: selected_option_key }
    let timeRemaining = 300; // 5 minutes
    let timerInterval = null;

    async function init() {
        await fetchQuiz();
        if (quizData.length > 0) {
            quizLoader.classList.add('d-none');
            quizCard.classList.remove('d-none');
            startTimer();
            renderQuestion();
        }
    }

    async function fetchQuiz() {
        try {
            const response = await fetch(`${API_BASE_URL}/quiz/${microStepId}`, {
                method: 'GET',
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + getToken()
                }
            });

            if (handle401Error(response)) return;

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || "Failed to load quiz.");
            }

            const data = await response.json();
            quizData = data.questions;
            topicName = data.topic_name;
            if (topicBadge) {
                topicBadge.innerText = topicName;
            }
        } catch (err) {
            quizLoader.innerHTML = `<div class="alert alert-danger m-3">${err.message}</div>`;
        }
    }

    function startTimer() {
        updateTimerDisplay();
        timerInterval = setInterval(() => {
            timeRemaining--;
            updateTimerDisplay();

            if (timeRemaining <= 60) {
                quizTimer.classList.remove('bg-dark');
                quizTimer.classList.add('bg-danger');
            }

            if (timeRemaining <= 0) {
                clearInterval(timerInterval);
                alert("Time's up! Submitting your quiz automatically.");
                submitQuiz();
            }
        }, 1000);
    }

    function updateTimerDisplay() {
        const minutes = Math.floor(timeRemaining / 60);
        const seconds = timeRemaining % 60;
        quizTimer.innerText = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    function renderQuestion() {
        const question = quizData[currentIdx];
        
        // Update texts
        questionCounter.innerText = `Question ${currentIdx + 1} of ${quizData.length}`;
        questionText.innerText = question.question_text;
        
        // Progress Bar
        const progressPercentage = ((currentIdx) / quizData.length) * 100;
        quizProgressBar.style.width = `${progressPercentage}%`;
        quizProgressBar.setAttribute('aria-valuenow', progressPercentage);

        // Options
        optionsContainer.innerHTML = '';
        question.options.forEach(opt => {
            const isSelected = userAnswers[question.id] === opt.key;
            
            const card = document.createElement('div');
            card.className = `option-card ${isSelected ? 'selected' : ''}`;
            card.innerHTML = `
                <input type="radio" name="question_option" value="${opt.key}" ${isSelected ? 'checked' : ''}>
                <span class="text-dark fw-medium">${opt.text}</span>
            `;

            card.addEventListener('click', () => {
                // Select Option
                userAnswers[question.id] = opt.key;
                
                // Update styling
                document.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                card.querySelector('input').checked = true;
            });

            optionsContainer.appendChild(card);
        });

        // Button state
        prevBtn.disabled = currentIdx === 0;
        if (currentIdx === quizData.length - 1) {
            nextBtn.innerText = "Submit Quiz";
            nextBtn.classList.remove('btn-primary');
            nextBtn.classList.add('btn-success');
        } else {
            nextBtn.innerText = "Next";
            nextBtn.classList.add('btn-primary');
            nextBtn.classList.remove('btn-success');
        }
    }

    prevBtn.addEventListener('click', () => {
        if (currentIdx > 0) {
            currentIdx--;
            renderQuestion();
        }
    });

    nextBtn.addEventListener('click', () => {
        if (currentIdx < quizData.length - 1) {
            currentIdx++;
            renderQuestion();
        } else {
            submitQuiz();
        }
    });

    async function submitQuiz() {
        clearInterval(timerInterval);
        quizCard.classList.add('d-none');
        quizLoader.classList.remove('d-none');
        quizLoader.querySelector('p').innerText = "Analyzing your answers...";

        // Construct answers list (ensure all questions have an entry, even if blank)
        const answersPayload = quizData.map(q => {
            return {
                question_id: q.id,
                selected_option: userAnswers[q.id] || ""
            };
        });

        try {
            const response = await fetch(`${API_BASE_URL}/quiz/submit`, {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + getToken()
                },
                body: JSON.stringify({
                    micro_step_id: microStepId,
                    answers: answersPayload
                })
            });

            if (handle401Error(response)) return;

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || "Submission failed.");
            }

            const data = await response.json();
            
            // Auto mark as completed if passed
            if (data.passed) {
                try {
                    await fetch(`${API_BASE_URL}/progress/complete`, {
                        method: 'POST',
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": "Bearer " + getToken()
                        },
                        body: JSON.stringify({
                            micro_step_id: microStepId
                        })
                    });
                } catch (err) {
                    console.error("Auto-completion error:", err);
                }
            }

            renderResults(data);
        } catch (err) {
            quizLoader.innerHTML = `<div class="alert alert-danger m-3">${err.message}</div>`;
        }
    }

    function renderResults(resultData) {
        quizLoader.classList.add('d-none');
        resultsCard.classList.remove('d-none');

        const scorePercent = Math.round((resultData.score / quizData.length) * 100);
        document.getElementById('resultScore').innerText = `${resultData.score}/${quizData.length}`;
        document.getElementById('resultPercentage').innerText = `${scorePercent}%`;

        const circle = document.getElementById('resultCircle');
        const alertBox = document.getElementById('resultAlert');
        const feedbackText = document.getElementById('resultFeedback');

        if (resultData.passed) {
            circle.className = "result-circle circle-passed";
            alertBox.className = "alert alert-success mb-4 py-3 border-0 rounded-3 shadow-sm fw-bold text-center";
            alertBox.innerHTML = `✓ Congratulations! You passed the quiz!`;
            feedbackText.innerText = "Excellent understanding! This micro-step has been marked as complete. Return to your roadmap to proceed to the next topic!";
        } else {
            circle.className = "result-circle circle-failed";
            alertBox.className = "alert alert-danger mb-4 py-3 border-0 rounded-3 shadow-sm fw-bold text-center";
            alertBox.innerHTML = `✗ Quiz Failed. You got ${resultData.score} out of ${quizData.length} correct.`;
            feedbackText.innerText = "You need at least 60% (3/5) correct to pass this step. We highly suggest revising the learning material and retrying the quiz.";
        }

        // Render reviews
        const reviewsContainer = document.getElementById('reviewsContainer');
        reviewsContainer.innerHTML = '';

        quizData.forEach((q, idx) => {
            const resultItem = resultData.results.find(r => r.question_id === q.id) || {};
            const isCorrect = resultItem.is_correct;
            
            const reviewCard = document.createElement('div');
            reviewCard.className = `review-card ${isCorrect ? 'correct' : 'incorrect'}`;

            // Map keys (option_a) to readable options index/text
            let userAnsText = "No answer provided";
            let correctAnsText = "";

            q.options.forEach(opt => {
                if (opt.key === resultItem.selected_option) userAnsText = opt.text;
                if (opt.key === resultItem.correct_answer) correctAnsText = opt.text;
            });

            const statusBadge = isCorrect 
                ? `<span class="badge bg-success mb-2 px-3 py-1">Correct</span>` 
                : `<span class="badge bg-danger mb-2 px-3 py-1">Incorrect</span>`;

            reviewCard.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="fw-bold text-dark mb-2">Question ${idx + 1}: ${q.question_text}</h6>
                        <div class="small mb-1">
                            <span class="text-muted">Your Answer:</span> 
                            <strong class="${isCorrect ? 'text-success' : 'text-danger'}">${userAnsText}</strong>
                        </div>
                        ${!isCorrect ? `
                        <div class="small">
                            <span class="text-muted">Correct Answer:</span> 
                            <strong class="text-success">${correctAnsText}</strong>
                        </div>` : ''}
                    </div>
                    <div>
                        ${statusBadge}
                    </div>
                </div>
            `;
            reviewsContainer.appendChild(reviewCard);
        });
    }

    retryBtn.addEventListener('click', () => {
        // Reset state
        currentIdx = 0;
        userAnswers = {};
        timeRemaining = 300;
        
        resultsCard.classList.add('d-none');
        quizLoader.classList.remove('d-none');
        
        // Remove bg-danger and set back to bg-dark
        quizTimer.className = "badge bg-dark timer-badge rounded-pill px-3 py-2";
        
        // Reload questions to get a fresh randomized set!
        init();
    });

    init();
});
