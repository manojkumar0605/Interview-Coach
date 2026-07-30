import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import TopicScore, Evaluation, GrammarEvaluation, Answer, Question, Session as InterviewSession

def update_user_topic_scores(db: Session, user_id: int) -> List[TopicScore]:
    """
    Aggregates all evaluations (content and grammar) for user_id grouped by topic_tag.
    Computes rolling average score and grammar average score per topic.
    Updates or inserts records into topic_scores table.
    """
    # Fetch content evaluations
    results = (
        db.query(
            Evaluation.topic_tag,
            func.avg(Evaluation.score).label("avg_score"),
            func.count(Evaluation.id).label("eval_count")
        )
        .join(Answer, Evaluation.answer_id == Answer.id)
        .join(Question, Answer.question_id == Question.id)
        .join(InterviewSession, Question.session_id == InterviewSession.id)
        .filter(InterviewSession.user_id == user_id)
        .group_by(Evaluation.topic_tag)
        .all()
    )

    # Fetch grammar evaluations by topic
    grammar_results = (
        db.query(
            Question.topic_tag,
            func.avg(GrammarEvaluation.grammar_score).label("avg_grammar")
        )
        .join(Answer, GrammarEvaluation.answer_id == Answer.id)
        .join(Question, Answer.question_id == Question.id)
        .join(InterviewSession, Question.session_id == InterviewSession.id)
        .filter(InterviewSession.user_id == user_id)
        .group_by(Question.topic_tag)
        .all()
    )

    grammar_map = {topic: float(round(avg, 2)) for topic, avg in grammar_results if avg is not None}

    updated_scores = []
    for topic_tag, avg_score, eval_count in results:
        topic_record = (
            db.query(TopicScore)
            .filter(TopicScore.user_id == user_id, TopicScore.topic_tag == topic_tag)
            .first()
        )
        avg_val = float(round(avg_score, 2)) if avg_score else 0.0
        g_avg_val = grammar_map.get(topic_tag, 8.0)
        
        if not topic_record:
            topic_record = TopicScore(
                user_id=user_id,
                topic_tag=topic_tag,
                rolling_avg_score=avg_val,
                grammar_rolling_avg=g_avg_val,
                sessions_count=eval_count,
                last_updated=datetime.datetime.utcnow()
            )
            db.add(topic_record)
        else:
            topic_record.rolling_avg_score = avg_val
            topic_record.grammar_rolling_avg = g_avg_val
            topic_record.sessions_count = eval_count
            topic_record.last_updated = datetime.datetime.utcnow()
        
        updated_scores.append(topic_record)

    db.commit()
    return updated_scores


def get_weak_topics(db: Session, user_id: int) -> List[str]:
    records = (
        db.query(TopicScore)
        .filter(TopicScore.user_id == user_id)
        .all()
    )
    
    weak_topics = []
    for rec in records:
        if rec.rolling_avg_score < 6.0 and rec.sessions_count >= 2:
            weak_topics.append(rec.topic_tag)
            
    return weak_topics


def get_recurring_grammar_issues(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Aggregates recurring grammar, filler word, and clarity issues for user_id across sessions.
    Returns:
    {
      "overall_grammar_avg": 7.8,
      "total_filler_words": 12,
      "common_issue_types": [
        {"type": "filler_word", "count": 8},
        {"type": "clarity", "count": 4}
      ],
      "sample_corrections": [
        {"original": "...", "suggestion": "..."}
      ]
    }
    """
    evals = (
        db.query(GrammarEvaluation)
        .join(Answer, GrammarEvaluation.answer_id == Answer.id)
        .join(Question, Answer.question_id == Question.id)
        .join(InterviewSession, Question.session_id == InterviewSession.id)
        .filter(InterviewSession.user_id == user_id)
        .all()
    )

    if not evals:
        return {
            "overall_grammar_avg": 8.0,
            "total_filler_words": 0,
            "common_issue_types": [],
            "sample_corrections": []
        }

    total_score = sum(e.grammar_score for e in evals)
    total_fillers = sum(e.filler_word_count for e in evals)
    overall_avg = round(total_score / len(evals), 1)

    issue_counts = {}
    sample_corrections = []

    for e in evals:
        issues = e.issues_json or []
        for issue in issues:
            itype = issue.get("type", "grammar")
            issue_counts[itype] = issue_counts.get(itype, 0) + 1
            if len(sample_corrections) < 3 and issue.get("original") and issue.get("suggestion"):
                sample_corrections.append({
                    "original": issue["original"],
                    "suggestion": issue["suggestion"],
                    "explanation": issue.get("explanation", "")
                })

    common_types = [{"type": k, "count": v} for k, v in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)]

    return {
        "overall_grammar_avg": overall_avg,
        "total_filler_words": total_fillers,
        "common_issue_types": common_types,
        "sample_corrections": sample_corrections
    }
