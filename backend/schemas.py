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
    selected_roadmap_id: Optional[int] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


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
    quiz_passed: bool = False

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
    type: str # fast_track or deep_learning
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
    selected_roadmap_id: Optional[int] = None

class SelectRoadmapRequest(BaseModel):
    roadmap_id: int


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




