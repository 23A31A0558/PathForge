# 🚀 PathForge – Personalized AI Career Roadmap Platform

<div align="center">

### **Your AI Mentor for Learning, Skill Building & Placement Success**

*Generate personalized learning roadmaps, prepare for placements, practice AI-generated quizzes, and track your journey — all in one platform.*

</div>

---

# 📖 Overview

**PathForge** is an AI-powered career development platform that helps students learn the right skills in the right order.

Unlike traditional learning platforms that provide the same roadmap to everyone, PathForge generates **personalized AI learning paths** based on the user's:

- 🎯 Career Goal
- 📚 Current Skills
- ⏳ Available Time
- 💻 Technical Background
- 🎓 Academic Profile

It also includes a dedicated **Placement Preparation Module**, enabling students to prepare for campus placements through AI-generated placement roadmaps, aptitude preparation, DSA practice, interview guidance, and quizzes.

---

# ✨ Features

## 🎯 AI Personalized Learning Roadmaps

Generate customized learning paths for different careers including:

- Software Engineer
- Backend Developer
- Frontend Developer
- Full Stack Developer
- Data Scientist
- AI Engineer
- Machine Learning Engineer
- Cyber Security
- Cloud Engineer
- DevOps Engineer
- Data Analyst
- Mobile App Developer
- and many more...

---

## 🛤 Multiple Learning Paths

Users can maintain multiple independent learning journeys.

Example:

- Backend Development
- AI Engineering
- Cloud Computing

Each roadmap maintains its own:

- Progress
- Topics
- Projects
- Resources
- Quizzes

---

## 💼 AI Placement Preparation

Dedicated Placement Preparation Module.

Users complete a placement questionnaire including:

- Academic Information
- Aptitude Level
- DSA Level
- Target Companies
- Preparation Timeline

The AI then generates a personalized placement roadmap.

---

## 🧠 AI-Generated Quizzes

Every topic includes dynamically generated quizzes using AI.

Features:

- Topic-specific questions
- Multiple Choice Questions
- Difficulty progression
- Explanations
- Score Tracking

---

## 📚 Learning Resources

Each roadmap topic contains curated learning resources including:

- Articles
- Documentation
- Videos
- Practice Platforms

---

## 📈 Progress Tracking

Track your learning journey with:

- Completion Percentage
- Topic Progress
- Quiz Scores
- Learning Statistics

---

## 🎓 Roadmap Visualization

Interactive roadmap visualization featuring:

- Learning milestones
- Topic dependencies
- Progress indicators
- Interactive checkpoints

---

## 🤖 AI Powered

PathForge uses AI to generate:

- Personalized Roadmaps
- Placement Roadmaps
- Learning Resources
- Topic-wise Quizzes

---

# 🛠 Tech Stack

## Frontend

- HTML5
- CSS3
- JavaScript (Vanilla JS)
- Bootstrap 5

---

## Backend

- Python
- FastAPI

---

## Database

- SQLite
- SQLAlchemy ORM

---

## AI Integration

- Groq API
- LLM-powered roadmap generation
- AI quiz generation

---

## Authentication

- JWT Authentication
- Secure Login
- User Registration

---

# 🏗 Project Architecture

```
                User
                  │
                  ▼
        ┌──────────────────┐
        │    Frontend      │
        │ HTML/CSS/JS      │
        └────────┬─────────┘
                 │ REST API
                 ▼
        ┌──────────────────┐
        │     FastAPI      │
        │ Backend Services │
        └────────┬─────────┘
                 │
        ┌────────┼─────────┐
        ▼                  ▼
 SQLite Database      Groq AI API
        │                  │
        └────────┬─────────┘
                 ▼
       Personalized Roadmaps
```

---

# 🚀 Core Modules

### 👤 User Authentication

- Registration
- Login
- JWT Authentication
- Profile Management

---

### 📝 Learning Questionnaire

Collects:

- Career Goal
- Skills
- Experience
- Learning Style
- Timeline

Generates AI-powered personalized learning roadmap.

---

### 💼 Placement Questionnaire

Collects:

- College
- Branch
- Year
- Aptitude Level
- DSA Level
- Target Companies
- Timeline

Generates AI-powered placement roadmap.

---

### 🗺 Roadmap Generator

Creates structured learning paths consisting of:

- Phases
- Topics
- Resources
- Projects
- Quizzes

---

### 📊 Dashboard

Displays:

- Active Learning Path
- Progress
- Statistics
- Placement Module
- Multiple Roadmaps

---

### 🧩 Quiz Module

AI-generated quizzes for every roadmap topic.

Features:

- MCQs
- Explanations
- Score Calculation
- Progress Update

---

# 📂 Project Structure

```
PathForge
│
├── backend/
│   ├── ai/
│   ├── database.py
│   ├── models.py
│   ├── main.py
│   ├── roadmap_ai_service.py
│   ├── groq_ai_service.py
│   └── ...
│
├── frontend/
│   ├── css/
│   ├── js/
│   ├── dashboard.html
│   ├── roadmap.html
│   ├── questionnaire.html
│   ├── placement_questionnaire.html
│   ├── quiz.html
│   └── ...
│
├── start.py
├── requirements.txt
└── README.md
```

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/your-username/PathForge.git

cd PathForge
```

---

## Create Virtual Environment

```bash
python -m venv venv
```

Activate:

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment

Create a `.env` file inside the backend directory.

```env
GROQ_API_KEY=YOUR_API_KEY
JWT_SECRET_KEY=YOUR_SECRET
```

---

## Run Application

```bash
python start.py
```

or

```bash
uvicorn backend.main:app --reload
```

---

# 📷 Screenshots

Add screenshots here:

- Dashboard
- Learning Roadmap
- Placement Roadmap
- Questionnaire
- AI Loading Screen
- Quiz Module

---

# 🎯 Future Enhancements

- Mobile Application
- AI Chat Mentor
- Resume Analyzer
- Mock Interview Simulator
- Company-wise Preparation
- Weekly Progress Reports
- Team Learning
- Leaderboards
- Dark Mode
- Notifications

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository

2. Create a new branch

```bash
git checkout -b feature-name
```

3. Commit changes

```bash
git commit -m "Add feature"
```

4. Push

```bash
git push origin feature-name
```

5. Open a Pull Request

---

# 📜 License

This project is developed for educational and learning purposes.

---

# 👨‍💻 Author

## Sai Charan

**PathForge — AI-Powered Personalized Learning & Placement Preparation Platform**

GitHub:
https://github.com/your-username

LinkedIn:
https://linkedin.com/in/your-profile

---

<div align="center">

### ⭐ If you like this project, don't forget to star the repository!

**Made with ❤️ using FastAPI, Groq AI, HTML, CSS & JavaScript**

</div>
