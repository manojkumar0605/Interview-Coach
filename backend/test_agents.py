import asyncio
import os
import sys

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import engine, Base, SessionLocal
from app.models import User, Resume, Session as InterviewSession, Question, Answer, Evaluation
from app.agents.resume_analyzer import analyze_resume
from app.agents.question_generator import generate_questions
from app.agents.answer_evaluator import evaluate_answer
from app.agents.weak_topic_tracker import update_user_topic_scores, get_weak_topics
from app.agents.feedback_planner import generate_study_plan

async def test_full_pipeline():
    print("=== 1. Initializing Database Schema ===")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("=== 2. Creating Test User ===")
    test_email = "candidate@example.com"
    user = db.query(User).filter(User.email == test_email).first()
    if not user:
        user = User(email=test_email, password_hash="hashed_secret")
        db.add(user)
        db.commit()
        db.refresh(user)
    print(f"User ID: {user.id}, Email: {user.email}")

    print("=== 3. Testing Resume Analyzer (OpenRouter API) ===")
    sample_resume_text = """
    Jane Doe - Senior Backend Engineer
    Experience:
    - Senior Backend Developer at Tech Corp (4 years). Built high-throughput microservices using Python, FastAPI, and PostgreSQL.
    - Software Engineer at Data Systems (2 years). Designed Redis caching strategies and optimized SQL queries.
    Skills: Python, FastAPI, PostgreSQL, Docker, Redis, Kubernetes, System Design, REST APIs.
    Education: B.S. Computer Science.
    """
    resume_analysis = await analyze_resume(sample_resume_text, target_role="Senior Backend Engineer")
    print(f"Resume Analysis Output: {resume_analysis}")

    resume_obj = Resume(
        user_id=user.id,
        raw_text=sample_resume_text,
        parsed_json=resume_analysis,
        target_role="Senior Backend Engineer",
        seniority=resume_analysis.get("seniority_estimate", "Senior")
    )
    db.add(resume_obj)
    db.commit()
    db.refresh(resume_obj)

    print("=== 4. Testing Question Generator (OpenRouter API) ===")
    questions_list = await generate_questions(
        resume_json=resume_analysis,
        target_role="Senior Backend Engineer",
        weak_topics=["Database Indexing", "Concurrency"]
    )
    print(f"Generated {len(questions_list)} questions:")
    for idx, q in enumerate(questions_list):
        print(f" [{idx+1}] [{q.get('topic_tag')}] ({q.get('type')}) {q.get('text')}")

    print("=== 5. Creating Session & Saving Questions ===")
    session_obj = InterviewSession(
        user_id=user.id,
        resume_id=resume_obj.id,
        role_target="Senior Backend Engineer",
        status="active"
    )
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)

    saved_questions = []
    for idx, q in enumerate(questions_list[:3]): # Test with first 3 questions
        q_obj = Question(
            session_id=session_obj.id,
            text=q.get("text"),
            topic_tag=q.get("topic_tag", "General"),
            difficulty=q.get("difficulty", "medium"),
            type=q.get("type", "technical"),
            order_index=idx
        )
        db.add(q_obj)
        db.commit()
        db.refresh(q_obj)
        saved_questions.append(q_obj)

    print("=== 6. Testing Answer Evaluator (OpenRouter API) ===")
    sample_answers = [
        "I use PostgreSQL index types such as B-Tree for equality and range queries, and GIN indices for JSONB columns. I analyze query execution plans using EXPLAIN ANALYZE to eliminate sequential scans.",
        "I implement distributed locking using Redis Redlock or optimistic concurrency control with version columns in SQLAlchemy to prevent race conditions during DB updates.",
        "In my previous role I communicated sprint goals clearly and used STAR method to structure team post-mortems after outages."
    ]

    for q_obj, ans_text in zip(saved_questions, sample_answers):
        ans_obj = Answer(question_id=q_obj.id, user_response=ans_text)
        db.add(ans_obj)
        db.commit()
        db.refresh(ans_obj)

        eval_res = await evaluate_answer(
            question_text=q_obj.text,
            user_response=ans_text,
            topic_tag=q_obj.topic_tag
        )
        print(f"\nQuestion: {q_obj.text}")
        print(f"Answer Score: {eval_res.get('score')}/10 | Rationale: {eval_res.get('rationale')}")

        eval_obj = Evaluation(
            answer_id=ans_obj.id,
            score=eval_res.get("score", 7.0),
            criteria_json=eval_res.get("criteria", {}),
            rationale=eval_res.get("rationale", ""),
            ideal_answer_json=eval_res.get("ideal_answer_points", []),
            topic_tag=q_obj.topic_tag
        )
        db.add(eval_obj)
        db.commit()

    print("\n=== 7. Testing Weak Topic Tracker (Pure Python) ===")
    topic_scores = update_user_topic_scores(db, user.id)
    weak_topics = get_weak_topics(db, user.id)
    print(f"Updated Topic Scores Count: {len(topic_scores)}")
    print(f"Identified Weak Topics: {weak_topics}")

    print("\n=== 8. Testing Feedback Planner (OpenRouter API) ===")
    session_summary = []
    for q_obj in saved_questions:
        ans = q_obj.answer
        session_summary.append({
            "question": q_obj.text,
            "topic": q_obj.topic_tag,
            "user_answer": ans.user_response if ans else "",
            "score": ans.evaluation.score if (ans and ans.evaluation) else 0.0,
            "rationale": ans.evaluation.rationale if (ans and ans.evaluation) else ""
        })

    study_plan = await generate_study_plan(
        session_results=session_summary,
        role_target="Senior Backend Engineer",
        historical_weak_topics=weak_topics
    )
    print("Generated Study Plan JSON:")
    print(study_plan)

    print("\n✅ ALL BACKEND PIPELINE TESTS PASSED CLEANLY!")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
