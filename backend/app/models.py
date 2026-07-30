import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    topic_scores = relationship("TopicScore", back_populates="user", cascade="all, delete-orphan")
    study_plans = relationship("StudyPlan", back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    raw_text = Column(Text, nullable=False)
    parsed_json = Column(JSON, nullable=True)
    target_role = Column(String, nullable=True)
    seniority = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="resumes")
    sessions = relationship("Session", back_populates="resume", cascade="all, delete-orphan")
    job_match = relationship("JobMatch", back_populates="resume", uselist=False, cascade="all, delete-orphan")


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    recommended_roles_json = Column(JSON, nullable=False)
    summary = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)

    resume = relationship("Resume", back_populates="job_match")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    role_target = Column(String, nullable=False)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String, default="active") # active, completed

    user = relationship("User", back_populates="sessions")
    resume = relationship("Resume", back_populates="sessions")
    questions = relationship("Question", back_populates="session", cascade="all, delete-orphan")
    study_plan = relationship("StudyPlan", back_populates="session", uselist=False, cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    text = Column(Text, nullable=False)
    topic_tag = Column(String, nullable=False)
    difficulty = Column(String, default="medium")
    type = Column(String, nullable=False) # behavioral, technical, follow-up
    order_index = Column(Integer, nullable=False)

    session = relationship("Session", back_populates="questions")
    answer = relationship("Answer", back_populates="question", uselist=False, cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_response = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)

    question = relationship("Question", back_populates="answer")
    evaluation = relationship("Evaluation", back_populates="answer", uselist=False, cascade="all, delete-orphan")
    grammar_evaluation = relationship("GrammarEvaluation", back_populates="answer", uselist=False, cascade="all, delete-orphan")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey("answers.id"), nullable=False)
    score = Column(Float, nullable=False)
    criteria_json = Column(JSON, nullable=False) # {clarity, specificity, relevance}
    rationale = Column(Text, nullable=False)
    ideal_answer_json = Column(JSON, nullable=True) # list of points
    topic_tag = Column(String, nullable=False)

    answer = relationship("Answer", back_populates="evaluation")


class GrammarEvaluation(Base):
    __tablename__ = "grammar_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey("answers.id"), nullable=False)
    grammar_score = Column(Float, nullable=False)
    issues_json = Column(JSON, nullable=False)
    filler_word_count = Column(Integer, nullable=False, default=0)
    tone = Column(String, nullable=False, default="professional")
    corrected_version = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    answer = relationship("Answer", back_populates="grammar_evaluation")


class TopicScore(Base):
    __tablename__ = "topic_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_tag = Column(String, nullable=False)
    rolling_avg_score = Column(Float, nullable=False, default=0.0)
    grammar_rolling_avg = Column(Float, nullable=False, default=0.0)
    sessions_count = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="topic_scores")


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)
    plan_json = Column(JSON, nullable=False)

    user = relationship("User", back_populates="study_plans")
    session = relationship("Session", back_populates="study_plan")
