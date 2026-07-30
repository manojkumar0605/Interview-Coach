from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

class UserSignup(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str

class RecommendedRoleSchema(BaseModel):
    title: str
    match_score: int
    reasoning: str
    matching_skills: List[str]
    skill_gaps: List[str]
    seniority_fit: str

class JobMatchSchema(BaseModel):
    recommended_roles: List[RecommendedRoleSchema]
    summary: str

class ResumeUploadResponse(BaseModel):
    id: int
    user_id: int
    target_role: str
    seniority: Optional[str] = None
    parsed_json: Dict[str, Any]
    uploaded_at: datetime
    job_matches: Optional[JobMatchSchema] = None

class SessionStartRequest(BaseModel):
    resume_id: int
    role_target: str

class QuestionSchema(BaseModel):
    id: int
    session_id: int
    text: str
    topic_tag: str
    difficulty: str
    type: str
    order_index: int

    class Config:
        from_attributes = True

class SessionStartResponse(BaseModel):
    session_id: int
    role_target: str
    questions: List[QuestionSchema]

class AnswerSubmitRequest(BaseModel):
    user_response: str

class EvaluationSchema(BaseModel):
    score: float
    criteria_json: Dict[str, Any]
    rationale: str
    ideal_answer_json: List[str]
    topic_tag: str

class GrammarEvaluationSchema(BaseModel):
    grammar_score: float
    issues: List[Dict[str, Any]]
    filler_word_count: int
    tone: str
    corrected_version: str

class AnswerSubmitResponse(BaseModel):
    answer_id: int
    question_id: int
    evaluation: EvaluationSchema
    grammar_evaluation: Optional[GrammarEvaluationSchema] = None
    follow_up_question: Optional[QuestionSchema] = None
    next_question: Optional[QuestionSchema] = None
    is_session_complete: bool = False

class SessionCompleteResponse(BaseModel):
    session_id: int
    status: str
    study_plan: Dict[str, Any]
    weak_topics: List[str]

class TopicScoreSchema(BaseModel):
    topic_tag: str
    rolling_avg_score: float
    grammar_rolling_avg: float = 0.0
    sessions_count: int
    last_updated: datetime

class ProgressResponse(BaseModel):
    topic_scores: List[TopicScoreSchema]
    weak_topics: List[str]
    grammar_overall_avg: float = 0.0
    common_grammar_issues: List[Dict[str, Any]] = []
    latest_job_matches: Optional[JobMatchSchema] = None
