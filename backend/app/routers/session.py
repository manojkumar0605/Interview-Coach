import asyncio
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.database import get_db
from app.deps import get_current_user
from app.models import (
    User, Resume, Session as InterviewSession, Question, Answer,
    Evaluation, GrammarEvaluation, StudyPlan
)
from app.schemas import (
    SessionStartRequest, SessionStartResponse, QuestionSchema,
    AnswerSubmitRequest, AnswerSubmitResponse, EvaluationSchema,
    GrammarEvaluationSchema, SessionCompleteResponse
)
from app.agents.question_generator import generate_questions
from app.agents.answer_evaluator import evaluate_answer
from app.agents.grammar_coach import evaluate_grammar
from app.agents.interview_agent import evaluate_shallowness_and_maybe_followup
from app.agents.weak_topic_tracker import get_weak_topics, update_user_topic_scores, get_recurring_grammar_issues
from app.agents.feedback_planner import generate_study_plan

router = APIRouter(prefix="/session", tags=["Session"])

@router.post("/start", response_model=SessionStartResponse)
async def start_session(
    req: SessionStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify resume belongs to user
    resume = db.query(Resume).filter(Resume.id == req.resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    # Fetch weak topics for user
    weak_topics = get_weak_topics(db, current_user.id)

    # Generate questions via OpenRouter LLM
    parsed_resume = resume.parsed_json or {}
    raw_questions = await generate_questions(
        resume_json=parsed_resume,
        target_role=req.role_target,
        weak_topics=weak_topics
    )

    if not raw_questions:
        raw_questions = [
            {
                "text": f"Tell me about your background and why you are interested in the {req.role_target} role.",
                "topic_tag": "Behavioral",
                "difficulty": "easy",
                "type": "behavioral"
            },
            {
                "text": "Describe a complex technical challenge you faced in your recent project and how you solved it.",
                "topic_tag": "Problem Solving",
                "difficulty": "medium",
                "type": "technical"
            }
        ]

    # Create session
    session_obj = InterviewSession(
        user_id=current_user.id,
        resume_id=resume.id,
        role_target=req.role_target,
        status="active"
    )
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)

    # Save questions
    q_schemas = []
    for index, q in enumerate(raw_questions):
        question_obj = Question(
            session_id=session_obj.id,
            text=q.get("text", "Interview question"),
            topic_tag=q.get("topic_tag", "General"),
            difficulty=q.get("difficulty", "medium"),
            type=q.get("type", "technical"),
            order_index=index
        )
        db.add(question_obj)
        db.commit()
        db.refresh(question_obj)
        q_schemas.append(QuestionSchema.from_orm(question_obj))

    return SessionStartResponse(
        session_id=session_obj.id,
        role_target=session_obj.role_target,
        questions=q_schemas
    )


@router.get("/{session_id}")
def get_session_details(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session_obj = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    questions = db.query(Question).filter(Question.session_id == session_id).order_by(Question.order_index).all()
    q_data = []
    for q in questions:
        ans = db.query(Answer).filter(Answer.question_id == q.id).first()
        eval_data = None
        grammar_data = None

        if ans and ans.evaluation:
            eval_data = {
                "score": ans.evaluation.score,
                "criteria_json": ans.evaluation.criteria_json,
                "rationale": ans.evaluation.rationale,
                "ideal_answer_json": ans.evaluation.ideal_answer_json,
                "topic_tag": ans.evaluation.topic_tag
            }

        if ans and ans.grammar_evaluation:
            grammar_data = {
                "grammar_score": ans.grammar_evaluation.grammar_score,
                "issues": ans.grammar_evaluation.issues_json or [],
                "filler_word_count": ans.grammar_evaluation.filler_word_count,
                "tone": ans.grammar_evaluation.tone,
                "corrected_version": ans.grammar_evaluation.corrected_version
            }

        q_data.append({
            "id": q.id,
            "text": q.text,
            "topic_tag": q.topic_tag,
            "difficulty": q.difficulty,
            "type": q.type,
            "order_index": q.order_index,
            "answer": ans.user_response if ans else None,
            "evaluation": eval_data,
            "grammar_evaluation": grammar_data
        })

    study_plan_data = None
    if session_obj.study_plan:
        study_plan_data = session_obj.study_plan.plan_json

    return {
        "id": session_obj.id,
        "role_target": session_obj.role_target,
        "status": session_obj.status,
        "started_at": session_obj.started_at,
        "ended_at": session_obj.ended_at,
        "questions": q_data,
        "study_plan": study_plan_data
    }


@router.post("/{session_id}/answer", response_model=AnswerSubmitResponse)
async def submit_answer(
    session_id: int,
    req: AnswerSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session_obj = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if session_obj.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session is already completed")

    # Find unanswered question with lowest order_index
    questions = db.query(Question).filter(Question.session_id == session_id).order_by(Question.order_index).all()
    current_q = None
    for q in questions:
        ans = db.query(Answer).filter(Answer.question_id == q.id).first()
        if not ans:
            current_q = q
            break

    if not current_q:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="All questions in session are already answered")

    # Save user answer
    answer_obj = Answer(
        question_id=current_q.id,
        user_response=req.user_response
    )
    db.add(answer_obj)
    db.commit()
    db.refresh(answer_obj)

    # Concurrently execute Content Answer Evaluator AND Grammar Coach Agent using asyncio.gather
    eval_res, grammar_res = await asyncio.gather(
        evaluate_answer(
            question_text=current_q.text,
            user_response=req.user_response,
            topic_tag=current_q.topic_tag
        ),
        evaluate_grammar(answer_text=req.user_response)
    )

    # Save Content Evaluation Record
    eval_obj = Evaluation(
        answer_id=answer_obj.id,
        score=eval_res["score"],
        criteria_json=eval_res.get("criteria", {"clarity": 7, "specificity": 7, "relevance": 7}),
        rationale=eval_res.get("rationale", "Response recorded."),
        ideal_answer_json=eval_res.get("ideal_answer_points", []),
        topic_tag=current_q.topic_tag
    )
    db.add(eval_obj)

    # Save Grammar Evaluation Record
    grammar_obj = GrammarEvaluation(
        answer_id=answer_obj.id,
        grammar_score=grammar_res.get("grammar_score", 8.0),
        issues_json=grammar_res.get("issues", []),
        filler_word_count=grammar_res.get("filler_word_count", 0),
        tone=grammar_res.get("tone", "professional"),
        corrected_version=grammar_res.get("corrected_version", req.user_response)
    )
    db.add(grammar_obj)
    db.commit()

    db.refresh(eval_obj)
    db.refresh(grammar_obj)

    # Check for follow-up question
    follow_up_schema = None
    follow_up_data = await evaluate_shallowness_and_maybe_followup(
        question_text=current_q.text,
        user_answer=req.user_response,
        topic_tag=current_q.topic_tag,
        eval_score=eval_obj.score
    )

    if follow_up_data and current_q.type != "follow-up":
        # Shift order_indices of questions after current_q
        subsequent_qs = db.query(Question).filter(
            Question.session_id == session_id,
            Question.order_index > current_q.order_index
        ).all()
        for sq in subsequent_qs:
            sq.order_index += 1
        db.commit()

        new_fq = Question(
            session_id=session_id,
            text=follow_up_data["text"],
            topic_tag=follow_up_data["topic_tag"],
            difficulty=follow_up_data["difficulty"],
            type="follow-up",
            order_index=current_q.order_index + 1
        )
        db.add(new_fq)
        db.commit()
        db.refresh(new_fq)
        follow_up_schema = QuestionSchema.from_orm(new_fq)

    # Find next unanswered question
    all_qs_updated = db.query(Question).filter(Question.session_id == session_id).order_by(Question.order_index).all()
    next_q_schema = None
    for q in all_qs_updated:
        ans = db.query(Answer).filter(Answer.question_id == q.id).first()
        if not ans:
            next_q_schema = QuestionSchema.from_orm(q)
            break

    is_complete = (next_q_schema is None)

    evaluation_schema = EvaluationSchema(
        score=eval_obj.score,
        criteria_json=eval_obj.criteria_json,
        rationale=eval_obj.rationale,
        ideal_answer_json=eval_obj.ideal_answer_json or [],
        topic_tag=eval_obj.topic_tag
    )

    grammar_evaluation_schema = GrammarEvaluationSchema(
        grammar_score=grammar_obj.grammar_score,
        issues=grammar_obj.issues_json or [],
        filler_word_count=grammar_obj.filler_word_count,
        tone=grammar_obj.tone,
        corrected_version=grammar_obj.corrected_version
    )

    return AnswerSubmitResponse(
        answer_id=answer_obj.id,
        question_id=current_q.id,
        evaluation=evaluation_schema,
        grammar_evaluation=grammar_evaluation_schema,
        follow_up_question=follow_up_schema,
        next_question=next_q_schema,
        is_session_complete=is_complete
    )


@router.post("/{session_id}/complete", response_model=SessionCompleteResponse)
async def complete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session_obj = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    session_obj.status = "completed"
    session_obj.ended_at = datetime.datetime.utcnow()
    db.commit()

    # Update topic_scores table with rolling averages
    update_user_topic_scores(db, current_user.id)
    weak_topics = get_weak_topics(db, current_user.id)
    grammar_insights = get_recurring_grammar_issues(db, current_user.id)

    # Gather session Q&A summary for feedback planner
    questions = db.query(Question).filter(Question.session_id == session_id).order_by(Question.order_index).all()
    session_summary = []
    for q in questions:
        ans = db.query(Answer).filter(Answer.question_id == q.id).first()
        score = ans.evaluation.score if (ans and ans.evaluation) else 0.0
        rationale = ans.evaluation.rationale if (ans and ans.evaluation) else ""
        grammar_score = ans.grammar_evaluation.grammar_score if (ans and ans.grammar_evaluation) else 8.0
        session_summary.append({
            "question": q.text,
            "topic": q.topic_tag,
            "user_answer": ans.user_response if ans else "",
            "score": score,
            "grammar_score": grammar_score,
            "rationale": rationale
        })

    # Generate study plan via OpenRouter
    plan_dict = await generate_study_plan(
        session_results=session_summary,
        role_target=session_obj.role_target,
        historical_weak_topics=weak_topics,
        grammar_insights=grammar_insights
    )

    # Store study plan
    study_plan_obj = StudyPlan(
        user_id=current_user.id,
        session_id=session_obj.id,
        plan_json=plan_dict
    )
    db.add(study_plan_obj)
    db.commit()

    return SessionCompleteResponse(
        session_id=session_obj.id,
        status="completed",
        study_plan=plan_dict,
        weak_topics=weak_topics
    )
