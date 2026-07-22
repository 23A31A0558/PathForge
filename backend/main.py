import sys

# 1. Verify dependencies at startup
REQUIRED_MODULES = [
    ("dotenv", "python-dotenv"),
    ("groq", "groq"),
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("sqlalchemy", "sqlalchemy"),
    ("jose", "python-jose"),
    ("passlib", "passlib[bcrypt]"),
    ("pydantic", "pydantic"),
    ("email_validator", "email-validator"),
    ("requests", "requests"),
    ("httpx", "httpx"),
]

missing_modules = []
for module_name, package_name in REQUIRED_MODULES:
    try:
        __import__(module_name)
    except ImportError:
        missing_modules.append(package_name)

if missing_modules:
    print("*" * 80, file=sys.stderr)
    print(" CRITICAL ERROR: Missing required python packages for PathForge startup:", file=sys.stderr)
    for pkg in missing_modules:
        print(f" - {pkg}", file=sys.stderr)
    print(" Please install them using: pip install -r requirements.txt", file=sys.stderr)
    print("*" * 80, file=sys.stderr)
    sys.exit(1)

import os
from typing import List, Optional, Dict, Any, Union
import datetime
import time
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify GROQ_API_KEY exists (Warning only, do not crash server)
groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    print("WARNING: GROQ_API_KEY is not set in environment or .env file. AI Roadmap generation will fail with a clean error response.", file=sys.stderr)

# Setup logger
backend_logger = logging.getLogger("backend")
if not backend_logger.handlers:
    backend_logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    backend_logger.addHandler(ch)

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text, func
import models, schemas, auth, database
from database import engine

models.Base.metadata.create_all(bind=engine)

# Apply migrations for missing columns
try:
    with engine.begin() as conn:
        # Check and add selected_roadmap_id
        try:
            conn.execute(text("SELECT selected_roadmap_id FROM users LIMIT 1"))
        except Exception:
            conn.execute(text("ALTER TABLE users ADD COLUMN selected_roadmap_id INTEGER DEFAULT NULL"))
            
        # Check and add questionnaire_completed
        try:
            conn.execute(text("SELECT questionnaire_completed FROM users LIMIT 1"))
        except Exception:
            conn.execute(text("ALTER TABLE users ADD COLUMN questionnaire_completed BOOLEAN DEFAULT 0"))

        # Check and add onboarding_completed
        try:
            conn.execute(text("SELECT onboarding_completed FROM users LIMIT 1"))
        except Exception:
            conn.execute(text("ALTER TABLE users ADD COLUMN onboarding_completed BOOLEAN DEFAULT 0"))

        # Check and add is_archived to roadmaps
        try:
            conn.execute(text("SELECT is_archived FROM roadmaps LIMIT 1"))
        except Exception:
            conn.execute(text("ALTER TABLE roadmaps ADD COLUMN is_archived BOOLEAN DEFAULT 0"))

        # Check and add description to roadmaps
        try:
            conn.execute(text("SELECT description FROM roadmaps LIMIT 1"))
        except Exception:
            conn.execute(text("ALTER TABLE roadmaps ADD COLUMN description TEXT DEFAULT NULL"))

        # Check and add created_at to roadmaps
        try:
            conn.execute(text("SELECT created_at FROM roadmaps LIMIT 1"))
        except Exception:
            conn.execute(text("ALTER TABLE roadmaps ADD COLUMN created_at DATETIME DEFAULT NULL"))

        # Check and add generated_by_ai to roadmaps
        try:
            conn.execute(text("SELECT generated_by_ai FROM roadmaps LIMIT 1"))
        except Exception:
            conn.execute(text("ALTER TABLE roadmaps ADD COLUMN generated_by_ai BOOLEAN DEFAULT 1"))
except Exception as migration_err:
    print(f"Migration error: {migration_err}", sys.stderr)

app = FastAPI(title="PathForge API")

# HTTP logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    backend_logger.info(f"Incoming request: {request.method} {request.url.path}")
    start_time = time.time()
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        backend_logger.info(f"Response status: {response.status_code} for {request.method} {request.url.path} (Duration: {duration:.4f}s)")
        return response
    except Exception as e:
        duration = time.time() - start_time
        backend_logger.error(f"Exception during request {request.method} {request.url.path}: {str(e)} (Duration: {duration:.4f}s)")
        raise e


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    import logging
    logging.getLogger("backend").warning(f"HTTPException caught: {exc.detail} (Status: {exc.status_code})")
    detail_msg = exc.detail
    if exc.status_code == 404:
        detail_msg = "Endpoint not found"
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail_msg, "success": False, "message": detail_msg}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    import logging
    logging.getLogger("backend").warning(f"RequestValidationError caught: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "success": False, "message": "Validation error"}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import logging
    import traceback
    logging.getLogger("backend").error(f"CRITICAL: Unhandled Exception: {str(exc)}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "success": False,
            "message": "Internal server error",
            "details": str(exc)
        }
    )

from fastapi.middleware.cors import CORSMiddleware

import os
from dotenv import load_dotenv

load_dotenv()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    import logging
    import traceback
    backend_logger = logging.getLogger("backend")
    
    backend_logger.info(f"Incoming registration request: username={user.username}, email={user.email}")
    
    try:
        # Check duplicate email
        db_user_email = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user_email:
            backend_logger.warning(f"Registration failed: Email {user.email} already registered.")
            raise HTTPException(status_code=400, detail="Email already registered")
            
        # Check duplicate username
        db_user_name = db.query(models.User).filter(models.User.username == user.username).first()
        if db_user_name:
            backend_logger.warning(f"Registration failed: Username {user.username} already exists.")
            raise HTTPException(status_code=400, detail="Username already exists")
            
        # Password hashing
        try:
            hashed_password = auth.get_password_hash(user.password)
        except Exception as hash_err:
            backend_logger.error(f"Password hashing exception: {str(hash_err)}")
            raise HTTPException(status_code=500, detail=f"Failed to secure password: {str(hash_err)}")
            
        # Create user
        new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        backend_logger.info(f"User {user.username} successfully registered with ID {new_user.id}")
        return new_user
        
    except HTTPException as http_exc:
        # Safe rollback
        try:
            db.rollback()
        except Exception:
            pass
        raise http_exc
    except Exception as e:
        # Safe rollback
        try:
            db.rollback()
        except Exception:
            pass
        backend_logger.error(f"Unexpected exception during registration: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except auth.jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/users/select-roadmap")
def select_roadmap(
    payload: schemas.SelectRoadmapRequest,
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    roadmap = db.query(models.Roadmap).filter(
        models.Roadmap.id == payload.roadmap_id,
        models.Roadmap.user_id == current_user.id
    ).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found or not owned by user")
    
    current_user.selected_roadmap_id = roadmap.id
    db.commit()
    return {"message": "Active roadmap updated successfully", "selected_roadmap_id": roadmap.id}

@app.get("/users/status", response_model=schemas.UserStatusResponse)
def get_user_status(
    current_user: models.User = Depends(read_users_me)
):
    return {
        "questionnaire_completed": current_user.questionnaire_completed,
        "onboarding_completed": current_user.onboarding_completed,
        "selected_roadmap_id": current_user.selected_roadmap_id
    }

@app.get("/roadmap/status", response_model=schemas.RoadmapStatusResponse)
def get_roadmap_status(
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    status_rec = db.query(models.RoadmapGenerationStatus).filter(models.RoadmapGenerationStatus.user_id == current_user.id).first()
    if status_rec:
        return {
            "status": status_rec.status,
            "error_message": status_rec.error_message
        }
    
    # Fallback to check if roadmap records exist
    existing_roadmap = db.query(models.Roadmap).filter(models.Roadmap.user_id == current_user.id).first()
    if existing_roadmap:
        return {
            "status": "READY",
            "error_message": None
        }
        
    return {
        "status": "NOT_STARTED",
        "error_message": None
    }

@app.on_event("startup")
def seed_database():
    db = database.SessionLocal()
    # Run self-healing sqlite migrations
    try:
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS roadmap_generation_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                status VARCHAR,
                error_message VARCHAR,
                updated_at DATETIME
            )
        """))
        db.commit()
    except Exception:
        pass
    try:
        db.execute(text("ALTER TABLE users ADD COLUMN selected_roadmap_id INTEGER"))
        db.commit()
    except Exception:
        pass
    try:
        db.execute(text("ALTER TABLE users ADD COLUMN questionnaire_completed BOOLEAN DEFAULT 0"))
        db.commit()
    except Exception:
        pass
    try:
        db.execute(text("ALTER TABLE users ADD COLUMN onboarding_completed BOOLEAN DEFAULT 0"))
        db.commit()
    except Exception:
        pass
    try:
        db.execute(text("UPDATE users SET onboarding_completed = 1 WHERE questionnaire_completed = 1"))
        db.commit()
    except Exception:
        pass
    try:
        db.execute(text("ALTER TABLE roadmaps ADD COLUMN is_archived BOOLEAN DEFAULT 0"))
        db.commit()
    except Exception:
        pass
    try:
        db.execute(text("ALTER TABLE roadmaps ADD COLUMN description VARCHAR"))
        db.commit()
    except Exception:
        pass
    try:
        db.execute(text("ALTER TABLE roadmaps ADD COLUMN created_at DATETIME"))
        db.commit()
    except Exception:
        pass
    try:
        db.execute(text("ALTER TABLE roadmaps ADD COLUMN generated_by_ai BOOLEAN DEFAULT 1"))
        db.commit()
    except Exception:
        pass
    try:
        db.execute(text("UPDATE users SET questionnaire_completed = 1 WHERE id IN (SELECT DISTINCT user_id FROM answers)"))
        db.commit()
    except Exception:
        pass

    # Groups self-healing migrations
    try:
        db.execute(text("ALTER TABLE groups ADD COLUMN group_name VARCHAR"))
        db.commit()
    except Exception:
        pass
    try:
        db.execute(text("ALTER TABLE groups ADD COLUMN description VARCHAR"))
        db.commit()
    except Exception:
        pass
    try:
        db.execute(text("ALTER TABLE groups ADD COLUMN owner_id INTEGER"))
        db.commit()
    except Exception:
        pass
    try:
        db.execute(text("ALTER TABLE groups ADD COLUMN created_at DATETIME"))
        db.commit()
    except Exception:
        pass
    try:
        db.execute(text("UPDATE groups SET group_name = name WHERE group_name IS NULL"))
        db.execute(text("UPDATE groups SET owner_id = created_by WHERE owner_id IS NULL"))
        db.execute(text("UPDATE groups SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
        db.commit()
    except Exception:
        pass

    # Check if questions exist
    if db.query(models.Question).first() is None:
        questions_data = [
            {"text": "Preferred role", "type": "radio", "options": [
                {"opt": "Backend", "val": "backend"},
                {"opt": "Frontend", "val": "frontend"},
                {"opt": "AI/Data", "val": "ai"},
                {"opt": "Not sure", "val": "not_sure"}
            ]},
            {"text": "Experience level", "type": "radio", "options": [
                {"opt": "Beginner", "val": "beginner"},
                {"opt": "Intermediate", "val": "intermediate"},
                {"opt": "Advanced", "val": "advanced"}
            ]},
            {"text": "Time availability per week", "type": "radio", "options": [
                {"opt": "1-2 hours", "val": "1-2hr"},
                {"opt": "2-4 hours", "val": "2-4hr"},
                {"opt": "5+ hours", "val": "5+hr"}
            ]},
            {"text": "Tech preference", "type": "radio", "options": [
                {"opt": "Python", "val": "python"},
                {"opt": "JavaScript/TypeScript", "val": "javascript"},
                {"opt": "Java", "val": "java"},
                {"opt": "No preference", "val": "no_preference"}
            ]},
            {"text": "Learning style", "type": "radio", "options": [
                {"opt": "Video Tutorials", "val": "videos"},
                {"opt": "Reading Docs/Articles", "val": "docs"},
                {"opt": "Practical/Project-based", "val": "practical"}
            ]}
        ]
        
        for q_data in questions_data:
            new_q = models.Question(question_text=q_data["text"], type=q_data["type"])
            db.add(new_q)
            db.commit()
            db.refresh(new_q)
            for o_data in q_data["options"]:
                new_opt = models.Option(question_id=new_q.id, option_text=o_data["opt"], value=o_data["val"])
                db.add(new_opt)
            db.commit()

    # Update existing micro steps' resource links if they are currently "#" or None
    from roadmap_logic import RESOURCE_LINKS
    existing_micros = db.query(models.MicroStep).filter((models.MicroStep.resource_link == "#") | (models.MicroStep.resource_link == None)).all()
    if existing_micros:
        for ms in existing_micros:
            if ms.title in RESOURCE_LINKS:
                ms.resource_link = RESOURCE_LINKS[ms.title]
        db.commit()

    # Sync and seed quizzes for existing micro steps (migration)
    all_micros = db.query(models.MicroStep).all()
    for ms in all_micros:
        quiz_exists = db.query(models.Quiz).filter(models.Quiz.micro_step_id == ms.id).first() is not None
        if not quiz_exists:
            from roadmap_logic import create_quiz_for_micro_step
            create_quiz_for_micro_step(db, ms.id, ms.title)

    db.close()

from typing import List

@app.get("/questions", response_model=List[schemas.QuestionResponse])
def get_questions(db: Session = Depends(database.get_db)):
    questions = db.query(models.Question).all()
    result = []
    for q in questions:
        options = db.query(models.Option).filter(models.Option.question_id == q.id).all()
        q_dict = {
            "id": q.id,
            "question_text": q.question_text,
            "type": q.type,
            "options": options
        }
        result.append(q_dict)
    return result


import json

@app.post("/questionnaire")
def save_roadmap_questionnaire(
    body: schemas.RoadmapQuestionnaireCreate,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    import logging
    backend_logger = logging.getLogger("backend")
    backend_logger.info(f"Questionnaire received for user_id={current_user.id}: {body.dict()}")
    
    # Check limit of active roadmaps
    active_count = db.query(models.Roadmap).filter(models.Roadmap.user_id == current_user.id, models.Roadmap.is_archived == False).count()
    if active_count >= 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum active roadmap limit reached (20). Please archive or delete an existing roadmap before adding a new one."
        )
        
    try:
        # Check if roadmap generation is currently in progress
        status_rec = db.query(models.RoadmapGenerationStatus).filter(models.RoadmapGenerationStatus.user_id == current_user.id).first()
        if status_rec and status_rec.status == "GENERATING":
            return {"message": "Roadmap is currently generating.", "status": "GENERATING"}

        langs_str = ",".join(body.programming_languages) if body.programming_languages else ""
        
        skill_level = body.current_skill_level
        if not body.programming_languages:
            skill_level = "Beginner"

        # Check for identical questionnaire payload (Idempotency)
        existing_q = db.query(models.RoadmapQuestionnaire).filter(models.RoadmapQuestionnaire.user_id == current_user.id).first()
        is_identical = False
        if existing_q:
            is_identical = (
                existing_q.name == body.name and
                existing_q.college == body.college and
                existing_q.year == body.year and
                existing_q.branch == body.branch and
                existing_q.programming_languages == langs_str and
                existing_q.primary_career_goal == body.primary_career_goal and
                existing_q.current_skill_level == skill_level and
                existing_q.daily_learning_time == body.daily_learning_time and
                existing_q.target_timeline == body.target_timeline
            )

        if is_identical:
            # Check if there is an existing valid active roadmap matching this goal
            existing_roadmap = db.query(models.Roadmap).filter(
                models.Roadmap.user_id == current_user.id,
                models.Roadmap.is_archived == False,
                models.Roadmap.title.like(f"{body.primary_career_goal}%")
            ).first()
            if existing_roadmap:
                current_user.selected_roadmap_id = existing_roadmap.id
                current_user.onboarding_completed = True
                current_user.questionnaire_completed = True
                
                if not status_rec:
                    status_rec = models.RoadmapGenerationStatus(user_id=current_user.id, status="READY")
                    db.add(status_rec)
                else:
                    status_rec.status = "READY"
                    status_rec.error_message = None
                db.commit()
                return {"message": "Identical questionnaire found. Re-selected existing roadmap.", "status": "READY"}
            
        if existing_q:
            existing_q.name = body.name
            existing_q.college = body.college
            existing_q.year = body.year
            existing_q.branch = body.branch
            existing_q.programming_languages = langs_str
            existing_q.primary_career_goal = body.primary_career_goal
            existing_q.current_skill_level = skill_level
            existing_q.daily_learning_time = body.daily_learning_time
            existing_q.target_timeline = body.target_timeline
            new_q = existing_q
        else:
            new_q = models.RoadmapQuestionnaire(
                user_id=current_user.id,
                name=body.name,
                college=body.college,
                year=body.year,
                branch=body.branch,
                programming_languages=langs_str,
                primary_career_goal=body.primary_career_goal,
                current_skill_level=skill_level,
                daily_learning_time=body.daily_learning_time,
                target_timeline=body.target_timeline
            )
            db.add(new_q)
        db.flush()
        
        # Mark onboarding and questionnaire as completed
        current_user.onboarding_completed = True
        current_user.questionnaire_completed = True
        
        # Initialize or reset roadmap status to GENERATING
        if not status_rec:
            status_rec = models.RoadmapGenerationStatus(user_id=current_user.id, status="GENERATING")
            db.add(status_rec)
        else:
            status_rec.status = "GENERATING"
            status_rec.error_message = None
        db.commit()
        backend_logger.info("Questionnaire Saved ✓")

        # Execute roadmap generation in the background
        try:
            backend_logger.info(f"Enqueuing background roadmap generation for user_id={current_user.id}")
            roadmap_ai_service.generateRoadmapBackground(background_tasks, db, current_user.id)
            backend_logger.info(f"Background roadmap generation enqueued. Client redirecting to roadmap dashboard.")
        except Exception as background_err:
            # Fallback update to FAILED if enqueuing fails
            status_rec = db.query(models.RoadmapGenerationStatus).filter(models.RoadmapGenerationStatus.user_id == current_user.id).first()
            if status_rec:
                status_rec.status = "FAILED"
                status_rec.error_message = f"Failed to enqueue task: {str(background_err)}"
                db.commit()
            backend_logger.error(f"Failed to start roadmap generation for user_id={current_user.id}: {str(background_err)}")
            raise HTTPException(status_code=500, detail=f"Failed to start roadmap generation: {str(background_err)}")

        return {"message": "Roadmap questionnaire saved and AI roadmap generation started in background.", "status": "GENERATING"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        backend_logger.error(f"Failed to save questionnaire for user_id={current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save questionnaire: {str(e)}")

@app.get("/questionnaire", response_model=schemas.RoadmapQuestionnaireResponse)
def get_roadmap_questionnaire(
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    q = db.query(models.RoadmapQuestionnaire).filter(models.RoadmapQuestionnaire.user_id == current_user.id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Roadmap questionnaire not found.")
    return q


@app.post("/career-quiz", response_model=schemas.CareerQuizSubmitResponse)
def save_career_quiz(
    body: schemas.CareerQuizSubmit,
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    try:
        # Prevent duplicates
        db.query(models.CareerRecommendationQuiz).filter(models.CareerRecommendationQuiz.user_id == current_user.id).delete()
        
        careers = [
            "Backend Developer", "Frontend Developer", "Full Stack Developer",
            "AI / Machine Learning Engineer", "Data Scientist", "Data Analyst",
            "Cyber Security Engineer", "Cloud Engineer", "DevOps Engineer",
            "Mobile App Developer", "Game Developer", "UI / UX Designer",
            "Software Engineer", "Blockchain Developer", "Embedded Systems Engineer"
        ]
        
        scores = {c: 0 for c in careers}
        
        q1_map = {
            "Problem Solving": ["Backend Developer", "Software Engineer", "AI / Machine Learning Engineer"],
            "Designing Websites": ["Frontend Developer", "UI / UX Designer"],
            "Training AI Models": ["AI / Machine Learning Engineer", "Data Scientist"],
            "Finding Patterns in Data": ["Data Scientist", "Data Analyst"],
            "Building Applications": ["Mobile App Developer", "Full Stack Developer", "Software Engineer"],
            "Networking": ["Cloud Engineer", "Cyber Security Engineer", "DevOps Engineer"],
            "Cyber Security": ["Cyber Security Engineer"],
            "Cloud Infrastructure": ["Cloud Engineer", "DevOps Engineer"],
            "Automating Tasks": ["DevOps Engineer", "Backend Developer"],
            "Game Development": ["Game Developer"],
            "Other": ["Software Engineer"]
        }
        
        q2_map = {
            "Mathematics": ["AI / Machine Learning Engineer", "Data Scientist"],
            "Programming": ["Backend Developer", "Frontend Developer", "Software Engineer", "Mobile App Developer", "Full Stack Developer", "Blockchain Developer", "Embedded Systems Engineer"],
            "Design": ["UI / UX Designer", "Frontend Developer"],
            "Networking": ["Cloud Engineer", "DevOps Engineer", "Cyber Security Engineer"],
            "Data": ["Data Scientist", "Data Analyst"],
            "Cyber Security": ["Cyber Security Engineer"]
        }
        
        q3_map = {
            "Working with Data": ["Data Scientist", "Data Analyst", "AI / Machine Learning Engineer"],
            "Logical Problem Solving": ["Backend Developer", "Software Engineer", "Blockchain Developer", "Embedded Systems Engineer"],
            "Creativity": ["UI / UX Designer", "Frontend Developer", "Game Developer"],
            "Infrastructure": ["Cloud Engineer", "DevOps Engineer", "Cyber Security Engineer"],
            "Working with People": ["UI / UX Designer", "Software Engineer"],
            "Research": ["AI / Machine Learning Engineer", "Data Scientist"]
        }
        
        # Calculate
        for act in body.activities:
            if act in q1_map:
                for c in q1_map[act]:
                    scores[c] += 3
                    
        if body.subject in q2_map:
            for c in q2_map[body.subject]:
                scores[c] += 3
                
        if body.work_type in q3_map:
            for c in q3_map[body.work_type]:
                scores[c] += 3
                
        max_score = max(scores.values())
        
        # Scale proportionally so top gets 94% like the example
        recommendations = []
        for c, score in scores.items():
            if score > 0:
                scale_factor = 94.0 / max_score if max_score > 0 else 0
                pct = min(100, max(0, int(score * scale_factor)))
                recommendations.append({"career": c, "score_percentage": pct})
            else:
                recommendations.append({"career": c, "score_percentage": 0})
                
        # Sort and take top 3
        recommendations = sorted(recommendations, key=lambda x: x["score_percentage"], reverse=True)[:3]
        
        # Default fallback
        if not recommendations or max_score == 0:
            recommendations = [
                {"career": "Software Engineer", "score_percentage": 94},
                {"career": "Backend Developer", "score_percentage": 88},
                {"career": "Frontend Developer", "score_percentage": 75}
            ]
            
        rec_json = json.dumps(recommendations)
        acts_str = ",".join(body.activities)
        
        new_quiz = models.CareerRecommendationQuiz(
            user_id=current_user.id,
            activities=acts_str,
            subject=body.subject,
            work_type=body.work_type,
            recommended_careers=rec_json
        )
        db.add(new_quiz)
        db.commit()
        
        return {"recommendations": [schemas.RecommendedCareerScore(**r) for r in recommendations]}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process career quiz: {str(e)}")

@app.get("/career-quiz", response_model=schemas.CareerQuizResponse)
def get_career_quiz(
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    q = db.query(models.CareerRecommendationQuiz).filter(models.CareerRecommendationQuiz.user_id == current_user.id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Career recommendation quiz response not found.")
    return q


@app.post("/placement-profile")
def save_placement_profile(
    body: schemas.PlacementProfileCreate,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    try:
        # Prevent duplicates
        db.query(models.PlacementProfile).filter(models.PlacementProfile.user_id == current_user.id).delete()
        
        companies_str = ",".join(body.target_companies) if body.target_companies else ""
        
        new_profile = models.PlacementProfile(
            user_id=current_user.id,
            name=body.name,
            college=body.college,
            year=body.year,
            branch=body.branch,
            aptitude_level=body.aptitude_level,
            dsa_level=body.dsa_level,
            target_companies=companies_str,
            timeline=body.timeline
        )
        db.add(new_profile)
        
        current_user.onboarding_completed = True
        
        # Initialize or reset roadmap status to GENERATING
        status_rec = db.query(models.RoadmapGenerationStatus).filter(models.RoadmapGenerationStatus.user_id == current_user.id).first()
        if not status_rec:
            status_rec = models.RoadmapGenerationStatus(user_id=current_user.id, status="GENERATING")
            db.add(status_rec)
        else:
            status_rec.status = "GENERATING"
            status_rec.error_message = None
            
        db.commit()
        
        # Trigger background generation of placement roadmap
        roadmap_ai_service.generatePlacementRoadmapBackground(background_tasks, db, current_user.id)
        
        return {"message": "Placement profile saved and AI placement roadmap generation started.", "status": "GENERATING"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save placement profile: {str(e)}")

@app.get("/placement-profile", response_model=schemas.PlacementProfileResponse)
def get_placement_profile(
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    p = db.query(models.PlacementProfile).filter(models.PlacementProfile.user_id == current_user.id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Placement profile not found.")
    return p


@app.get("/placement-roadmap", response_model=schemas.RoadmapResponse)
def get_placement_roadmap(
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    roadmap = db.query(models.Roadmap).filter(
        models.Roadmap.user_id == current_user.id,
        models.Roadmap.type == "placement"
    ).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Placement roadmap not found")
        
    loaded = roadmap_ai_service.loadRoadmap(db, current_user.id, roadmap_id=roadmap.id)
    if not loaded:
        raise HTTPException(status_code=404, detail="Placement roadmap details not found")
    return loaded[0]


@app.get("/placement-roadmap/progress", response_model=List[schemas.ProgressResponse])
def get_placement_progress(
    roadmap_id: int,
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    # Verify ownership of this roadmap
    roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == roadmap_id).first()
    if not roadmap or roadmap.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
        
    # Get topics for this roadmap
    phases = db.query(models.RoadmapPhase).filter(models.RoadmapPhase.roadmap_id == roadmap_id).all()
    phase_ids = [p.id for p in phases]
    topics = db.query(models.RoadmapTopic).filter(models.RoadmapTopic.phase_id.in_(phase_ids)).all() if phase_ids else []
    topic_ids = [t.id for t in topics]
    
    if not topic_ids:
        return []
        
    prog = db.query(models.Progress).filter(
        models.Progress.user_id == current_user.id,
        models.Progress.micro_step_id.in_(topic_ids),
        models.Progress.is_completed == True
    ).all()
    return prog


@app.get("/placement-roadmap/progress/score", response_model=schemas.ScoreResponse)
def get_placement_score(
    roadmap_id: int,
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    # Verify ownership
    roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == roadmap_id).first()
    if not roadmap or roadmap.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
        
    score = calculate_user_total_score(db, current_user.id, roadmap_id)
    return {"score": score}


@app.post("/placement-roadmap/progress/complete")
def mark_placement_progress_complete(
    progress_data: schemas.ProgressComplete, 
    current_user: models.User = Depends(read_users_me), 
    db: Session = Depends(database.get_db)
):
    topic = db.query(models.RoadmapTopic).filter(models.RoadmapTopic.id == progress_data.micro_step_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    # Ownership validation
    phase = db.query(models.RoadmapPhase).filter(models.RoadmapPhase.id == topic.phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Topic phase not found")
    roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == phase.roadmap_id).first()
    if not roadmap or roadmap.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: you do not own this roadmap")

    # Complete the RoadmapTopic
    topic.completed = True
    
    # Save to Progress table
    existing_prog = db.query(models.Progress).filter(
        models.Progress.user_id == current_user.id,
        models.Progress.micro_step_id == topic.id
    ).first()
    if not existing_prog:
        new_prog = models.Progress(
            user_id=current_user.id, 
            micro_step_id=topic.id,
            is_completed=True,
            completed_at=datetime.datetime.utcnow()
        )
        db.add(new_prog)
    db.commit()
    return {"message": "Placement step marked as completed"}



@app.post("/answers")
def submit_answers(
    answers_data: schemas.AnswerListCreate, 
    current_user: models.User = Depends(read_users_me), 
    db: Session = Depends(database.get_db)
):
    print(f"DEBUG: Incoming request from {current_user.username}")
    print(f"DEBUG: Received answers body: {answers_data.dict()}")
    try:
        # Optional: Delete existing answers to allow multiple submissions or re-takes
        db.query(models.Answer).filter(models.Answer.user_id == current_user.id).delete()
        
        for ans in answers_data.answers:
            new_answer = models.Answer(
                user_id=current_user.id,
                question_id=ans.question_id,
                selected_option=ans.selected_option
            )
            db.add(new_answer)
        
        current_user.questionnaire_completed = True
        db.commit()
        print("DEBUG: Answers committed to database successfully")
        return {"message": "Answers submitted successfully"}
    except Exception as e:
        print(f"ERROR in /answers: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error while saving answers")

import roadmap_ai_service

@app.post("/generate-roadmap")
@app.post("/roadmap/generate")
def generate_roadmap(
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    if not os.getenv("GROQ_API_KEY"):
        status_rec = db.query(models.RoadmapGenerationStatus).filter(models.RoadmapGenerationStatus.user_id == current_user.id).first()
        if not status_rec:
            status_rec = models.RoadmapGenerationStatus(user_id=current_user.id, status="FAILED", error_message="Missing Groq API Key")
            db.add(status_rec)
        else:
            status_rec.status = "FAILED"
            status_rec.error_message = "Missing Groq API Key"
        db.commit()
        raise HTTPException(status_code=400, detail="Missing Groq API Key")

    # Verify questionnaire exists
    questionnaire = db.query(models.RoadmapQuestionnaire).filter(models.RoadmapQuestionnaire.user_id == current_user.id).first()
    if not questionnaire:
        raise HTTPException(
            status_code=400,
            detail="Roadmap questionnaire not found. Please complete the questionnaire first."
        )

    # Verify active roadmap count < 10
    active_count = db.query(models.Roadmap).filter(
        models.Roadmap.user_id == current_user.id,
        models.Roadmap.is_archived == False
    ).count()
    if active_count >= 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum active roadmap limit reached."
        )
        
    status_rec = db.query(models.RoadmapGenerationStatus).filter(models.RoadmapGenerationStatus.user_id == current_user.id).first()
    if status_rec and status_rec.status == "GENERATING":
        return {"message": "Roadmap is currently generating.", "status": "GENERATING"}

    if not status_rec:
        status_rec = models.RoadmapGenerationStatus(user_id=current_user.id, status="GENERATING")
        db.add(status_rec)
    else:
        status_rec.status = "GENERATING"
        status_rec.error_message = None
    db.commit()

    try:
        roadmap_ai_service.generateRoadmapBackground(background_tasks, db, current_user.id)
        return {"message": "Roadmap generation started in background.", "status": "GENERATING"}
    except Exception as e:
        status_rec = db.query(models.RoadmapGenerationStatus).filter(models.RoadmapGenerationStatus.user_id == current_user.id).first()
        if status_rec:
            status_rec.status = "FAILED"
            status_rec.error_message = str(e)
            db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/roadmap/suggestions", response_model=schemas.SuggestionsResponse)
def get_suggestions(current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    suggestions = analyze_user_progress(db, current_user.id)
    return {"suggestions": suggestions}

@app.get("/roadmap", response_model=List[schemas.RoadmapResponse])
def get_roadmap(current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    return roadmap_ai_service.loadRoadmap(db, current_user.id)

@app.get("/roadmap/{id}", response_model=schemas.RoadmapResponse)
def get_roadmap_by_id(id: int, current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    # Verify ownership
    roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    if roadmap.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: you do not own this roadmap")
        
    loaded = roadmap_ai_service.loadRoadmap(db, current_user.id, roadmap_id=id)
    if not loaded:
        raise HTTPException(status_code=404, detail="Roadmap details not found")
    return loaded[0]

@app.get("/roadmaps/list", response_model=List[schemas.RoadmapListResponse])
def get_roadmaps_list(
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    roadmaps = db.query(models.Roadmap).filter(models.Roadmap.user_id == current_user.id).all()
    res = []
    for r in roadmaps:
        # Calculate progress
        pct, _ = get_user_progress_stats(db, current_user.id, r.id)
        res.append({
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "progress": pct,
            "created_date": r.created_at,
            "updated_date": r.created_at,
            "archived_status": r.is_archived or False,
            "selected_status": r.id == current_user.selected_roadmap_id,
            "roadmap_type": r.type
        })
    return res

@app.post("/roadmap/select/{roadmap_id}")
def select_roadmap_by_id(
    roadmap_id: int,
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    if roadmap.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: you do not own this roadmap")
        
    current_user.selected_roadmap_id = roadmap.id
    db.commit()
    
    backend_logger.info(f"Roadmap Selected: {roadmap_id}")
    backend_logger.info(f"Roadmap Switched: {roadmap_id}")
    return {"message": "Active roadmap updated successfully", "selected_roadmap_id": roadmap.id}

@app.put("/roadmap/rename/{roadmap_id}")
def rename_roadmap_put(
    roadmap_id: int,
    payload: schemas.RenameRoadmapRequest,
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    if roadmap.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: you do not own this roadmap")
        
    new_title = payload.title.strip()
    if not new_title:
        raise HTTPException(status_code=400, detail="Roadmap title cannot be empty")
        
    roadmap.title = new_title
    db.commit()
    
    backend_logger.info(f"Roadmap Renamed: {roadmap_id}")
    return {"message": "Roadmap renamed successfully", "title": roadmap.title}

@app.post("/roadmap/archive/{roadmap_id}")
def archive_roadmap_post(
    roadmap_id: int,
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    if roadmap.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: you do not own this roadmap")
        
    roadmap.is_archived = not roadmap.is_archived
    db.commit()
    
    backend_logger.info(f"Roadmap Archived: {roadmap_id}")
    return {"message": "Roadmap archive status updated successfully", "is_archived": roadmap.is_archived}

@app.delete("/roadmap/delete/{roadmap_id}")
def delete_roadmap_endpoint(
    roadmap_id: int,
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    if roadmap.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: you do not own this roadmap")
        
    try:
        # Delete only this roadmap's related details
        phases = db.query(models.RoadmapPhase).filter(models.RoadmapPhase.roadmap_id == roadmap.id).all()
        phase_ids = [p.id for p in phases]
        topics = db.query(models.RoadmapTopic).filter(models.RoadmapTopic.phase_id.in_(phase_ids)).all() if phase_ids else []
        topic_ids = [t.id for t in topics]
        
        if topic_ids:
            # Delete quizzes and quiz questions
            quizzes = db.query(models.Quiz).filter(models.Quiz.micro_step_id.in_(topic_ids)).all()
            quiz_ids = [q.id for q in quizzes]
            if quiz_ids:
                db.query(models.QuizQuestion).filter(models.QuizQuestion.quiz_id.in_(quiz_ids)).delete(synchronize_session=False)
            db.query(models.Quiz).filter(models.Quiz.micro_step_id.in_(topic_ids)).delete(synchronize_session=False)
            
            # Delete progress and quiz attempts
            db.query(models.Progress).filter(models.Progress.micro_step_id.in_(topic_ids)).delete(synchronize_session=False)
            db.query(models.QuizAttempt).filter(models.QuizAttempt.micro_step_id.in_(topic_ids)).delete(synchronize_session=False)
            
            # Delete topics
            db.query(models.RoadmapTopic).filter(models.RoadmapTopic.phase_id.in_(phase_ids)).delete(synchronize_session=False)
            
        # Delete phases
        db.query(models.RoadmapPhase).filter(models.RoadmapPhase.roadmap_id == roadmap.id).delete(synchronize_session=False)
        
        # Delete the roadmap
        db.delete(roadmap)
        
        # If the deleted roadmap was selected
        if current_user.selected_roadmap_id == roadmap_id:
            current_user.selected_roadmap_id = None
            
            # Automatically switch to another active roadmap if one exists
            remaining = db.query(models.Roadmap).filter(
                models.Roadmap.user_id == current_user.id,
                models.Roadmap.id != roadmap_id,
                models.Roadmap.is_archived == False
            ).order_by(models.Roadmap.id.desc()).first()
            if remaining:
                current_user.selected_roadmap_id = remaining.id
        
        db.commit()
        
        backend_logger.info(f"Roadmap Deleted: {roadmap_id}")
        return {"message": "Roadmap deleted successfully", "selected_roadmap_id": current_user.selected_roadmap_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete roadmap: {str(e)}")




def calculate_user_quiz_bonus(db: Session, user_id: int, roadmap_id: Optional[int] = None) -> int:
    # Get user's best attempt score per micro step/topic of a specific roadmap
    if roadmap_id:
        phases = db.query(models.RoadmapPhase).filter(models.RoadmapPhase.roadmap_id == roadmap_id).all()
        phase_ids = [p.id for p in phases]
        topics = db.query(models.RoadmapTopic).filter(models.RoadmapTopic.phase_id.in_(phase_ids)).all() if phase_ids else []
        topic_ids = [t.id for t in topics]
        
        if not topic_ids:
            macros = db.query(models.MacroStep).filter(models.MacroStep.roadmap_id == roadmap_id).all()
            macro_ids = [m.id for m in macros]
            micros = db.query(models.MicroStep).filter(models.MicroStep.macro_step_id.in_(macro_ids)).all() if macro_ids else []
            topic_ids = [m.id for m in micros]
            
        if not topic_ids:
            return 0
            
        best_attempts = db.query(
            models.QuizAttempt.micro_step_id,
            func.max(models.QuizAttempt.score).label("max_score")
        ).filter(
            models.QuizAttempt.user_id == user_id,
            models.QuizAttempt.micro_step_id.in_(topic_ids)
        ).group_by(models.QuizAttempt.micro_step_id).all()
    else:
        best_attempts = db.query(
            models.QuizAttempt.micro_step_id,
            func.max(models.QuizAttempt.score).label("max_score")
        ).filter(models.QuizAttempt.user_id == user_id).group_by(models.QuizAttempt.micro_step_id).all()
    
    bonus = 0
    for ba in best_attempts:
        if ba.max_score == 5:
            bonus += 10
        elif ba.max_score >= 3:
            bonus += 5
    return bonus

def calculate_user_total_score(db: Session, user_id: int, roadmap_id: Optional[int] = None) -> int:
    if not roadmap_id:
        user_record = db.query(models.User).filter(models.User.id == user_id).first()
        roadmap_id = user_record.selected_roadmap_id if user_record else None
        
    if not roadmap_id:
        first_rm = db.query(models.Roadmap).filter(models.Roadmap.user_id == user_id).first()
        roadmap_id = first_rm.id if first_rm else None

    if not roadmap_id:
        return 0

    # Scoped to the specific roadmap_id
    completed_topics = db.query(models.RoadmapTopic).join(models.RoadmapPhase).filter(
        models.RoadmapPhase.roadmap_id == roadmap_id,
        models.RoadmapTopic.completed == True
    ).all()
    
    roadmap_score = len(completed_topics) * 10
    
    # Check old progress entries just in case
    phases = db.query(models.RoadmapPhase).filter(models.RoadmapPhase.roadmap_id == roadmap_id).all()
    phase_ids = [p.id for p in phases]
    topics = db.query(models.RoadmapTopic).filter(models.RoadmapTopic.phase_id.in_(phase_ids)).all() if phase_ids else []
    topic_ids = [t.id for t in topics]
    
    if not topic_ids:
        macros = db.query(models.MacroStep).filter(models.MacroStep.roadmap_id == roadmap_id).all()
        macro_ids = [m.id for m in macros]
        micros = db.query(models.MicroStep).filter(models.MicroStep.macro_step_id.in_(macro_ids)).all() if macro_ids else []
        topic_ids = [m.id for m in micros]
        if topic_ids:
            prog = db.query(models.Progress).filter(
                models.Progress.user_id == user_id,
                models.Progress.micro_step_id.in_(topic_ids),
                models.Progress.is_completed == True
            ).all()
            old_completed_ids = [p.micro_step_id for p in prog]
            if old_completed_ids:
                old_score = db.query(func.sum(models.MicroStep.weight)).filter(
                    models.MicroStep.id.in_(old_completed_ids)
                ).scalar() or 0
                roadmap_score += old_score
        
    quiz_bonus = calculate_user_quiz_bonus(db, user_id, roadmap_id)
    return roadmap_score + quiz_bonus

@app.post("/progress/complete")
def mark_progress_complete(
    progress_data: schemas.ProgressComplete, 
    current_user: models.User = Depends(read_users_me), 
    db: Session = Depends(database.get_db)
):
    topic = db.query(models.RoadmapTopic).filter(models.RoadmapTopic.id == progress_data.micro_step_id).first()
    if not topic:
        # Fallback to old MicroStep just in case
        target_micro = db.query(models.MicroStep).filter(models.MicroStep.id == progress_data.micro_step_id).first()
        if not target_micro:
            raise HTTPException(status_code=404, detail="Topic or Step not found")
        
        # Ownership validation
        macro = db.query(models.MacroStep).filter(models.MacroStep.id == target_micro.macro_step_id).first()
        if not macro:
            raise HTTPException(status_code=404, detail="Macro step not found")
        roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == macro.roadmap_id).first()
        if not roadmap or roadmap.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied: you do not own this roadmap")

        # Enforce passing the quiz first
        passed_quiz = db.query(models.QuizAttempt).filter(
            models.QuizAttempt.user_id == current_user.id,
            models.QuizAttempt.micro_step_id == progress_data.micro_step_id,
            models.QuizAttempt.score >= 3
        ).first() is not None
        
        if not passed_quiz:
            raise HTTPException(
                status_code=400,
                detail="You must pass the quiz for this step (minimum 60% score) before marking it complete."
            )
            
        existing = db.query(models.Progress).filter(
            models.Progress.user_id == current_user.id,
            models.Progress.micro_step_id == target_micro.id
        ).first()
        if existing:
            existing.is_completed = True
        else:
            new_prog = models.Progress(
                user_id=current_user.id, 
                micro_step_id=target_micro.id,
                is_completed=True,
                completed_at=datetime.datetime.utcnow()
            )
            db.add(new_prog)
        db.commit()
        return {"message": "Step marked as completed"}

    # Ownership validation
    phase = db.query(models.RoadmapPhase).filter(models.RoadmapPhase.id == topic.phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Topic phase not found")
    roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == phase.roadmap_id).first()
    if not roadmap or roadmap.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: you do not own this roadmap")

    # Complete the new RoadmapTopic
    topic.completed = True
    
    # Also save to Progress table for backwards-compatibility (leaderboard stats/etc)
    existing_prog = db.query(models.Progress).filter(
        models.Progress.user_id == current_user.id,
        models.Progress.micro_step_id == topic.id
    ).first()
    if not existing_prog:
        new_prog = models.Progress(
            user_id=current_user.id, 
            micro_step_id=topic.id,
            is_completed=True,
            completed_at=datetime.datetime.utcnow()
        )
        db.add(new_prog)
    db.commit()
    return {"message": "Step marked as completed"}

@app.get("/progress", response_model=List[schemas.ProgressResponse])
def get_progress(current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    selected_id = current_user.selected_roadmap_id
    if not selected_id:
        return []
        
    # Get topics for the selected roadmap
    phases = db.query(models.RoadmapPhase).filter(models.RoadmapPhase.roadmap_id == selected_id).all()
    phase_ids = [p.id for p in phases]
    topics = db.query(models.RoadmapTopic).filter(models.RoadmapTopic.phase_id.in_(phase_ids)).all() if phase_ids else []
    topic_ids = [t.id for t in topics]
    
    if not topic_ids:
        macros = db.query(models.MacroStep).filter(models.MacroStep.roadmap_id == selected_id).all()
        macro_ids = [m.id for m in macros]
        micros = db.query(models.MicroStep).filter(models.MicroStep.macro_step_id.in_(macro_ids)).all() if macro_ids else []
        topic_ids = [m.id for m in micros]
        
    if not topic_ids:
        return []
        
    prog = db.query(models.Progress).filter(
        models.Progress.user_id == current_user.id,
        models.Progress.micro_step_id.in_(topic_ids),
        models.Progress.is_completed == True
    ).all()
    return prog

@app.get("/progress/score", response_model=schemas.ScoreResponse)
def get_score(current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    score = calculate_user_total_score(db, current_user.id, current_user.selected_roadmap_id)
    return {"score": score}

def analyze_user_progress(db: Session, user_id: int):
    prog = db.query(models.Progress).filter(models.Progress.user_id == user_id, models.Progress.is_completed == True).all()
    suggestions = []
    
    if not prog:
        suggestions.append("Start your journey")
    elif len(prog) < 3:
        suggestions.append("Keep going, you're just starting out!")
    else:
        suggestions.append("Great progress!")
        
    return suggestions


def get_leaderboard_data(db: Session, roadmap_type: str = None):
    users = db.query(models.User).all()
    
    leaderboard = []
    for u in users:
        # Determine user role/track
        ans = db.query(models.Answer).join(models.Question, models.Answer.question_id == models.Question.id).filter(
            models.Question.question_text == "Preferred role",
            models.Answer.user_id == u.id
        ).first()
        role = ans.selected_option if ans else "backend"
        if not ans:
            q = db.query(models.RoadmapQuestionnaire).filter(models.RoadmapQuestionnaire.user_id == u.id).first()
            if q:
                goal = q.primary_career_goal.lower()
                if "backend" in goal:
                    role = "backend"
                elif "frontend" in goal:
                    role = "frontend"
                elif "ai" in goal or "machine" in goal or "data" in goal:
                    role = "ai"
                    
        # Check roadmap type filter
        if roadmap_type and role != roadmap_type:
            continue
            
        pct, total_score = get_user_progress_stats(db, u.id)
            
        leaderboard.append({
            "username": u.username,
            "score": total_score,
            "progress_percentage": pct
        })
        
    # Sort
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    
    ranked_leaderboard = []
    current_rank = 1
    previous_score = None
    for i, item in enumerate(leaderboard):
        if previous_score is not None and item["score"] < previous_score:
            current_rank = i + 1
        previous_score = item["score"]
        ranked_leaderboard.append({
            "rank": current_rank,
            "username": item["username"],
            "score": item["score"],
            "progress_percentage": item["progress_percentage"]
        })
        
    return ranked_leaderboard


@app.get("/leaderboard/global", response_model=List[schemas.LeaderboardUser])
def get_global_leaderboard(db: Session = Depends(database.get_db)):
    return get_leaderboard_data(db)

@app.get("/leaderboard/roadmap/{type}", response_model=List[schemas.LeaderboardUser])
def get_roadmap_leaderboard(type: str, db: Session = Depends(database.get_db)):
    return get_leaderboard_data(db, roadmap_type=type)

@app.post("/friends/request")
def send_friend_request(req: schemas.FriendRequest, current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    receiver = None
    if req.receiver_id:
        receiver = db.query(models.User).filter(models.User.id == req.receiver_id).first()
    elif req.username:
        receiver = db.query(models.User).filter(models.User.username == req.username).first()
        
    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")
    if receiver.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send request to self")
        
    existing = db.query(models.Friend).filter(
        ((models.Friend.sender_id == current_user.id) & (models.Friend.receiver_id == receiver.id)) |
        ((models.Friend.sender_id == receiver.id) & (models.Friend.receiver_id == current_user.id))
    ).first()
    
    if existing:
        if existing.status == "accepted":
            raise HTTPException(status_code=400, detail="Already friends")
        elif existing.status == "pending":
            raise HTTPException(status_code=400, detail="Request already pending")
            
    new_req = models.Friend(sender_id=current_user.id, receiver_id=receiver.id, status="pending")
    db.add(new_req)
    db.commit()
    return {"message": "Friend request sent"}

@app.post("/friends/respond")
def respond_friend_request(resp: schemas.FriendRespond, current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    friend_req = db.query(models.Friend).filter(models.Friend.id == resp.request_id, models.Friend.receiver_id == current_user.id).first()
    if not friend_req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if resp.action not in ["accept", "reject"]:
        raise HTTPException(status_code=400, detail="Invalid action")
        
    if resp.action == "accept":
        friend_req.status = "accepted"
    else:
        friend_req.status = "rejected"
        
    db.commit()
    return {"message": f"Request {resp.action}ed"}

@app.get("/friends", response_model=List[schemas.FriendResponse])
def get_friends(current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    friends = db.query(models.Friend).filter(
        ((models.Friend.sender_id == current_user.id) | (models.Friend.receiver_id == current_user.id)),
        models.Friend.status == "accepted"
    ).all()
    
    res = []
    for f in friends:
        friend_id = f.receiver_id if f.sender_id == current_user.id else f.sender_id
        friend_user = db.query(models.User).filter(models.User.id == friend_id).first()
        if friend_user:
            res.append({"id": f.id, "username": friend_user.username, "status": f.status})
        
    return res

@app.get("/friends/requests", response_model=List[schemas.FriendResponse])
def get_friend_requests(current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    requests = db.query(models.Friend).filter(
        models.Friend.receiver_id == current_user.id,
        models.Friend.status == "pending"
    ).all()
    
    res = []
    for r in requests:
        sender_user = db.query(models.User).filter(models.User.id == r.sender_id).first()
        if sender_user:
            res.append({"id": r.id, "username": sender_user.username, "status": r.status})
        
    return res

@app.get("/friends/progress", response_model=List[schemas.FriendProgress])
def get_friends_progress(current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    friends = db.query(models.Friend).filter(
        ((models.Friend.sender_id == current_user.id) | (models.Friend.receiver_id == current_user.id)),
        models.Friend.status == "accepted"
    ).all()
    
    friend_ids = [f.receiver_id if f.sender_id == current_user.id else f.sender_id for f in friends]
    
    if not friend_ids:
        return []
    
    res = []
    for fid in friend_ids:
        user = db.query(models.User).filter(models.User.id == fid).first()
        if user:
            ans = db.query(models.Answer).join(models.Question, models.Answer.question_id == models.Question.id).filter(
                models.Question.question_text == "Preferred role",
                models.Answer.user_id == fid
            ).first()
            roadmap_type = ans.selected_option if ans else "backend"
            if not ans:
                q = db.query(models.RoadmapQuestionnaire).filter(models.RoadmapQuestionnaire.user_id == fid).first()
                if q:
                    goal = q.primary_career_goal.lower()
                    if "backend" in goal:
                        roadmap_type = "backend"
                    elif "frontend" in goal:
                        roadmap_type = "frontend"
                    elif "ai" in goal or "machine" in goal or "data" in goal:
                        roadmap_type = "ai"
            
            pct, score_val = get_user_progress_stats(db, fid)
            
            res.append({
                "username": user.username,
                "roadmap_type": roadmap_type,
                "progress_percentage": pct,
                "score": score_val
            })
        
    return res

def get_user_progress_stats(db: Session, user_id: int, roadmap_id: Optional[int] = None):
    # Check if this user has any AI roadmaps first!
    if not roadmap_id:
        user_record = db.query(models.User).filter(models.User.id == user_id).first()
        roadmap_id = user_record.selected_roadmap_id if user_record else None
        
    if not roadmap_id:
        first_rm = db.query(models.Roadmap).filter(models.Roadmap.user_id == user_id).first()
        roadmap_id = first_rm.id if first_rm else None

    if not roadmap_id:
        return 0.0, 0

    roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == roadmap_id).first()
    if not roadmap:
        return 0.0, 0

    if roadmap.generated_by_ai:
        total_topics = db.query(models.RoadmapTopic).join(models.RoadmapPhase).filter(models.RoadmapPhase.roadmap_id == roadmap_id).count()
        completed_topics = db.query(models.RoadmapTopic).join(models.RoadmapPhase).filter(
            models.RoadmapPhase.roadmap_id == roadmap_id,
            models.RoadmapTopic.completed == True
        ).count()
        
        pct = 0.0
        if total_topics > 0:
            pct = round((completed_topics / total_topics) * 100, 2)
            
        score_val = calculate_user_total_score(db, user_id, roadmap_id)
        return pct, score_val
    else:
        roadmap_score = db.query(func.sum(models.MicroStep.weight)).select_from(models.Progress).join(
            models.MicroStep, models.Progress.micro_step_id == models.MicroStep.id
        ).filter(models.Progress.user_id == user_id, models.Progress.is_completed == True).scalar() or 0
        max_score_val = db.query(func.sum(models.MicroStep.weight)).select_from(models.Roadmap).join(
            models.MacroStep, models.Roadmap.id == models.MacroStep.roadmap_id
        ).join(
            models.MicroStep, models.MacroStep.id == models.MicroStep.macro_step_id
        ).filter(models.Roadmap.user_id == user_id).scalar() or 0
        quiz_bonus = calculate_user_quiz_bonus(db, user_id, roadmap_id)
        score_val = roadmap_score + quiz_bonus
        
        pct = 0.0
        if max_score_val > 0:
            pct = round((roadmap_score / max_score_val) * 100, 2)
        return pct, score_val

@app.post("/groups/create", response_model=schemas.GroupResponseNew)
def create_group(group: schemas.GroupCreateNew, current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    default_roadmap_type = "backend"
    owner_roadmap = db.query(models.Roadmap).filter(models.Roadmap.user_id == current_user.id).first()
    if owner_roadmap:
        default_roadmap_type = owner_roadmap.type

    new_group = models.Group(
        group_name=group.group_name,
        description=group.description,
        owner_id=current_user.id,
        # backward compatibility
        name=group.group_name,
        created_by=current_user.id,
        roadmap_type=default_roadmap_type
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    
    new_member = models.GroupMember(group_id=new_group.id, user_id=current_user.id)
    db.add(new_member)
    db.commit()
    
    return new_group

@app.post("/groups/join/{group_id}")
def join_group(group_id: int, current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
        
    existing = db.query(models.GroupMember).filter(models.GroupMember.group_id == group_id, models.GroupMember.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already a member")
        
    new_member = models.GroupMember(group_id=group_id, user_id=current_user.id)
    db.add(new_member)
    db.commit()
    return {"message": "Successfully joined group"}

@app.post("/groups/join")
def join_group_old(req: schemas.GroupJoin, current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    return join_group(req.group_id, current_user, db)

@app.post("/groups/leave/{group_id}")
def leave_group(group_id: int, current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
        
    membership = db.query(models.GroupMember).filter(models.GroupMember.group_id == group_id, models.GroupMember.user_id == current_user.id).first()
    if not membership:
        raise HTTPException(status_code=400, detail="Not a member of this group")
        
    db.delete(membership)
    db.commit()
    return {"message": "Successfully left group"}

@app.get("/groups")
def get_groups(current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    groups = db.query(models.Group).all()
    res = []
    for g in groups:
        member_count = db.query(models.GroupMember).filter(models.GroupMember.group_id == g.id).count()
        members = db.query(models.GroupMember).filter(models.GroupMember.group_id == g.id).all()
        avg_progress = 0.0
        if members:
            total_progress = 0.0
            for m in members:
                prog_pct, _ = get_user_progress_stats(db, m.user_id)
                total_progress += prog_pct
            avg_progress = round(total_progress / len(members), 2)

        is_member = db.query(models.GroupMember).filter(
            models.GroupMember.group_id == g.id,
            models.GroupMember.user_id == current_user.id
        ).first() is not None

        res.append({
            "id": g.id,
            "group_name": g.group_name or g.name,
            "description": g.description or "",
            "owner_id": g.owner_id or g.created_by,
            "created_at": g.created_at,
            "member_count": member_count,
            "average_progress": avg_progress,
            "is_member": is_member
        })
    return res

@app.get("/groups/{group_id}", response_model=schemas.GroupDetailsResponse)
def get_group_details(group_id: int, current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
        
    owner = db.query(models.User).filter(models.User.id == (group.owner_id or group.created_by)).first()
    owner_username = owner.username if owner else "Unknown"
    
    members = db.query(models.GroupMember).filter(models.GroupMember.group_id == group_id).all()
    member_count = len(members)
    
    avg_progress = 0.0
    most_active_member = "None"
    highest_score = -1
    
    if members:
        total_progress = 0.0
        for m in members:
            pct, score_val = get_user_progress_stats(db, m.user_id)
            total_progress += pct
            if score_val > highest_score:
                highest_score = score_val
                member_user = db.query(models.User).filter(models.User.id == m.user_id).first()
                if member_user:
                    most_active_member = f"{member_user.username} ({score_val} pts)"
        avg_progress = round(total_progress / member_count, 2)
        
    # Group Roadmap features
    shared_roadmap_title = None
    shared_roadmap_completion = None
    current_stage = None
    next_stage = None
    
    if members:
        shared_type = None
        all_same = True
        roadmap_ids = []
        for m in members:
            user_rec = db.query(models.User).filter(models.User.id == m.user_id).first()
            if user_rec and user_rec.selected_roadmap_id:
                rm = db.query(models.Roadmap).filter(models.Roadmap.id == user_rec.selected_roadmap_id).first()
                if rm:
                    rm_type = rm.type.split(":")[-1].strip().lower()
                    if shared_type is None:
                        shared_type = rm_type
                        shared_roadmap_title = rm.title.replace("Deep-Learning:", "").replace("Fast-Track:", "").strip() + " Journey"
                    elif shared_type != rm_type:
                        all_same = False
                        break
                    roadmap_ids.append(rm.id)
                else:
                    all_same = False
                    break
            else:
                all_same = False
                break
                
        if all_same and shared_type and roadmap_ids:
            shared_roadmap_completion = avg_progress
            rep_roadmap_id = roadmap_ids[0]
            rep_macros = db.query(models.MacroStep).filter(models.MacroStep.roadmap_id == rep_roadmap_id).order_by(models.MacroStep.order_index).all()
            
            sequence_steps = []
            for macro in rep_macros:
                micros = db.query(models.MicroStep).filter(models.MicroStep.macro_step_id == macro.id).all()
                for micro in micros:
                    sequence_steps.append(micro)
                    
            if sequence_steps:
                group_current_step = None
                group_next_step = None
                
                for idx, step in enumerate(sequence_steps):
                    completed_count = 0
                    for m in members:
                        has_completed = db.query(models.Progress).join(
                            models.MicroStep, models.Progress.micro_step_id == models.MicroStep.id
                        ).filter(
                            models.Progress.user_id == m.user_id,
                            models.MicroStep.title == step.title,
                            models.Progress.is_completed == True
                        ).first() is not None
                        if has_completed:
                            completed_count += 1
                            
                    if completed_count < len(members):
                        group_current_step = step
                        if idx + 1 < len(sequence_steps):
                            group_next_step = sequence_steps[idx + 1]
                        break
                
                if group_current_step:
                    current_stage = group_current_step.title
                    next_stage = group_next_step.title if group_next_step else "Goal Reached!"
                else:
                    current_stage = "All complete!"
                    next_stage = "Trophy unlocked!"

    return {
        "id": group.id,
        "group_name": group.group_name or group.name,
        "description": group.description or "",
        "owner_id": group.owner_id or group.created_by,
        "owner_username": owner_username,
        "created_at": group.created_at,
        "member_count": member_count,
        "average_progress": avg_progress,
        "most_active_member": most_active_member,
        "shared_roadmap_title": shared_roadmap_title,
        "shared_roadmap_completion": shared_roadmap_completion,
        "current_stage": current_stage,
        "next_stage": next_stage
    }

@app.get("/groups/{group_id}/members", response_model=List[schemas.GroupMemberProgressNew])
def get_group_members(group_id: int, current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
        
    members = db.query(models.GroupMember).filter(models.GroupMember.group_id == group_id).all()
    res = []
    for m in members:
        user = db.query(models.User).filter(models.User.id == m.user_id).first()
        if user:
            pct, score_val = get_user_progress_stats(db, m.user_id)
            res.append({
                "user_id": user.id,
                "username": user.username,
                "progress": pct,
                "score": score_val
            })
    res.sort(key=lambda x: x["score"], reverse=True)
    return res

@app.delete("/groups/{group_id}/member/{user_id}")
def remove_group_member(group_id: int, user_id: int, current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
        
    group_owner_id = group.owner_id or group.created_by
    if group_owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the group owner can remove members")
        
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="The owner cannot remove themselves")
        
    membership = db.query(models.GroupMember).filter(
        models.GroupMember.group_id == group_id,
        models.GroupMember.user_id == user_id
    ).first()
    if not membership:
        raise HTTPException(status_code=404, detail="User is not a member of this group")
        
    db.delete(membership)
    db.commit()
    return {"message": "Member successfully removed from group"}

@app.get("/groups/{group_id}/progress", response_model=List[schemas.GroupProgress])
def get_group_progress(group_id: int, current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    members = db.query(models.GroupMember).filter(models.GroupMember.group_id == group_id).all()
    res = []
    for m in members:
        user = db.query(models.User).filter(models.User.id == m.user_id).first()
        if user:
            pct, score_val = get_user_progress_stats(db, m.user_id)
            res.append({
                "username": user.username,
                "progress_percentage": pct,
                "score": score_val
            })
    res.sort(key=lambda x: x["score"], reverse=True)
    return res

@app.get("/quiz/{micro_step_id}", response_model=schemas.QuizResponse)
def get_quiz(
    micro_step_id: int,
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    # Verify ownership of micro_step_id
    topic = db.query(models.RoadmapTopic).filter(models.RoadmapTopic.id == micro_step_id).first()
    if topic:
        phase = db.query(models.RoadmapPhase).filter(models.RoadmapPhase.id == topic.phase_id).first()
        if not phase:
            raise HTTPException(status_code=404, detail="Topic phase not found")
        roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == phase.roadmap_id).first()
        if not roadmap or roadmap.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied: you do not own this roadmap")
    else:
        micro_step = db.query(models.MicroStep).filter(models.MicroStep.id == micro_step_id).first()
        if micro_step:
            macro = db.query(models.MacroStep).filter(models.MacroStep.id == micro_step.macro_step_id).first()
            if not macro:
                raise HTTPException(status_code=404, detail="Macro step not found")
            roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == macro.roadmap_id).first()
            if not roadmap or roadmap.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied: you do not own this roadmap")
        else:
            raise HTTPException(status_code=404, detail="Step not found")

    import random
    # Find the Quiz row for this micro_step_id
    quiz = db.query(models.Quiz).filter(models.Quiz.micro_step_id == micro_step_id).first()
    if not quiz:
        # Fallback: check if the ID belongs to a RoadmapTopic (new AI roadmaps) or a MicroStep (old roadmaps)
        roadmap_topic = db.query(models.RoadmapTopic).filter(models.RoadmapTopic.id == micro_step_id).first()
        if roadmap_topic:
            from roadmap_logic import create_quiz_for_micro_step
            create_quiz_for_micro_step(db, micro_step_id, roadmap_topic.topic_title)
            quiz = db.query(models.Quiz).filter(models.Quiz.micro_step_id == micro_step_id).first()
        else:
            micro_step = db.query(models.MicroStep).filter(models.MicroStep.id == micro_step_id).first()
            if not micro_step:
                raise HTTPException(status_code=404, detail="Topic or Step not found")
            from roadmap_logic import create_quiz_for_micro_step
            create_quiz_for_micro_step(db, micro_step_id, micro_step.title)
            quiz = db.query(models.Quiz).filter(models.Quiz.micro_step_id == micro_step_id).first()
            
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found and could not be created")

    # Query all Questions for this quiz_id
    pool = db.query(models.QuizQuestion).filter(models.QuizQuestion.quiz_id == quiz.id).all()
    if not pool:
        raise HTTPException(status_code=404, detail="No questions found for this quiz topic")

    # Get user's last attempt for this micro_step_id to prevent repeats
    last_attempt = db.query(models.QuizAttempt).filter(
        models.QuizAttempt.user_id == current_user.id,
        models.QuizAttempt.micro_step_id == micro_step_id
    ).order_by(models.QuizAttempt.attempted_at.desc()).first()

    last_question_ids = []
    if last_attempt and last_attempt.question_ids:
        last_question_ids = [int(qid) for qid in last_attempt.question_ids.split(",") if qid.strip().isdigit()]

    # Filter into unused vs used questions
    unused_questions = [q for q in pool if q.id not in last_question_ids]
    used_questions = [q for q in pool if q.id in last_question_ids]

    # Select 5 questions
    selected = []
    if len(unused_questions) >= 5:
        selected = random.sample(unused_questions, 5)
    else:
        selected = list(unused_questions)
        needed = 5 - len(selected)
        if len(used_questions) >= needed:
            selected += random.sample(used_questions, needed)
        else:
            selected += used_questions

    # Shuffle the option letters for each question
    questions_response = []
    for q in selected:
        options = [
            {"key": "option_a", "text": q.option_a},
            {"key": "option_b", "text": q.option_b},
            {"key": "option_c", "text": q.option_c},
            {"key": "option_d", "text": q.option_d}
        ]
        random.shuffle(options)
        questions_response.append({
            "id": q.id,
            "question_text": q.question_text,
            "options": options
        })

    return {"topic_name": quiz.topic_name, "questions": questions_response}

@app.post("/quiz/submit", response_model=schemas.QuizSubmissionResponse)
def submit_quiz(
    payload: schemas.QuizSubmission,
    current_user: models.User = Depends(read_users_me),
    db: Session = Depends(database.get_db)
):
    micro_step_id = payload.micro_step_id
    # Verify ownership of micro_step_id
    topic = db.query(models.RoadmapTopic).filter(models.RoadmapTopic.id == micro_step_id).first()
    if topic:
        phase = db.query(models.RoadmapPhase).filter(models.RoadmapPhase.id == topic.phase_id).first()
        if not phase:
            raise HTTPException(status_code=404, detail="Topic phase not found")
        roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == phase.roadmap_id).first()
        if not roadmap or roadmap.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied: you do not own this roadmap")
    else:
        micro_step = db.query(models.MicroStep).filter(models.MicroStep.id == micro_step_id).first()
        if micro_step:
            macro = db.query(models.MacroStep).filter(models.MacroStep.id == micro_step.macro_step_id).first()
            if not macro:
                raise HTTPException(status_code=404, detail="Macro step not found")
            roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == macro.roadmap_id).first()
            if not roadmap or roadmap.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied: you do not own this roadmap")
        else:
            raise HTTPException(status_code=404, detail="Step not found")

    answers = payload.answers

    # Find the quiz
    quiz = db.query(models.Quiz).filter(models.Quiz.micro_step_id == micro_step_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    correct_count = 0
    served_ids = []
    results_breakdown = []
    
    # Verify each answer
    for ans in answers:
        question = db.query(models.QuizQuestion).filter(
            models.QuizQuestion.id == ans.question_id,
            models.QuizQuestion.quiz_id == quiz.id
        ).first()
        if not question:
            raise HTTPException(status_code=400, detail=f"Question {ans.question_id} not found in this quiz")
        
        served_ids.append(str(question.id))
        is_correct = (ans.selected_option == question.correct_answer)
        if is_correct:
            correct_count += 1
            
        results_breakdown.append({
            "question_id": question.id,
            "selected_option": ans.selected_option,
            "correct_answer": question.correct_answer,
            "is_correct": is_correct
        })

    served_str = ",".join(served_ids)

    # Save attempt
    new_attempt = models.QuizAttempt(
        user_id=current_user.id,
        micro_step_id=micro_step_id,
        score=correct_count,
        question_ids=served_str
    )
    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)

    passed = correct_count >= 3 # 60% of 5 questions is 3 or more

    return {
        "score": correct_count,
        "passed": passed,
        "results": results_breakdown
    }

from fastapi.staticfiles import StaticFiles
import os

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

