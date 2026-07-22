# backend/roadmap_ai_service.py

import os
import json
import datetime
import time
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from database import SessionLocal

import models
from ai.logger import logger
from groq_ai_service import generate_personalized_roadmap, generate_placement_roadmap

def saveRoadmap(db: Session, user_id: int, parsed_data: dict) -> List[models.Roadmap]:
    """
    Saves the generated roadmaps (Fast Track and Deep Learning), phases, and topics.
    Does NOT delete existing roadmaps to support multiple independent journeys.
    """
    saved_roadmaps = []
    try:
        # Save the new roadmaps (Fast Track and Deep Learning)
        for i, rm_schema in enumerate(parsed_data["roadmaps"]):
            # Determine the type: fast_track or deep_learning
            rm_type = "fast_track" if i == 0 else "deep_learning"
            new_rm = models.Roadmap(
                user_id=user_id,
                title=rm_schema["title"],
                description=rm_schema["description"],
                type=rm_type,
                generated_by_ai=True,
                created_at=datetime.datetime.utcnow()
            )
            db.add(new_rm)
            db.flush()
            
            logger.info("Roadmap Created")
            logger.info(f"Roadmap ID: {new_rm.id}")
            
            phase_count = 0
            topic_count = 0

            # Save phases
            for ph_schema in rm_schema["phases"]:
                new_phase = models.RoadmapPhase(
                    roadmap_id=new_rm.id,
                    phase_number=ph_schema["phase_number"],
                    phase_title=ph_schema["phase_title"],
                    estimated_duration=ph_schema["estimated_duration"]
                )
                db.add(new_phase)
                db.flush()
                phase_count += 1

                # Save topics
                for idx, tp_schema in enumerate(ph_schema["topics"]):
                    resources_json = json.dumps(tp_schema["resources"])
                    new_topic = models.RoadmapTopic(
                        phase_id=new_phase.id,
                        topic_title=tp_schema["topic"],
                        difficulty=tp_schema["difficulty"],
                        estimated_hours=tp_schema["estimated_hours"],
                        resources_json=resources_json,
                        mini_project=tp_schema["mini_project"],
                        quiz_required=tp_schema["quiz_required"],
                        completed=False,
                        order_number=idx + 1
                    )
                    db.add(new_topic)
                    topic_count += 1
            
            db.flush()
            logger.info(f"Phase Count: {phase_count}")
            logger.info(f"Topic Count: {topic_count}")
            saved_roadmaps.append(new_rm)
            
        db.commit()
        for rm in saved_roadmaps:
            db.refresh(rm)
            
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save generated roadmap: {str(e)}")
        raise e

    return saved_roadmaps



def generateRoadmapBackground(background_tasks: BackgroundTasks, db: Session, user_id: int):
    """
    Kicks off AI roadmap generation asynchronously using FastAPI's BackgroundTasks.
    Pre-loads user profile synchronously to avoid multi-thread session leakage.
    """
    questionnaire = db.query(models.RoadmapQuestionnaire).filter(models.RoadmapQuestionnaire.user_id == user_id).first()
    if not questionnaire:
        logger.error(f"Cannot generate roadmap: Questionnaire answers missing for user {user_id}")
        return
        
    learning_style = "Practical/Project-based"
    ans = db.query(models.Answer).join(
        models.Question, models.Answer.question_id == models.Question.id
    ).filter(
        models.Question.question_text == "Learning style",
        models.Answer.user_id == user_id
    ).first()
    if ans:
        learning_style = ans.selected_option
        
    # Fetch Career Recommendation Quiz if it exists
    career_quiz = db.query(models.CareerRecommendationQuiz).filter(models.CareerRecommendationQuiz.user_id == user_id).first()
    
    # Fetch Placement Profile if it exists
    placement_profile = db.query(models.PlacementProfile).filter(models.PlacementProfile.user_id == user_id).first()

    profile_data = {
        "career": questionnaire.primary_career_goal,
        "languages": questionnaire.programming_languages,
        "skill": questionnaire.current_skill_level,
        "study_time": questionnaire.daily_learning_time,
        "timeline": questionnaire.target_timeline,
        "learning_style": learning_style,
        "year": questionnaire.year,
        "branch": questionnaire.branch,
        "questionnaire_answers": {
            "name": questionnaire.name,
            "college": questionnaire.college,
            "year": questionnaire.year,
            "branch": questionnaire.branch,
            "languages": questionnaire.programming_languages,
            "career": questionnaire.primary_career_goal,
            "skill": questionnaire.current_skill_level,
            "study_time": questionnaire.daily_learning_time,
            "timeline": questionnaire.target_timeline
        },
        "career_quiz_answers": {
            "activities": career_quiz.activities,
            "subject": career_quiz.subject,
            "work_type": career_quiz.work_type,
            "recommended_careers": career_quiz.recommended_careers
        } if career_quiz else None,
        "placement_answers": {
            "aptitude_level": placement_profile.aptitude_level,
            "dsa_level": placement_profile.dsa_level,
            "target_companies": placement_profile.target_companies,
            "timeline": placement_profile.timeline
        } if placement_profile else None
    }
    
    # Internal function to run in background worker
    def run_generation_pipeline():
        logger.info(f"Background roadmap generation worker started for user {user_id}")
        db_session = SessionLocal()
        try:
            # Re-confirm status is set to GENERATING
            status_rec = db_session.query(models.RoadmapGenerationStatus).filter(models.RoadmapGenerationStatus.user_id == user_id).first()
            if not status_rec:
                status_rec = models.RoadmapGenerationStatus(user_id=user_id, status="GENERATING")
                db_session.add(status_rec)
            else:
                status_rec.status = "GENERATING"
                status_rec.error_message = None
            db_session.commit()
            
            # Execute pipeline
            generated_data = generate_personalized_roadmap(profile_data)
            
            # Save generated roadmap
            save_start = time.time()
            saved_rms = saveRoadmap(db_session, user_id, generated_data)
            logger.info("Roadmap Saved ✓")
            
            # Update user's active selected roadmap to the newly generated one
            user_rec = db_session.query(models.User).filter(models.User.id == user_id).first()
            if user_rec and saved_rms:
                user_rec.selected_roadmap_id = saved_rms[0].id
                db_session.commit()
                
            # Log audit details
            user_rec = db_session.query(models.User).filter(models.User.id == user_id).first()
            selected_rm_id = user_rec.selected_roadmap_id if user_rec else None
            if selected_rm_id:
                phase_count = db_session.query(models.RoadmapPhase).filter(models.RoadmapPhase.roadmap_id == selected_rm_id).count()
                topic_count = db_session.query(models.RoadmapTopic).join(models.RoadmapPhase).filter(models.RoadmapPhase.roadmap_id == selected_rm_id).count()
                completed_count = db_session.query(models.RoadmapTopic).join(models.RoadmapPhase).filter(
                    models.RoadmapPhase.roadmap_id == selected_rm_id,
                    models.RoadmapTopic.completed == True
                ).count()
                progress_pct = (completed_count / topic_count * 100) if topic_count > 0 else 0.0
            else:
                phase_count = 0
                topic_count = 0
                progress_pct = 0.0

            logger.info(f"Phase Count: {phase_count}")
            logger.info(f"Topic Count: {topic_count}")
            logger.info(f"selected_roadmap_id: {selected_rm_id}")
            logger.info(f"Progress %: {progress_pct:.2f}%")
                
            # Set generation status to READY
            status_rec = db_session.query(models.RoadmapGenerationStatus).filter(models.RoadmapGenerationStatus.user_id == user_id).first()
            status_rec.status = "READY"
            db_session.commit()
            logger.info(f"Generation status successfully set to READY for user {user_id}")
            
        except Exception as ex:
            logger.error("Generation Failed")
            logger.error(f"Failed to generate roadmap in background for user {user_id}: {str(ex)}")
            try:
                status_rec = db_session.query(models.RoadmapGenerationStatus).filter(models.RoadmapGenerationStatus.user_id == user_id).first()
                if status_rec:
                    status_rec.status = "FAILED"
                    status_rec.error_message = str(ex)
                    db_session.commit()
            except Exception as rollback_err:
                logger.error(f"Failed to record FAILED status for user {user_id}: {str(rollback_err)}")
        finally:
            db_session.close()
            
    background_tasks.add_task(run_generation_pipeline)


def loadRoadmap(db: Session, user_id: int, roadmap_id: Optional[int] = None) -> List[dict]:
    """
    Queries and builds the compatible Roadmap response structure.
    If roadmap_id is specified, returns that roadmap. Otherwise returns all roadmaps for user.
    """
    query = db.query(models.Roadmap).filter(models.Roadmap.user_id == user_id)
    if roadmap_id:
        query = query.filter(models.Roadmap.id == roadmap_id)
    
    roadmaps = query.all()
    result = []
    
    for r in roadmaps:
        phases = db.query(models.RoadmapPhase).filter(models.RoadmapPhase.roadmap_id == r.id).order_by(models.RoadmapPhase.phase_number).all()
        macro_steps = []
        for p in phases:
            topics = db.query(models.RoadmapTopic).filter(models.RoadmapTopic.phase_id == p.id).order_by(models.RoadmapTopic.order_number).all()
            micro_steps = []
            for t in topics:
                resources = []
                try:
                    if t.resources_json:
                        resources = json.loads(t.resources_json)
                except Exception:
                    pass
                
                resource_link = resources[0]["url"] if resources else "#"
                
                micro_steps.append({
                    "id": t.id,
                    "title": t.topic_title,
                    "description": f"Mini Project: {t.mini_project}" if t.mini_project else "Core concept topic details.",
                    "difficulty": t.difficulty,
                    "weight": 10,
                    "resource_link": resource_link,
                    "quiz_passed": not t.quiz_required or (db.query(models.QuizAttempt).filter(
                        models.QuizAttempt.user_id == user_id,
                        models.QuizAttempt.micro_step_id == t.id,
                        models.QuizAttempt.score >= 3
                    ).first() is not None),
                    "completed": t.completed,
                    "resources": resources,
                    "estimated_hours": t.estimated_hours,
                    "mini_project": t.mini_project,
                    "quiz_required": t.quiz_required
                })
            
            macro_steps.append({
                "id": p.id,
                "title": p.phase_title,
                "order_index": p.phase_number,
                "micro_steps": micro_steps
            })
            
        result.append({
            "id": r.id,
            "title": r.title,
            "type": r.type,
            "description": r.description,
            "created_at": r.created_at,
            "generated_by_ai": r.generated_by_ai or False,
            "is_archived": r.is_archived or False,
            "macro_steps": macro_steps
        })
        
    return result

def savePlacementRoadmap(db: Session, user_id: int, parsed_data: dict) -> List[models.Roadmap]:
    """
    Saves the generated placement roadmap.
    Deletes the old placement roadmap for this user (if exists) before inserting.
    Do NOT delete or modify existing learning roadmaps.
    """
    saved_roadmaps = []
    try:
        # Delete existing placement roadmap and its phases/topics
        existing_pm = db.query(models.Roadmap).filter(
            models.Roadmap.user_id == user_id,
            models.Roadmap.type == "placement"
        ).first()
        if existing_pm:
            phases = db.query(models.RoadmapPhase).filter(models.RoadmapPhase.roadmap_id == existing_pm.id).all()
            for phase in phases:
                db.query(models.RoadmapTopic).filter(models.RoadmapTopic.phase_id == phase.id).delete()
            db.query(models.RoadmapPhase).filter(models.RoadmapPhase.roadmap_id == existing_pm.id).delete()
            db.delete(existing_pm)
            db.flush()

        # Save the new placement roadmap
        rm_schema = parsed_data["roadmaps"][0]
        new_rm = models.Roadmap(
            user_id=user_id,
            title=rm_schema["title"],
            description=rm_schema["description"],
            type="placement",
            generated_by_ai=True,
            created_at=datetime.datetime.utcnow()
        )
        db.add(new_rm)
        db.flush()
        
        logger.info("Placement Roadmap Created")
        logger.info(f"Placement Roadmap ID: {new_rm.id}")
        
        phase_count = 0
        topic_count = 0

        # Save phases
        for ph_schema in rm_schema["phases"]:
            new_phase = models.RoadmapPhase(
                roadmap_id=new_rm.id,
                phase_number=ph_schema["phase_number"],
                phase_title=ph_schema["phase_title"],
                estimated_duration=ph_schema["estimated_duration"]
            )
            db.add(new_phase)
            db.flush()
            phase_count += 1

            # Save topics
            for idx, tp_schema in enumerate(ph_schema["topics"]):
                resources_json = json.dumps(tp_schema["resources"])
                new_topic = models.RoadmapTopic(
                    phase_id=new_phase.id,
                    topic_title=tp_schema["topic"],
                    difficulty=tp_schema["difficulty"],
                    estimated_hours=tp_schema["estimated_hours"],
                    resources_json=resources_json,
                    mini_project=tp_schema["mini_project"],
                    quiz_required=tp_schema["quiz_required"],
                    completed=False,
                    order_number=idx + 1
                )
                db.add(new_topic)
                topic_count += 1
        
        db.flush()
        logger.info(f"Placement Phase Count: {phase_count}")
        logger.info(f"Placement Topic Count: {topic_count}")
        saved_roadmaps.append(new_rm)
        db.commit()
        for rm in saved_roadmaps:
            db.refresh(rm)
            
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save generated placement roadmap: {str(e)}")
        raise e

    return saved_roadmaps


def generatePlacementRoadmapBackground(background_tasks: BackgroundTasks, db: Session, user_id: int):
    """
    Kicks off AI placement roadmap generation asynchronously using FastAPI's BackgroundTasks.
    Pre-loads user profile synchronously to avoid multi-thread session leakage.
    """
    placement_profile = db.query(models.PlacementProfile).filter(models.PlacementProfile.user_id == user_id).first()
    if not placement_profile:
        logger.error(f"Cannot generate placement roadmap: Placement profile answers missing for user {user_id}")
        return

    profile_data = {
        "branch": placement_profile.branch,
        "year": placement_profile.year,
        "questionnaire_answers": {
            "name": placement_profile.name,
            "college": placement_profile.college
        },
        "placement_answers": {
            "aptitude_level": placement_profile.aptitude_level,
            "dsa_level": placement_profile.dsa_level,
            "target_companies": placement_profile.target_companies,
            "timeline": placement_profile.timeline
        }
    }
    
    # Internal function to run in background worker
    def run_generation_pipeline():
        logger.info(f"Background placement roadmap generation worker started for user {user_id}")
        db_session = SessionLocal()
        try:
            # Re-confirm status is set to GENERATING
            status_rec = db_session.query(models.RoadmapGenerationStatus).filter(models.RoadmapGenerationStatus.user_id == user_id).first()
            if not status_rec:
                status_rec = models.RoadmapGenerationStatus(user_id=user_id, status="GENERATING")
                db_session.add(status_rec)
            else:
                status_rec.status = "GENERATING"
                status_rec.error_message = None
            db_session.commit()
            
            # Execute pipeline
            generated_data = generate_placement_roadmap(profile_data)
            
            # Save generated placement roadmap
            savePlacementRoadmap(db_session, user_id, generated_data)
            logger.info("Placement Roadmap Saved ✓")
            
            # Set generation status to READY
            status_rec = db_session.query(models.RoadmapGenerationStatus).filter(models.RoadmapGenerationStatus.user_id == user_id).first()
            status_rec.status = "READY"
            db_session.commit()
            logger.info(f"Placement Generation status successfully set to READY for user {user_id}")
            
        except Exception as ex:
            logger.error("Placement Generation Failed")
            logger.error(f"Failed to generate placement roadmap in background for user {user_id}: {str(ex)}")
            try:
                status_rec = db_session.query(models.RoadmapGenerationStatus).filter(models.RoadmapGenerationStatus.user_id == user_id).first()
                if status_rec:
                    status_rec.status = "FAILED"
                    status_rec.error_message = str(ex)
                    db_session.commit()
            except Exception as rollback_err:
                logger.error(f"Failed to record FAILED status for user {user_id}: {str(rollback_err)}")
        finally:
            db_session.close()
            
    background_tasks.add_task(run_generation_pipeline)

