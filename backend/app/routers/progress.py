from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_current_user
from app.models import User, TopicScore, Resume, JobMatch
from app.schemas import ProgressResponse, TopicScoreSchema, JobMatchSchema
from app.agents.weak_topic_tracker import get_weak_topics, update_user_topic_scores, get_recurring_grammar_issues

router = APIRouter(prefix="/progress", tags=["Progress"])

@router.get("", response_model=ProgressResponse)
def get_user_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Refresh topic scores
    update_user_topic_scores(db, current_user.id)
    
    scores = db.query(TopicScore).filter(TopicScore.user_id == current_user.id).order_by(TopicScore.topic_tag).all()
    score_schemas = [
        TopicScoreSchema(
            topic_tag=s.topic_tag,
            rolling_avg_score=s.rolling_avg_score,
            grammar_rolling_avg=getattr(s, "grammar_rolling_avg", 8.0),
            sessions_count=s.sessions_count,
            last_updated=s.last_updated
        )
        for s in scores
    ]

    weak_topics = get_weak_topics(db, current_user.id)
    grammar_insights = get_recurring_grammar_issues(db, current_user.id)

    # Fetch latest resume job matches if available
    latest_matches = None
    latest_resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.uploaded_at.desc())
        .first()
    )
    if latest_resume and latest_resume.job_match:
        latest_matches = JobMatchSchema(
            recommended_roles=latest_resume.job_match.recommended_roles_json,
            summary=latest_resume.job_match.summary
        )

    return ProgressResponse(
        topic_scores=score_schemas,
        weak_topics=weak_topics,
        grammar_overall_avg=grammar_insights.get("overall_grammar_avg", 8.0),
        common_grammar_issues=grammar_insights.get("common_issue_types", []),
        latest_job_matches=latest_matches
    )
