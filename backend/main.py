from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text, func
import models, schemas, auth, database
from database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PathForge API")

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
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

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
        "selected_roadmap_id": current_user.selected_roadmap_id
    }

@app.on_event("startup")
def seed_database():
    db = database.SessionLocal()
    # Run self-healing sqlite migrations
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
        db.execute(text("ALTER TABLE roadmaps ADD COLUMN is_archived BOOLEAN DEFAULT 0"))
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

import roadmap_logic

@app.post("/generate-roadmap")
def generate_roadmap(current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    print(f"DEBUG: Generating roadmap for {current_user.username}")
    try:
        # Trigger roadmap generation based on user answers
        roadmap_logic.generate_roadmaps_for_user(db, current_user.id)
        print("DEBUG: Roadmap generated successfully")
        return {"message": "Roadmaps generated successfully."}
    except Exception as e:
        print(f"ERROR in /generate-roadmap: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error while generating roadmap")

@app.get("/roadmap", response_model=List[schemas.RoadmapResponse])
def get_roadmap(current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    roadmaps = db.query(models.Roadmap).filter(models.Roadmap.user_id == current_user.id).all()
    result = []
    
    for r in roadmaps:
        r_dict = {
            "id": r.id,
            "title": r.title,
            "type": r.type,
            "macro_steps": []
        }
        
        macros = db.query(models.MacroStep).filter(models.MacroStep.roadmap_id == r.id).order_by(models.MacroStep.order_index).all()
        for macro in macros:
            m_dict = {
                "id": macro.id,
                "title": macro.title,
                "order_index": macro.order_index,
                "micro_steps": []
            }
            
            micros = db.query(models.MicroStep).filter(models.MicroStep.macro_step_id == macro.id).all()
            for micro in micros:
                passed_quiz = db.query(models.QuizAttempt).filter(
                    models.QuizAttempt.user_id == current_user.id,
                    models.QuizAttempt.micro_step_id == micro.id,
                    models.QuizAttempt.score >= 3
                ).first() is not None
                
                m_dict["micro_steps"].append({
                    "id": micro.id,
                    "title": micro.title,
                    "description": micro.description,
                    "difficulty": micro.difficulty,
                    "weight": micro.weight,
                    "resource_link": micro.resource_link,
                    "quiz_passed": passed_quiz
                })
            
            r_dict["macro_steps"].append(m_dict)
            
        result.append(r_dict)
    
    return result

def calculate_user_quiz_bonus(db: Session, user_id: int) -> int:
    # Get user's best attempt score per micro step
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

def calculate_user_total_score(db: Session, user_id: int) -> int:
    prog = db.query(models.Progress).filter(
        models.Progress.user_id == user_id,
        models.Progress.is_completed == True
    ).all()
    completed_ids = [p.micro_step_id for p in prog]
    
    roadmap_score = 0
    if completed_ids:
        roadmap_score = db.query(func.sum(models.MicroStep.weight)).filter(
            models.MicroStep.id.in_(completed_ids)
        ).scalar() or 0
        
    quiz_bonus = calculate_user_quiz_bonus(db, user_id)
    return roadmap_score + quiz_bonus

@app.post("/progress/complete")
def mark_progress_complete(
    progress_data: schemas.ProgressComplete, 
    current_user: models.User = Depends(read_users_me), 
    db: Session = Depends(database.get_db)
):
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
        models.Progress.micro_step_id == progress_data.micro_step_id
    ).first()
    
    if existing:
        if existing.is_completed:
            return {"message": "Already completed"}
        else:
            existing.is_completed = True
            db.commit()
            return {"message": "Step marked as completed"}
            
    target_micro = db.query(models.MicroStep).filter(models.MicroStep.id == progress_data.micro_step_id).first()
    if not target_micro:
        raise HTTPException(status_code=404, detail="Micro step not found")
            
    new_prog = models.Progress(
        user_id=current_user.id, 
        micro_step_id=target_micro.id,
        is_completed=True
    )
    db.add(new_prog)
    db.commit()
    return {"message": "Step marked as completed"}

@app.get("/progress", response_model=List[schemas.ProgressResponse])
def get_progress(current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    prog = db.query(models.Progress).filter(
        models.Progress.user_id == current_user.id,
        models.Progress.is_completed == True
    ).all()
    return prog

@app.get("/progress/score", response_model=schemas.ScoreResponse)
def get_score(current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    score = calculate_user_total_score(db, current_user.id)
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

@app.get("/roadmap/suggestions", response_model=schemas.SuggestionsResponse)
def get_suggestions(current_user: models.User = Depends(read_users_me), db: Session = Depends(database.get_db)):
    suggestions = analyze_user_progress(db, current_user.id)
    return {"suggestions": suggestions}


def get_leaderboard_data(db: Session, roadmap_type: str = None):
    users = db.query(models.User).all()
    
    leaderboard = []
    for u in users:
        # Check roadmap type filter
        if roadmap_type:
            ans = db.query(models.Answer).join(models.Question, models.Answer.question_id == models.Question.id).filter(
                models.Question.question_text == "Preferred role",
                models.Answer.user_id == u.id
            ).first()
            role = ans.selected_option if ans else "backend"
            if role != roadmap_type:
                continue
                
        # Calculate progress score
        prog = db.query(models.Progress).filter(
            models.Progress.user_id == u.id,
            models.Progress.is_completed == True
        ).all()
        completed_ids = [p.micro_step_id for p in prog]
        
        roadmap_score = 0
        if completed_ids:
            roadmap_score = db.query(func.sum(models.MicroStep.weight)).filter(
                models.MicroStep.id.in_(completed_ids)
            ).scalar() or 0
            
        # Calculate max score
        max_score_val = db.query(func.sum(models.MicroStep.weight)).select_from(models.Roadmap).join(
            models.MacroStep, models.Roadmap.id == models.MacroStep.roadmap_id
        ).join(
            models.MicroStep, models.MacroStep.id == models.MicroStep.macro_step_id
        ).filter(models.Roadmap.user_id == u.id).scalar() or 0
        
        quiz_bonus = calculate_user_quiz_bonus(db, u.id)
        total_score = roadmap_score + quiz_bonus
        
        pct = 0.0
        if max_score_val > 0:
            pct = round((roadmap_score / max_score_val) * 100, 2)
            
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
            
            roadmap_score = db.query(func.sum(models.MicroStep.weight)).select_from(models.Progress).join(
                models.MicroStep, models.Progress.micro_step_id == models.MicroStep.id
            ).filter(models.Progress.user_id == fid, models.Progress.is_completed == True).scalar() or 0
            max_score_val = db.query(func.sum(models.MicroStep.weight)).select_from(models.Roadmap).join(
                models.MacroStep, models.Roadmap.id == models.MacroStep.roadmap_id
            ).join(
                models.MicroStep, models.MacroStep.id == models.MicroStep.macro_step_id
            ).filter(models.Roadmap.user_id == fid).scalar() or 0
            quiz_bonus = calculate_user_quiz_bonus(db, fid)
            score_val = roadmap_score + quiz_bonus
            
            pct = 0.0
            if max_score_val > 0:
                pct = round((roadmap_score / max_score_val) * 100, 2)
                
            res.append({
                "username": user.username,
                "roadmap_type": roadmap_type,
                "progress_percentage": pct,
                "score": score_val
            })
        
    return res

def get_user_progress_stats(db: Session, user_id: int):
    roadmap_score = db.query(func.sum(models.MicroStep.weight)).select_from(models.Progress).join(
        models.MicroStep, models.Progress.micro_step_id == models.MicroStep.id
    ).filter(models.Progress.user_id == user_id, models.Progress.is_completed == True).scalar() or 0
    max_score_val = db.query(func.sum(models.MicroStep.weight)).select_from(models.Roadmap).join(
        models.MacroStep, models.Roadmap.id == models.MacroStep.roadmap_id
    ).join(
        models.MicroStep, models.MacroStep.id == models.MicroStep.macro_step_id
    ).filter(models.Roadmap.user_id == user_id).scalar() or 0
    quiz_bonus = calculate_user_quiz_bonus(db, user_id)
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
    import random
    # Find the Quiz row for this micro_step_id
    quiz = db.query(models.Quiz).filter(models.Quiz.micro_step_id == micro_step_id).first()
    if not quiz:
        # Fallback: check if the micro step exists, and if so, create the quiz dynamically
        micro_step = db.query(models.MicroStep).filter(models.MicroStep.id == micro_step_id).first()
        if not micro_step:
            raise HTTPException(status_code=404, detail="Micro step not found")
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

