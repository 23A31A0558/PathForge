from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    selected_roadmap_id = Column(Integer, nullable=True)
    questionnaire_completed = Column(Boolean, default=False)


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, index=True)
    type = Column(String) # radio or select

class Option(Base):
    __tablename__ = "options"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, index=True)
    option_text = Column(String)
    value = Column(String)

class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    question_id = Column(Integer, index=True)
    selected_option = Column(String)

class Roadmap(Base):
    __tablename__ = "roadmaps"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String)
    type = Column(String) # fast_track or deep_learning
    is_archived = Column(Boolean, default=False)


class MacroStep(Base):
    __tablename__ = "macro_steps"
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, index=True)
    title = Column(String)
    order_index = Column(Integer)

class MicroStep(Base):
    __tablename__ = "micro_steps"
    id = Column(Integer, primary_key=True, index=True)
    macro_step_id = Column(Integer, index=True)
    title = Column(String)
    description = Column(String)
    difficulty = Column(String) # easy, medium, hard
    weight = Column(Integer)
    resource_link = Column(String, nullable=True)

from sqlalchemy import DateTime
import datetime

class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    micro_step_id = Column(Integer, index=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    from sqlalchemy import UniqueConstraint
    __table_args__ = (UniqueConstraint('user_id', 'micro_step_id', name='uq_user_micro_step'),)
class Friend(Base):
    __tablename__ = "friends"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, index=True)
    receiver_id = Column(Integer, index=True)
    status = Column(String, default="pending") # pending, accepted, rejected
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String, index=True, nullable=True)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Compatibility columns
    name = Column(String, index=True, nullable=True)
    created_by = Column(Integer, index=True, nullable=True)
    roadmap_type = Column(String, nullable=True)

class GroupMember(Base):
    __tablename__ = "group_members"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)

class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    micro_step_id = Column(Integer, index=True)
    topic_name = Column(String)

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, index=True)
    question_text = Column(String)
    option_a = Column(String)
    option_b = Column(String)
    option_c = Column(String)
    option_d = Column(String)
    correct_answer = Column(String) # Stores "option_a", "option_b", "option_c", or "option_d"

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    micro_step_id = Column(Integer, index=True)
    score = Column(Integer)
    question_ids = Column(String, nullable=True) # comma separated list of question IDs served
    attempted_at = Column(DateTime, default=datetime.datetime.utcnow)

