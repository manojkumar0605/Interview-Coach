import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import engine, Base, SessionLocal, run_migrations
from app.models import User, Resume, Session as InterviewSession, Question, Answer, Evaluation, GrammarEvaluation
from app.agents.grammar_coach import evaluate_grammar
from app.agents.answer_evaluator import evaluate_answer
from app.agents.weak_topic_tracker import update_user_topic_scores, get_recurring_grammar_issues
from app.agents.feedback_planner import generate_study_plan

async def test_grammar_coach_pipeline():
    print("=== 1. Creating Grammar Evaluation Tables & Migrations ===")
    Base.metadata.create_all(bind=engine)
    run_migrations()
    db = SessionLocal()

    print("=== 2. Testing Grammar Coach Agent directly ===")
    sample_answer = "Um, like, basically I used PostgreSQL for storing data and you know, we had a lot of race conditions so I kind of added Redis locks."
    grammar_result = await evaluate_grammar(sample_answer)
    print(f"Grammar Evaluation Result: {grammar_result}")

    print("=== 3. Testing Concurrent Execution (asyncio.gather) ===")
    eval_res, grammar_res = await asyncio.gather(
        evaluate_answer(
            question_text="How do you handle concurrency in PostgreSQL?",
            user_response=sample_answer,
            topic_tag="Concurrency"
        ),
        evaluate_grammar(answer_text=sample_answer)
    )

    print(f"Content Score: {eval_res.get('score')} / 10")
    print(f"Grammar Score: {grammar_res.get('grammar_score')} / 10")
    print(f"Filler Words Count: {grammar_res.get('filler_word_count')}")
    print(f"Corrected Version: {grammar_res.get('corrected_version')}")

    print("\n=== 4. Testing Grammar Tracker Aggregation ===")
    user = db.query(User).first()
    if user:
        update_user_topic_scores(db, user.id)
        grammar_insights = get_recurring_grammar_issues(db, user.id)
        print(f"Grammar Insights: {grammar_insights}")

    print("\nGRAMMAR COACH PIPELINE TEST COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test_grammar_coach_pipeline())
