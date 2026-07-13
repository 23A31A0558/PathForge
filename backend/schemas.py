from pydantic import BaseModel
from typing import List, Optional
import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    questionnaire_completed: bool
    onboarding_completed: bool
    selected_roadmap_id: Optional[int] = None
    success: bool = True

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    success: bool = True



class OptionBase(BaseModel):
    id: int
    option_text: str
    value: str

    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    id: int
    question_text: str
    type: str
    options: List[OptionBase] = []

    class Config:
        from_attributes = True

class AnswerCreate(BaseModel):
    question_id: int
    selected_option: str

class AnswerListCreate(BaseModel):
    answers: List[AnswerCreate]


class MicroStepResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    weight: int
    resource_link: Optional[str] = None
    quiz_passed: bool = True
    completed: bool = False
    resources: List[dict] = []
    estimated_hours: int = 0
    mini_project: Optional[str] = None
    quiz_required: bool = False

    class Config:
        from_attributes = True

class MacroStepResponse(BaseModel):
    id: int
    title: str
    order_index: int
    micro_steps: List[MicroStepResponse] = []

    class Config:
        from_attributes = True

class RoadmapResponse(BaseModel):
    id: int
    title: str
    type: str  # fast_track or deep_learning
    description: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    generated_by_ai: bool = True
    is_archived: bool = False
    macro_steps: List[MacroStepResponse] = []

    class Config:
        from_attributes = True

class ProgressComplete(BaseModel):
    micro_step_id: int

class ProgressResponse(BaseModel):
    micro_step_id: int
    is_completed: bool

    class Config:
        from_attributes = True

class SuggestionsResponse(BaseModel):
    suggestions: List[str]
class ScoreResponse(BaseModel):
    score: int

class LeaderboardUser(BaseModel):
    rank: int
    username: str
    score: int
    progress_percentage: float

class FriendRequest(BaseModel):
    receiver_id: Optional[int] = None
    username: Optional[str] = None

class FriendRespond(BaseModel):
    request_id: int
    action: str # "accept" or "reject"

class FriendResponse(BaseModel):
    id: int
    username: str
    status: str

    class Config:
        from_attributes = True

class FriendProgress(BaseModel):
    username: str
    roadmap_type: str
    progress_percentage: float
    score: int

class GroupCreate(BaseModel):
    name: str
    roadmap_type: str

class GroupResponse(BaseModel):
    id: int
    name: str
    created_by: int
    roadmap_type: str

    class Config:
        from_attributes = True

class GroupJoin(BaseModel):
    group_id: int

class GroupMemberResponse(BaseModel):
    id: int
    group_id: int
    user_id: int
    username: str

class GroupProgress(BaseModel):
    username: str
    progress_percentage: float
    score: int

class QuizQuestionOption(BaseModel):
    key: str
    text: str

class QuizQuestionResponse(BaseModel):
    id: int
    question_text: str
    options: List[QuizQuestionOption]

class QuizResponse(BaseModel):
    topic_name: str
    questions: List[QuizQuestionResponse]

class QuizAnswerSubmit(BaseModel):
    question_id: int
    selected_option: str

class QuizSubmission(BaseModel):
    micro_step_id: int
    answers: List[QuizAnswerSubmit]

class QuizSubmissionResponse(BaseModel):
    score: int
    passed: bool
    results: List[dict] = []

class UserStatusResponse(BaseModel):
    questionnaire_completed: bool
    onboarding_completed: bool
    selected_roadmap_id: Optional[int] = None

class SelectRoadmapRequest(BaseModel):
    roadmap_id: int

class RenameRoadmapRequest(BaseModel):
    title: str


class GroupCreateNew(BaseModel):
    group_name: str
    description: str

class GroupResponseNew(BaseModel):
    id: int
    group_name: str
    description: str
    owner_id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class GroupDetailsResponse(BaseModel):
    id: int
    group_name: str
    description: str
    owner_id: int
    owner_username: str
    created_at: datetime.datetime
    member_count: int
    average_progress: float
    most_active_member: str
    shared_roadmap_title: Optional[str] = None
    shared_roadmap_completion: Optional[float] = None
    current_stage: Optional[str] = None
    next_stage: Optional[str] = None

class GroupMemberProgressNew(BaseModel):
    user_id: int
    username: str
    progress: float
    score: int


# Roadmap Questionnaire schemas
class RoadmapQuestionnaireCreate(BaseModel):
    name: str
    college: str
    year: str
    branch: str
    programming_languages: List[str]
    primary_career_goal: str
    current_skill_level: str
    daily_learning_time: str
    target_timeline: str

class RoadmapQuestionnaireResponse(BaseModel):
    id: int
    user_id: int
    name: str
    college: str
    year: str
    branch: str
    programming_languages: str
    primary_career_goal: str
    current_skill_level: str
    daily_learning_time: str
    target_timeline: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# Career Quiz schemas
class CareerQuizSubmit(BaseModel):
    activities: List[str]
    subject: str
    work_type: str

class RecommendedCareerScore(BaseModel):
    career: str
    score_percentage: int

class CareerQuizSubmitResponse(BaseModel):
    recommendations: List[RecommendedCareerScore]

class CareerQuizResponse(BaseModel):
    id: int
    user_id: int
    activities: str
    subject: str
    work_type: str
    recommended_careers: str  # JSON list of RecommendedCareerScore
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# Placement Profile schemas
class PlacementProfileCreate(BaseModel):
    name: str
    college: str
    year: str
    branch: str
    aptitude_level: str
    dsa_level: str
    target_companies: List[str]
    timeline: str

class PlacementProfileResponse(BaseModel):
    id: int
    user_id: int
    name: str
    college: str
    year: str
    branch: str
    aptitude_level: str
    dsa_level: str
    target_companies: str
    timeline: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class RoadmapStatusResponse(BaseModel):
    status: str
    error_message: Optional[str] = None


class RoadmapListResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    progress: float
    created_date: Optional[datetime.datetime] = None
    updated_date: Optional[datetime.datetime] = None
    archived_status: bool
    selected_status: bool
    roadmap_type: str

    class Config:
        from_attributes = True






