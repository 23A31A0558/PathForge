// PathForge - Journey Map JS Engine

// Topic Details Metadata Mapping
const TOPIC_DETAILS = {
    // Frontend Developer
    "HTML/CSS": {
        icon: "HTML", desc: "Learn the core markup and styling languages of the web.", time: "1.5 hr", diff: "Easy", quizzes: 5, resources: [
            { type: "video", title: "HTML & CSS Full Course for Beginners", url: "https://www.youtube.com/watch?v=Dpajb4F1Hwg" },
            { type: "doc", title: "MDN Web Docs - HTML Basics", url: "https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/HTML_basics" },
            { type: "practice", title: "CSS Diner - Interactive CSS Practice", url: "https://flukeout.github.io/" }
        ], project: "Portfolio Landing Page", projectDesc: "Create a personal responsive portfolio landing page using semantic HTML and flexbox.", notesPlaceholder: "HTML provides structure. CSS controls presentation. Master flexbox and CSS variables."
    },
    "JavaScript": {
        icon: "JS", desc: "Add interactivity and logic to your frontend applications.", time: "3 hr", diff: "Medium", quizzes: 6, resources: [
            { type: "video", title: "JavaScript ES6+ Modern Course", url: "https://www.youtube.com/watch?v=d51vODW0cBA" },
            { type: "doc", title: "MDN JavaScript Guide", url: "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide" },
            { type: "practice", title: "JavaScript Challenges on Exercism", url: "https://exercism.org/tracks/javascript" }
        ], project: "Interactive Calculator", projectDesc: "Build an interactive calculator with standard operations and theme switching.", notesPlaceholder: "Understand DOM manipulation, event listeners, array methods, and async programming."
    },
    "Bootstrap": {
        icon: "BS", desc: "Fast-track design using the world's most popular CSS framework.", time: "1 hr", diff: "Easy", quizzes: 5, resources: [
            { type: "video", title: "Bootstrap 5 Crash Course", url: "https://www.youtube.com/watch?v=Jyvffr3aCp0" },
            { type: "doc", title: "Bootstrap 5 Official Docs", url: "https://getbootstrap.com/docs/5.3/getting-started/introduction/" },
            { type: "practice", title: "W3Schools Bootstrap Exercises", url: "https://www.w3schools.com/bootstrap5/index.php" }
        ], project: "Responsive Pricing Table", projectDesc: "Build a modern responsive multi-tier product pricing page using Bootstrap layout utility classes.", notesPlaceholder: "Utilize utility classes for spacing, flexbox alignment, grids, and components."
    },
    "Figma basics": {
        icon: "🎨", desc: "Learn the fundamentals of designing high-fidelity UIs in Figma.", time: "1.2 hr", diff: "Easy", quizzes: 5, resources: [
            { type: "video", title: "Figma UI Design for Beginners", url: "https://www.youtube.com/watch?v=dXQ7IHkTiMM" },
            { type: "doc", title: "Figma Getting Started Guide", url: "https://help.figma.com/hc/en-us/articles/360040328273-Get-started-with-Figma" },
            { type: "practice", title: "Figma Basics Interactive Playground", url: "https://figma.com/" }
        ], project: "Profile Dashboard Wireframe", projectDesc: "Design a desktop dashboard wireframe including sidebar and widgets in Figma.", notesPlaceholder: "Master frames, auto-layout, components, and basic prototyping transitions."
    },
    "Components": {
        icon: "⚛️", desc: "Understand React components, state, and properties.", time: "2.5 hr", diff: "Medium", quizzes: 5, resources: [
            { type: "video", title: "React JS Basics for Beginners", url: "https://www.youtube.com/watch?v=w7ejDZ8SWv8" },
            { type: "doc", title: "React Docs - Your First Component", url: "https://react.dev/learn/your-first-component" },
            { type: "practice", title: "Create React App CRUD challenges", url: "https://react.dev/learn" }
        ], project: "Custom Profile Card Widget", projectDesc: "Build reusable React components displaying user statistics and custom hover actions.", notesPlaceholder: "Components are building blocks. Props are read-only inputs, State is local mutable memory."
    },
    "State Management": {
        icon: "📦", desc: "Manage application state globally using Redux or Context API.", time: "3 hr", diff: "Hard", quizzes: 5, resources: [
            { type: "video", title: "Redux Toolkit & Context API Complete Guide", url: "https://www.youtube.com/watch?v=5yEG6GhoJBs" },
            { type: "doc", title: "React Docs - Managing State", url: "https://react.dev/learn/managing-state" },
            { type: "practice", title: "Global Context Tasks", url: "https://react.dev/learn/passing-data-deeply-with-context" }
        ], project: "Shopping Cart App with Global State", projectDesc: "Design a shopping cart using global Context API or Redux Toolkit to sync prices and items.", notesPlaceholder: "Context avoids prop-drilling. Redux RTK is recommended for larger enterprise states."
    },
    
    // AI / Data Science
    "Syntax & Variables": {
        icon: "Py", desc: "Learn basic Python variables, types, and mathematical operations.", time: "45 min", diff: "Easy", quizzes: 5, resources: [
            { type: "video", title: "Python Basics for Data Science", url: "https://www.youtube.com/watch?v=rfscVS0vtbw" },
            { type: "doc", title: "Python Official Tutorial", url: "https://docs.python.org/3/tutorial/introduction.html" },
            { type: "practice", title: "Python Syntax Practice on Exercism", url: "https://exercism.org/tracks/python" }
        ], project: "Basic Math Script", projectDesc: "Write a command-line script to calculate statistics (mean, median) from input lists.", notesPlaceholder: "Python is whitespace-sensitive. Variables are dynamically typed but strongly typed."
    },
    "Functions & Classes": {
        icon: "OOP", desc: "Learn modular scripting and object-oriented programming in Python.", time: "1.5 hr", diff: "Medium", quizzes: 6, resources: [
            { type: "video", title: "Object Oriented Programming in Python", url: "https://www.youtube.com/watch?v=JeznW_7DlB0" },
            { type: "doc", title: "Python Classes & Objects", url: "https://docs.python.org/3/tutorial/classes.html" },
            { type: "practice", title: "OOP Python Exercises on RealPython", url: "https://realpython.com/python3-object-oriented-programming/" }
        ], project: "Student Gradebook System", projectDesc: "Design a class structure in Python simulating students, courses, and grade calculations.", notesPlaceholder: "Classes define templates. Methods represent behaviors. __init__ is the constructor."
    },
    "Pandas": {
        icon: "🐼", desc: "Learn high-performance data manipulation and analytics using Pandas.", time: "2 hr", diff: "Medium", quizzes: 5, resources: [
            { type: "video", title: "Pandas Complete Tutorial for Data Science", url: "https://www.youtube.com/watch?v=vmEHCJofslg" },
            { type: "doc", title: "Pandas Official 10-Minute Guide", url: "https://pandas.pydata.org/docs/user_guide/10min.html" },
            { type: "practice", title: "Pandas DataFrame Exercises", url: "https://pandas.pydata.org/docs/user_guide/index.html" }
        ], project: "CSV Data Cleaner CLI", projectDesc: "Load a messy dataset using Pandas, clean null values, normalize formats, and export a report.", notesPlaceholder: "DataFrames represent tables. Series are columns. Utilize vectorization over looping."
    },
    "Matplotlib": {
        icon: "📊", desc: "Visualize insights using Matplotlib and Seaborn charts.", time: "1 hr", diff: "Medium", quizzes: 5, resources: [
            { type: "video", title: "Matplotlib Data Visualization Full Course", url: "https://www.youtube.com/watch?v=DAQNHzOcO5A" },
            { type: "doc", title: "Matplotlib Quickstart Guide", url: "https://matplotlib.org/stable/tutorials/introductory/quickstart.html" },
            { type: "practice", title: "Chart Plotting Exercises", url: "https://matplotlib.org/stable/gallery/index.html" }
        ], project: "Sales Report Plotter", projectDesc: "Generate line charts, scatter plots, and bar graphs representing mock monthly sales distributions.", notesPlaceholder: "Understand figure vs axes objects, customization of colors, grids, and legend anchors."
    },
    "Scikit-Learn": {
        icon: "🤖", desc: "Build standard predictive ML models using Scikit-Learn.", time: "3 hr", diff: "Hard", quizzes: 5, resources: [
            { type: "video", title: "Scikit-Learn Machine Learning Guide", url: "https://www.youtube.com/watch?v=0Lt9w-ROKFQ" },
            { type: "doc", title: "Scikit-Learn Tutorial", url: "https://scikit-learn.org/stable/tutorial/basic/tutorial.html" },
            { type: "practice", title: "Model Fitting Exercises", url: "https://scikit-learn.org/stable/auto_examples/index.html" }
        ], project: "House Price Predictor", projectDesc: "Fit a linear regression model to predict housing valuations based on bedroom counts and locations.", notesPlaceholder: "Train-test split, model.fit(), model.predict(), and evaluation metrics like MSE or accuracy."
    },
    "Neural Networks Basics": {
        icon: "🧠", desc: "Build neural network classifiers using TensorFlow or PyTorch.", time: "4 hr", diff: "Hard", quizzes: 5, resources: [
            { type: "video", title: "Neural Networks & Deep Learning Intro", url: "https://www.youtube.com/watch?v=aircAruvnKk" },
            { type: "doc", title: "DeepLearning.AI Network Basics", url: "https://www.deeplearning.ai/resources/what-is-a-neural-network/" },
            { type: "practice", title: "Model design challenges", url: "https://www.tensorflow.org/tutorials/keras/classification" }
        ], project: "Handwritten Digit Classifier", projectDesc: "Train a simple feedforward neural network on the MNIST dataset to classify digits with >95% accuracy.", notesPlaceholder: "Layers, activation functions (ReLU, Sigmoid), optimizer (Adam), and loss metrics."
    },
    
    // Backend Developer
    "Variables": {
        icon: "x=", desc: "Learn basic data types, variables, and allocations in Python.", time: "45 min", diff: "Easy", quizzes: 5, resources: [
            { type: "video", title: "Python Variables and Types", url: "https://www.youtube.com/watch?v=cQT33yukyDM" },
            { type: "doc", title: "Real Python: Variables in Python", url: "https://realpython.com/python-variables/" },
            { type: "practice", title: "Python Variables Exercises", url: "https://www.w3schools.com/python/python_variables.asp" }
        ], project: "Currency Converter Script", projectDesc: "Write a script that takes user input to convert cash denominations based on conversion ratios.", notesPlaceholder: "Dynamic variables act as object pointers. Understand immutable vs mutable types."
    },
    "Loops": {
        icon: "🔄", desc: "Master loops and conditional iteration blocks in Python.", time: "1 hr", diff: "Easy", quizzes: 5, resources: [
            { type: "video", title: "Python Loops Tutorial", url: "https://www.youtube.com/watch?v=6iF8Xb7Z3wQ" },
            { type: "doc", title: "Python Control Flow & Loops", url: "https://docs.python.org/3/tutorial/controlflow.html" },
            { type: "practice", title: "Hackerrank Python loops track", url: "https://www.hackerrank.com/domains/python" }
        ], project: "Number Guessing Game", projectDesc: "Build a game where the user guesses a randomized number with conditional loop limits.", notesPlaceholder: "For loops are used for sequences. While loops require explicit termination state flags."
    },
    "Functions": {
        icon: "f(x)", desc: "Build modular, reusable code structures using custom functions.", time: "1.2 hr", diff: "Medium", quizzes: 5, resources: [
            { type: "video", title: "Python Functions - Complete Course", url: "https://www.youtube.com/watch?v=NSbOtYzIQI0" },
            { type: "doc", title: "Defining Functions - Official Docs", url: "https://docs.python.org/3/tutorial/controlflow.html#defining-functions" },
            { type: "practice", title: "Function exercises on Exercism", url: "https://exercism.org/tracks/python" }
        ], project: "Math Helper Module", projectDesc: "Build a helper library declaring algebraic functions that can be imported into other files.", notesPlaceholder: "Focus on scope, arguments (*args, **kwargs), return values, and docstrings."
    },
    "Databases": {
        icon: "🗄️", desc: "Understand relational databases, schemas, and writing SQL queries.", time: "2 hr", diff: "Medium", quizzes: 6, resources: [
            { type: "video", title: "SQL Basics & Relational Database Tutorial", url: "https://www.youtube.com/watch?v=HXV3zeQKqGY" },
            { type: "doc", title: "SQL Tutorial for Beginners", url: "https://www.w3schools.com/sql/" },
            { type: "practice", title: "SQLBolt Interactive Lessons", url: "https://sqlbolt.com/" }
        ], project: "Bookstore Schema Setup", projectDesc: "Write SQL statements to define tables for authors, books, and sales, inserting sample records.", notesPlaceholder: "Focus on primary keys, foreign key relations, joins, and indexing select columns."
    },
    "FastAPI/Django": {
        icon: "⚡", desc: "Build fast backend web applications using modern python frameworks.", time: "3 hr", diff: "Hard", quizzes: 5, resources: [
            { type: "video", title: "FastAPI Tutorial for Beginners", url: "https://www.youtube.com/watch?v=tLKKmouUaRQ" },
            { type: "doc", title: "FastAPI Official Documentation", url: "https://fastapi.tiangolo.com/" },
            { type: "practice", title: "First FastAPI API challenges", url: "https://fastapi.tiangolo.com/tutorial/first-steps/" }
        ], project: "API Book Inventory", projectDesc: "Write a CRUD API utilizing FastAPI path and query variables, validating inputs via Pydantic.", notesPlaceholder: "FastAPI automatically handles JSON parsing, Pydantic validations, and generates Swagger documentation."
    },
    "Routing": {
        icon: "🛣️", desc: "Learn to design RESTful endpoint path structures.", time: "1.5 hr", diff: "Medium", quizzes: 5, resources: [
            { type: "video", title: "FastAPI API Routing Guide", url: "https://www.youtube.com/watch?v=GjHDw2J7QTI" },
            { type: "doc", title: "FastAPI Router Setup - Bigger Applications", url: "https://fastapi.tiangolo.com/tutorial/bigger-applications/" },
            { type: "practice", title: "W3Schools REST API guidelines", url: "https://fastapi.tiangolo.com/tutorial/bigger-applications/#apirouter" }
        ], project: "Modular Backend Router", projectDesc: "Refactor a monolithic backend server into clean, separate router files using APIRouter.", notesPlaceholder: "Organize API endpoints under logical routers (e.g. users, products, categories) with tags."
    },
    "Build API": {
        icon: "🚀", desc: "Build a complete REST API from scratch with database integration.", time: "4 hr", diff: "Hard", quizzes: 8, resources: [
            { type: "video", title: "FastAPI with SQLAlchemy Database persistence", url: "https://www.youtube.com/watch?v=0sOvCWFmrtA" },
            { type: "doc", title: "FastAPI Database Tutorial Guide", url: "https://fastapi.tiangolo.com/tutorial/sql-databases/" },
            { type: "practice", title: "Full integration challenges", url: "https://fastapi.tiangolo.com/tutorial/" }
        ], project: "Library System API Service", projectDesc: "Deploy a library management REST API persisting book records in an SQLite database using SQLAlchemy.", notesPlaceholder: "Ensure DB sessions are correctly closed via dependency injection. Implement secure error handling."
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const nodesContainer = document.getElementById('nodesContainer');
    const pathCompleted = document.getElementById('pathCompleted');
    const pathLocked = document.getElementById('pathLocked');
    const canvasLoader = document.getElementById('canvasLoader');
    
    // Header stat elements
    const journeyTitle = document.getElementById('journeyTitle');
    const overallProgressVal = document.getElementById('overallProgressVal');
    const overallProgressBar = document.getElementById('overallProgressBar');
    const currentPositionVal = document.getElementById('currentPositionVal');
    const nextDestinationVal = document.getElementById('nextDestinationVal');
    const estCompletionVal = document.getElementById('estCompletionVal');
    
    // Details Panel elements
    const panelEmptyState = document.getElementById('panelEmptyState');
    const panelActiveContent = document.getElementById('panelActiveContent');
    const panelTopicIcon = document.getElementById('panelTopicIcon');
    const panelTopicTitle = document.getElementById('panelTopicTitle');
    const panelTopicDesc = document.getElementById('panelTopicDesc');
    const panelMetaTime = document.getElementById('panelMetaTime');
    const panelMetaDiff = document.getElementById('panelMetaDiff');
    const panelMetaQuizzes = document.getElementById('panelMetaQuizzes');
    const panelMetaResources = document.getElementById('panelMetaResources');
    const panelResourceList = document.getElementById('panelResourceList');
    const panelProjectTitle = document.getElementById('panelProjectTitle');
    const panelProjectDesc = document.getElementById('panelProjectDesc');
    const panelNotesArea = document.getElementById('panelNotesArea');
    const panelStartLearnBtn = document.getElementById('panelStartLearnBtn');
    const panelTakeQuizBtn = document.getElementById('panelTakeQuizBtn');
    const panelSaveNotesBtn = document.getElementById('panelSaveNotesBtn');

    let userDetails = null;
    let roadmapData = [];
    let progressData = [];
    let totalScore = 0;
    let activeNodeIndex = 0;
    let selectedStepId = null;
    let activeRoadmapId = null;

    const trackSwitcherBtn = document.getElementById('trackSwitcherBtn');
    const trackSwitcherMenu = document.getElementById('trackSwitcherMenu');

    let currentAbortController = null;

    function showPageLoader() {
        const loader = document.getElementById('pageLoader');
        const errorOverlay = document.getElementById('pageErrorOverlay');
        if (loader) {
            loader.classList.remove('d-none');
            loader.classList.add('d-flex');
            loader.style.opacity = '1';
        }
        if (errorOverlay) {
            errorOverlay.classList.add('d-none');
            errorOverlay.classList.remove('d-flex');
        }
    }

    function hidePageLoader() {
        const loader = document.getElementById('pageLoader');
        if (loader) {
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.classList.add('d-none');
                loader.classList.remove('d-flex');
            }, 300);
        }
    }

    function showPageError(message) {
        hidePageLoader();
        const errorOverlay = document.getElementById('pageErrorOverlay');
        const errMsgText = document.getElementById('pageErrorMessage');
        if (errMsgText && message) {
            errMsgText.textContent = message;
        }
        if (errorOverlay) {
            errorOverlay.classList.remove('d-none');
            errorOverlay.classList.add('d-flex');
        }
    }

    function getRoadmapIdFromHash() {
        const hash = window.location.hash;
        if (hash && hash.startsWith('#path=')) {
            const idVal = parseInt(hash.replace('#path=', ''), 10);
            return isNaN(idVal) ? null : idVal;
        }
        return null;
    }

    async function loadAndRenderRoadmap(roadmapId) {
        // Abort previous running requests to prevent race conditions
        if (currentAbortController) {
            currentAbortController.abort();
        }
        currentAbortController = new AbortController();
        const signal = currentAbortController.signal;

        showPageLoader();

        try {
            const token = getToken();
            const headers = { 
                "Authorization": "Bearer " + token,
                "Content-Type": "application/json"
            };

            // 1. Load user details
            const userResponse = await fetch(`${API_BASE_URL}/users/me`, { headers, signal });
            if (handle401Error(userResponse)) return;
            if (!userResponse.ok) throw new Error("Failed to retrieve user details.");
            
            userDetails = await userResponse.json();
            if (document.getElementById('sidebarUsername')) {
                document.getElementById('sidebarUsername').textContent = userDetails.username;
            }

            const urlParams = new URLSearchParams(window.location.search);
            const isPlacement = urlParams.get('type') === 'placement';

            if (isPlacement) {
                // Hide switcher and actions for placement
                const switcherBtn = document.getElementById('trackSwitcherBtn');
                const addPathBtn = document.getElementById('createNewJourneyBtn');
                const actionsBtn = document.getElementById('journeyActionsBtn');
                if (switcherBtn) switcherBtn.classList.add('d-none');
                if (addPathBtn) addPathBtn.classList.add('d-none');
                if (actionsBtn) actionsBtn.classList.add('d-none');
                
                const titleEl = document.getElementById('journeyTitle');
                if (titleEl) titleEl.textContent = "Placement Preparation Roadmap";

                // Fetch placement specific roadmap
                const roadmapResponse = await fetch(`${API_BASE_URL}/placement-roadmap`, { headers, signal });
                if (handle401Error(roadmapResponse)) return;
                if (!roadmapResponse.ok) throw new Error("Failed to load placement roadmap.");
                const rData = await roadmapResponse.json();
                activeRoadmapId = rData.id;
                roadmapData = [rData];

                // Fetch placement specific progress and score
                const [progressResponse, scoreResponse] = await Promise.all([
                    fetch(`${API_BASE_URL}/placement-roadmap/progress?roadmap_id=${activeRoadmapId}`, { headers, signal }),
                    fetch(`${API_BASE_URL}/placement-roadmap/progress/score?roadmap_id=${activeRoadmapId}`, { headers, signal })
                ]);

                if (progressResponse && progressResponse.ok) {
                    progressData = await progressResponse.json();
                }
                if (scoreResponse && scoreResponse.ok) {
                    const sData = await scoreResponse.json();
                    totalScore = sData.score;
                }

                renderJourneyMap();
                hidePageLoader();
                return; // Early return to avoid executing learning path logic!
            }

            // Decide which roadmap ID to load
            let targetId = roadmapId || userDetails.selected_roadmap_id;

            // Check if there is NO roadmap at all
            if (!targetId) {
                // Let's check status to see if one is currently generating
                const statusRes = await fetch(`${API_BASE_URL}/roadmap/status`, { headers, signal });
                if (statusRes.ok) {
                    const statusData = await statusRes.json();
                    if (statusData.status === 'GENERATING') {
                        window.location.href = 'questionnaire.html';
                        return;
                    }
                }
                
                if (!userDetails.onboarding_completed) {
                    window.location.href = 'welcome.html';
                    return;
                }
                
                window.location.href = 'questionnaire.html';
                return;
            }

            activeRoadmapId = targetId;
            // Update URL hash without triggering hashchange reload loop
            if (window.location.hash !== `#path=${targetId}`) {
                window.history.replaceState(null, null, `#path=${targetId}`);
            }

            // If user's selected_roadmap_id in the DB is different, select it
            if (userDetails.selected_roadmap_id !== targetId) {
                await fetch(`${API_BASE_URL}/roadmap/select/${targetId}`, { method: 'POST', headers, signal });
            }

            // 2. Fetch specific roadmap data
            const roadmapResponse = await fetch(`${API_BASE_URL}/roadmap/${targetId}`, { headers, signal });
            if (handle401Error(roadmapResponse)) return;
            if (!roadmapResponse.ok) throw new Error("Failed to load learning path roadmap.");
            const rData = await roadmapResponse.json();
            roadmapData = [rData];

            // 3. Fetch progress and score concurrently
            const [progressResponse, scoreResponse] = await Promise.all([
                fetch(`${API_BASE_URL}/progress`, { headers, signal }),
                fetch(`${API_BASE_URL}/progress/score`, { headers, signal }),
                fetch(`${API_BASE_URL}/roadmap/suggestions`, { headers, signal }).catch(() => {})
            ]);

            if (progressResponse && progressResponse.ok) {
                progressData = await progressResponse.json();
            }
            if (scoreResponse && scoreResponse.ok) {
                const sData = await scoreResponse.json();
                totalScore = sData.score;
            }

            // Refresh the journey dropdown state dynamically
            if (typeof refreshJourneyManager === 'function') {
                await refreshJourneyManager();
            }

            // Render
            renderJourneyMap();
            hidePageLoader();

        } catch (error) {
            if (error.name === 'AbortError') {
                console.log("Obsolete request aborted.");
                return;
            }
            console.error("Error loading path:", error);
            showPageError(error.message || "Failed to retrieve your personalized roadmap.");
        }
    }

    async function init() {
        // Wire up error overlay buttons
        const pageRetryBtn = document.getElementById('pageRetryBtn');
        const pageDashboardBtn = document.getElementById('pageDashboardBtn');
        if (pageRetryBtn) {
            pageRetryBtn.addEventListener('click', () => {
                const targetId = activeRoadmapId || getRoadmapIdFromHash();
                loadAndRenderRoadmap(targetId);
            });
        }
        if (pageDashboardBtn) {
            pageDashboardBtn.addEventListener('click', () => {
                window.location.href = 'dashboard.html';
            });
        }

        // Initialize Shared Journey Manager
        await initJourneyManager(async (newRoadmapId) => {
            if (newRoadmapId && newRoadmapId !== activeRoadmapId) {
                window.location.hash = `path=${newRoadmapId}`;
            }
        });

        // Listen for hashchange to support browser Back/Forward/Refresh
        window.addEventListener('hashchange', () => {
            const hashId = getRoadmapIdFromHash();
            if (hashId && hashId !== activeRoadmapId) {
                loadAndRenderRoadmap(hashId);
            }
        });

        // Perform initial load based on hash or default selected roadmap
        const initialId = getRoadmapIdFromHash();
        await loadAndRenderRoadmap(initialId);
    }

    // Snaking coordinates algorithm
    function getNodeCoordinates(index, total) {
        const cols = 4; // 4 columns winding snaker
        const row = Math.floor(index / cols);
        let col = index % cols;
        
        // Alternate column sequence for winding effect
        if (row % 2 === 1) {
            col = (cols - 1) - col;
        }
        
        // Percent grid coordinates
        const x = 12 + col * 25.3; // values map between 12% and 88%
        const y = 18 + row * 23.5; // values map between 18% and 88%
        
        // Dynamic organic curve offset
        const yOffset = Math.sin(index * 1.6) * 4.5;
        return { x, y: y + yOffset };
    }

    // Build SVG smooth Bezier curve connecting nodes
    function buildBezierPath(points) {
        if (points.length === 0) return "";
        const toYPx = (yVal) => (yVal / 100) * 620;
        let d = `M ${points[0].x} ${toYPx(points[0].y)}`;
        for (let i = 0; i < points.length - 1; i++) {
            const pA = points[i];
            const pB = points[i+1];
            const cp1x = pA.x + (pB.x - pA.x) / 2;
            const cp1y = toYPx(pA.y);
            const cp2x = pA.x + (pB.x - pA.x) / 2;
            const cp2y = toYPx(pB.y);
            d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${pB.x} ${toYPx(pB.y)}`;
        }
        return d;
    }

    function renderJourneyMap() {
        if (canvasLoader) canvasLoader.classList.add('d-none');
        
        // Clear SVG paths to prevent visual artifacts
        if (pathCompleted) pathCompleted.setAttribute('d', '');
        if (pathLocked) pathLocked.setAttribute('d', '');

        if (!nodesContainer) return;
        nodesContainer.innerHTML = '';

        if (!roadmapData || roadmapData.length === 0) {
            nodesContainer.innerHTML = '<div class="alert alert-info m-4">No roadmap generated</div>';
            return;
        }

        // Find active/selected roadmap
        const rmap = roadmapData.find(r => r.id === activeRoadmapId) || [...roadmapData].sort((a, b) => b.id - a.id)[0];
        if (journeyTitle) journeyTitle.innerText = rmap.title;

        // Flatten all micro steps from macro sections in order
        const steps = [];
        rmap.macro_steps.forEach(macro => {
            macro.micro_steps.forEach(micro => {
                steps.push(micro);
            });
        });

        const completedIds = new Set(progressData.filter(p => p.is_completed).map(p => p.micro_step_id));
        
        // Find current position index
        let currentIdx = 0;
        for (let i = 0; i < steps.length; i++) {
            if (!completedIds.has(steps[i].id)) {
                currentIdx = i + 1; // offset by 1 for START node
                break;
            }
            if (i === steps.length - 1) {
                currentIdx = steps.length + 1; // all completed, active node is the Goal
            }
        }
        activeNodeIndex = currentIdx;

        // Calculate total progress
        const completedCount = steps.filter(s => completedIds.has(s.id)).length;
        const progressPct = steps.length > 0 ? Math.round((completedCount / steps.length) * 100) : 0;
        
        if (overallProgressVal) overallProgressVal.innerText = `${progressPct}%`;
        if (overallProgressBar) overallProgressBar.style.width = `${progressPct}%`;
        
        // Set stats header values
        const activeNode = steps[Math.max(0, currentIdx - 1)] || null;
        const nextNode = steps[Math.min(steps.length - 1, currentIdx)] || null;
        
        if (currentPositionVal) currentPositionVal.innerText = activeNode ? activeNode.title : "Goal Reached!";
        if (nextDestinationVal) nextDestinationVal.innerText = nextNode ? nextNode.title : "Trophy!";
        
        // Est. completion based on remaining easy/medium/hard steps
        let remainingDays = 0;
        steps.forEach((s, idx) => {
            if (idx >= completedCount) {
                if (s.difficulty.toLowerCase() === 'easy') remainingDays += 0.5;
                else if (s.difficulty.toLowerCase() === 'medium') remainingDays += 1;
                else remainingDays += 2;
            }
        });
        if (estCompletionVal) estCompletionVal.innerText = remainingDays > 0 ? `${Math.ceil(remainingDays)} days` : "Complete!";

        // Assemble points: START + steps + GOAL
        const totalNodes = steps.length + 2;
        const points = [];
        for (let i = 0; i < totalNodes; i++) {
            points.push(getNodeCoordinates(i, totalNodes));
        }

        // Calculate maximum Y value and required wrapper height in pixels
        const cols = 4;
        const maxRow = Math.floor((totalNodes - 1) / cols);
        const maxY = 18 + maxRow * 23.5 + 4.5;
        const wrapperHeight = Math.max(620, (maxY / 100) * 620 + 80);

        // Dynamically adjust internal sizes for scrolling without changing original dimensions
        const canvasWrapper = document.getElementById('canvasWrapper');
        const roadmapSvg = document.getElementById('roadmapSvg');
        if (canvasWrapper) {
            canvasWrapper.style.overflowY = 'auto';
            canvasWrapper.style.overflowX = 'hidden';
            const landscapeBg = canvasWrapper.querySelector('.landscape-bg');
            if (landscapeBg) {
                landscapeBg.style.height = `${wrapperHeight}px`;
            }
        }
        if (roadmapSvg) {
            roadmapSvg.style.height = `${wrapperHeight}px`;
            roadmapSvg.setAttribute('viewBox', `0 0 100 ${wrapperHeight}`);
        }
        if (nodesContainer) {
            nodesContainer.style.height = `${wrapperHeight}px`;
        }

        // Render SVG Path Segment Lines
        // Completed: 0 up to currentIdx
        const completedPoints = points.slice(0, currentIdx + 1);
        pathCompleted.setAttribute('d', buildBezierPath(completedPoints));

        // Locked: currentIdx to end
        const lockedPoints = points.slice(currentIdx);
        pathLocked.setAttribute('d', buildBezierPath(lockedPoints));

        // Render Node 0: START
        const startPoint = points[0];
        const startNode = createNodeElement(startPoint, 'start', {
            title: "START",
            status: "completed",
            icon: `<i class="bi bi-play-fill text-white fs-4" style="margin-left: 2px;"></i>`
        });
        nodesContainer.appendChild(startNode);

        // Render Nodes 1 to N: Micro Steps
        steps.forEach((step, index) => {
            const point = points[index + 1];
            const nodeIdx = index + 1;
            
            let status = "locked";
            if (nodeIdx < currentIdx) status = "completed";
            else if (nodeIdx === currentIdx) status = "current";

            // Load Rich Topic Metadata dynamically from step values returned by AI
            const details = {
                icon: step.title.substring(0, 3),
                desc: step.description || `Master the concepts of ${step.title}.`,
                time: `${step.estimated_hours || 1} hours`,
                diff: step.difficulty || "Medium",
                quizzes: step.quiz_required ? 1 : 0,
                resources: step.resources || []
            };

            const stepIcon = status === "completed" ? `<i class="bi bi-check-lg text-white"></i>` : 
                             status === "locked" ? `<i class="bi bi-lock-fill"></i>` : 
                             `<span style="font-size: 0.85rem; font-weight: 800;">${details.icon}</span>`;

            const nodeEl = createNodeElement(point, 'step', {
                id: step.id,
                title: step.title,
                status: status,
                icon: stepIcon,
                time: details.time,
                diff: step.difficulty || "Medium",
                quizzes: details.quizzes,
                resourcesCount: details.resources.length
            });

            nodeEl.addEventListener('click', () => selectJourneyStep(step, details, status));
            nodesContainer.appendChild(nodeEl);
        });

        // Render Node N+1: GOAL / TROPHY
        const goalPoint = points[points.length - 1];
        const goalStatus = currentIdx > steps.length ? "completed" : "locked";
        const goalIcon = `<i class="bi bi-trophy-fill"></i>`;
        
        const goalNode = createNodeElement(goalPoint, 'goal', {
            title: "JOB READY",
            status: goalStatus,
            icon: goalIcon
        });
        
        goalNode.addEventListener('click', () => {
            selectGoalNode(goalStatus);
        });
        nodesContainer.appendChild(goalNode);

        // Auto select current active node on launch
        if (currentIdx > 0 && currentIdx <= steps.length) {
            const activeStep = steps[currentIdx - 1];
            const activeDetails = {
                icon: activeStep.title.substring(0, 3),
                desc: activeStep.description || `Master the concepts of ${activeStep.title}.`,
                time: `${activeStep.estimated_hours || 1} hours`,
                diff: activeStep.difficulty || "Medium",
                quizzes: activeStep.quiz_required ? 1 : 0,
                resources: activeStep.resources || []
            };
            let status = "current";
            selectJourneyStep(activeStep, activeDetails, status);
        } else if (currentIdx > steps.length) {
            selectGoalNode("completed");
        }
    }

    function createNodeElement(point, type, data) {
        const div = document.createElement('div');
        div.className = `journey-node node-${data.status}`;
        if (type === 'goal') div.classList.add('node-goal');
        
        div.style.left = `${point.x}%`;
        div.style.top = `${(point.y / 100) * 620}px`;
        div.innerHTML = data.icon;

        // Label below node
        const label = document.createElement('div');
        label.className = 'node-label';
        label.innerText = data.title;
        div.appendChild(label);

        // Hover expand tooltip card (only for micro step nodes)
        if (type === 'step') {
            const hoverCard = document.createElement('div');
            hoverCard.className = 'node-hover-card';
            hoverCard.innerHTML = `
                <div class="node-hover-title">${data.title}</div>
                <div class="node-hover-meta">
                    <span><i class="bi bi-clock"></i> ${data.time}</span>
                    <span class="text-capitalize"><i class="bi bi-bar-chart-steps"></i> ${data.diff}</span>
                    <span><i class="bi bi-patch-check"></i> ${data.quizzes} Q</span>
                    <span><i class="bi bi-folder2"></i> ${data.resourcesCount} Res</span>
                </div>
            `;
            div.appendChild(hoverCard);
        }

        return div;
    }

    // Right detail panel updater
    function selectJourneyStep(step, details, status) {
        selectedStepId = step.id;
        if (panelEmptyState) panelEmptyState.classList.add('d-none');
        if (panelActiveContent) panelActiveContent.classList.remove('d-none');

        // Populate details
        if (panelTopicIcon) panelTopicIcon.innerText = details.icon;
        if (panelTopicTitle) panelTopicTitle.innerText = step.title;
        if (panelTopicDesc) panelTopicDesc.innerText = details.desc || step.description;

        if (panelMetaTime) panelMetaTime.innerText = details.time;
        if (panelMetaDiff) panelMetaDiff.innerText = step.difficulty;
        if (panelMetaQuizzes) panelMetaQuizzes.innerText = `${details.quizzes} Questions`;
        if (panelMetaResources) panelMetaResources.innerText = `${details.resources.length} Materials`;

        // Render resources list
        if (panelResourceList) {
            panelResourceList.innerHTML = '';
            details.resources.forEach(res => {
                const item = document.createElement('a');
                item.className = 'resource-item';
                item.href = res.url;
                item.target = '_blank';
                
                let iconClass = 'bi-file-earmark-text-fill';
                if (res.type === 'video') iconClass = 'bi-play-circle-fill';
                else if (res.type === 'practice') iconClass = 'bi-code-square';

                item.innerHTML = `
                    <div class="d-flex align-items-center">
                        <i class="bi ${iconClass} type-icon"></i>
                        <span>${res.title}</span>
                    </div>
                    <i class="bi bi-chevron-right chevron-icon"></i>
                `;
                panelResourceList.appendChild(item);
            });
        }

        // Mini project
        if (panelProjectTitle) panelProjectTitle.innerText = step.mini_project || "None";
        if (panelProjectDesc) panelProjectDesc.innerText = step.mini_project ? `Build a ${step.mini_project} to demonstrate your knowledge.` : "No project required.";

        // Notes loading
        if (panelNotesArea) {
            const savedNote = localStorage.getItem(`notes_step_${step.id}`);
            panelNotesArea.value = savedNote !== null ? savedNote : (details.notesPlaceholder || "");
        }

        // Configure buttons based on completion status
        if (panelStartLearnBtn) {
            panelStartLearnBtn.href = step.resource_link || "#";
            if (status === 'locked') {
                panelStartLearnBtn.classList.add('disabled');
                panelStartLearnBtn.innerText = "Locked Checkpoint";
            } else if (status === 'completed') {
                panelStartLearnBtn.classList.remove('disabled');
                panelStartLearnBtn.innerText = "Review Content";
            } else {
                panelStartLearnBtn.classList.remove('disabled');
                panelStartLearnBtn.innerText = "Start Learning";
            }
        }

        if (panelTakeQuizBtn) {
            const urlParamsCheck = new URLSearchParams(window.location.search);
            const isPlacementCheck = urlParamsCheck.get('type') === 'placement';
            const quizSuffix = isPlacementCheck ? '&type=placement' : '';

            panelTakeQuizBtn.classList.remove('disabled', 'btn-outline-secondary', 'btn-warning', 'btn-success');
            if (status === 'locked') {
                panelTakeQuizBtn.href = `quiz.html?micro_step_id=${step.id}${quizSuffix}`;
                panelTakeQuizBtn.classList.add('disabled', 'btn-outline-secondary');
                panelTakeQuizBtn.innerText = "Take Quiz";
            } else if (status === 'completed') {
                panelTakeQuizBtn.href = `quiz.html?micro_step_id=${step.id}${quizSuffix}`;
                panelTakeQuizBtn.classList.add('btn-warning');
                panelTakeQuizBtn.innerText = "Retake Quiz";
            } else {
                // status is current
                if (step.quiz_passed) {
                    panelTakeQuizBtn.href = "#";
                    panelTakeQuizBtn.classList.add('btn-success');
                    panelTakeQuizBtn.innerText = "Complete Checkpoint";
                } else {
                    panelTakeQuizBtn.href = `quiz.html?micro_step_id=${step.id}${quizSuffix}`;
                    panelTakeQuizBtn.classList.add('btn-warning');
                    panelTakeQuizBtn.innerText = "Take Quiz";
                }
            }
        }
    }

    function selectGoalNode(status) {
        selectedStepId = null;
        if (panelEmptyState) panelEmptyState.classList.add('d-none');
        if (panelActiveContent) panelActiveContent.classList.remove('d-none');

        if (panelTopicIcon) panelTopicIcon.innerHTML = `<i class="bi bi-trophy-fill text-warning"></i>`;
        if (panelTopicTitle) panelTopicTitle.innerText = "JOB READY!";
        if (panelTopicDesc) panelTopicDesc.innerText = "Congratulations! You have completed your path.";

        if (panelMetaTime) panelMetaTime.innerText = "Complete";
        if (panelMetaDiff) panelMetaDiff.innerText = "Master";
        if (panelMetaQuizzes) panelMetaQuizzes.innerText = "All passed";
        if (panelMetaResources) panelMetaResources.innerText = "All finished";

        if (panelResourceList) {
            panelResourceList.innerHTML = `
                <div class="text-center py-3 text-success fw-bold">
                    <i class="bi bi-patch-check-fill fs-3 d-block mb-2"></i>
                    You have unlocked all curriculum items!
                </div>
            `;
        }

        if (panelProjectTitle) panelProjectTitle.innerText = "Ultimate Capstone Project";
        if (panelProjectDesc) panelProjectDesc.innerText = "Deploy your full portfolio services and apply for jobs!";

        if (panelNotesArea) panelNotesArea.value = "Great job finishing your journey. You are ready to start applying for jobs!";

        if (panelStartLearnBtn) {
            panelStartLearnBtn.classList.add('disabled');
            panelStartLearnBtn.innerText = "Journey Finished";
        }
        if (panelTakeQuizBtn) {
            panelTakeQuizBtn.classList.add('disabled');
            panelTakeQuizBtn.innerText = "Completed";
        }
    }

    // Save notes handler
    if (panelSaveNotesBtn) {
        panelSaveNotesBtn.addEventListener('click', () => {
            if (selectedStepId && panelNotesArea) {
                const noteVal = panelNotesArea.value;
                localStorage.setItem(`notes_step_${selectedStepId}`, noteVal);
                alert("Personal notes saved successfully!");
            } else {
                alert("Please select a valid checkpoint first.");
            }
        });
    }

    // Complete checkpoint click handler
    if (panelTakeQuizBtn) {
        panelTakeQuizBtn.addEventListener('click', async (e) => {
            if (panelTakeQuizBtn.innerText === "Complete Checkpoint") {
                e.preventDefault();
                try {
                    const urlParamsCheck = new URLSearchParams(window.location.search);
                    const isPlacementCheck = urlParamsCheck.get('type') === 'placement';
                    const completeUrl = isPlacementCheck ? `${API_BASE_URL}/placement-roadmap/progress/complete` : `${API_BASE_URL}/progress/complete`;

                    const response = await fetch(completeUrl, {
                        method: 'POST',
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": "Bearer " + getToken()
                        },
                        body: JSON.stringify({
                            micro_step_id: selectedStepId
                        })
                    });
                    if (handle401Error(response)) return;
                    if (response.ok) {
                        alert("Checkpoint marked as completed!");
                        // Reload and refresh layout!
                        const token = getToken();
                        const headers = { 
                            "Authorization": "Bearer " + token,
                            "Content-Type": "application/json"
                        };
                        if (isPlacementCheck) {
                            const [pRes, sRes] = await Promise.all([
                                fetch(`${API_BASE_URL}/placement-roadmap/progress?roadmap_id=${activeRoadmapId}`, { headers }),
                                fetch(`${API_BASE_URL}/placement-roadmap/progress/score?roadmap_id=${activeRoadmapId}`, { headers })
                            ]);
                            if (pRes.ok) progressData = await pRes.json();
                            if (sRes.ok) {
                                const sData = await sRes.json();
                                totalScore = sData.score;
                            }
                        } else {
                            try {
                                await loadProgress();
                                await loadScore();
                            } catch (err_calc) {
                                const [pRes, sRes] = await Promise.all([
                                    fetch(`${API_BASE_URL}/progress`, { headers }),
                                    fetch(`${API_BASE_URL}/progress/score`, { headers })
                                ]);
                                if (pRes.ok) progressData = await pRes.json();
                                if (sRes.ok) {
                                    const sData = await sRes.json();
                                    totalScore = sData.score;
                                }
                            }
                        }
                        renderJourneyMap();
                    } else {
                        const err = await response.json();
                        alert("Error: " + (err.detail || "Failed to complete step."));
                    }
                } catch (error) {
                    console.error("Error completing step:", error);
                    alert("Network error. Please try again.");
                }
            }
        });
    }



    init();
});
