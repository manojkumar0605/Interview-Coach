import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import engine, Base, SessionLocal, run_migrations
from app.models import User, Resume, JobMatch
from app.agents.job_matcher import match_roles

async def test_job_matcher_pipeline():
    print("=== 1. Initializing Database & Migrations ===")
    Base.metadata.create_all(bind=engine)
    run_migrations()
    db = SessionLocal()

    print("=== 2. Testing Job Matcher Agent directly ===")
    sample_resume_json = {
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "System Design", "REST APIs"],
        "years_experience": 5,
        "past_roles": ["Backend Developer", "Software Engineer"],
        "seniority_estimate": "Senior"
    }

    match_result = await match_roles(sample_resume_json)
    print(f"Market Positioning Summary: {match_result.get('summary')}")
    print(f"Recommended Roles Count: {len(match_result.get('recommended_roles', []))}")
    for r in match_result.get('recommended_roles', []):
        print(f" - [{r.get('match_score')}% Match] {r.get('title')} ({r.get('seniority_fit')}): {r.get('reasoning')}")

    print("\n=== 3. Testing Database Persistence ===")
    resume = db.query(Resume).first()
    if resume:
        job_match = JobMatch(
            resume_id=resume.id,
            recommended_roles_json=match_result.get("recommended_roles", []),
            summary=match_result.get("summary", "")
        )
        db.add(job_match)
        db.commit()
        print(f"Saved JobMatch record for Resume ID {resume.id} successfully!")

    print("\nJOB MATCHER PIPELINE TEST COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test_job_matcher_pipeline())
