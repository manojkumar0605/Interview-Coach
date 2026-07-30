import io
import pdfplumber
import docx
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.deps import get_current_user
from app.models import User, Resume, JobMatch
from app.schemas import ResumeUploadResponse, JobMatchSchema
from app.agents.resume_analyzer import analyze_resume
from app.agents.job_matcher import match_roles

router = APIRouter(prefix="/resume", tags=["Resume"])

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    filename_lower = filename.lower()
    text = ""

    if filename_lower.endswith(".pdf"):
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages_text = [page.extract_text() or "" for page in pdf.pages]
                text = "\n".join(pages_text)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse PDF file: {str(e)}"
            )

    elif filename_lower.endswith(".docx") or filename_lower.endswith(".doc"):
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join([p.text for p in doc.paragraphs if p.text])
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse DOCX file: {str(e)}"
            )

    else:
        # Fallback to plain text
        try:
            text = file_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format or invalid encoding: {str(e)}"
            )

    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Extracted text from resume is empty."
        )

    return text

@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    target_role: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contents = await file.read()
    raw_text = extract_text_from_file(contents, file.filename)

    # Analyze resume using LLM
    try:
        parsed_json = await analyze_resume(raw_text, target_role=target_role)
    except Exception as e:
        parsed_json = {
            "skills": ["General Engineering"],
            "years_experience": 1,
            "past_roles": [],
            "seniority_estimate": "Junior"
        }

    seniority = parsed_json.get("seniority_estimate", "Mid-Level")

    resume_obj = Resume(
        user_id=current_user.id,
        raw_text=raw_text,
        parsed_json=parsed_json,
        target_role=target_role,
        seniority=seniority
    )
    db.add(resume_obj)
    db.commit()
    db.refresh(resume_obj)

    # Run Job Matcher Agent to recommend ranked job roles
    match_dict = await match_roles(parsed_json)
    job_match_obj = JobMatch(
        resume_id=resume_obj.id,
        recommended_roles_json=match_dict.get("recommended_roles", []),
        summary=match_dict.get("summary", "")
    )
    db.add(job_match_obj)
    db.commit()
    db.refresh(job_match_obj)

    job_matches_schema = JobMatchSchema(
        recommended_roles=job_match_obj.recommended_roles_json,
        summary=job_match_obj.summary
    )

    return ResumeUploadResponse(
        id=resume_obj.id,
        user_id=resume_obj.user_id,
        target_role=resume_obj.target_role,
        seniority=resume_obj.seniority,
        parsed_json=resume_obj.parsed_json or {},
        uploaded_at=resume_obj.uploaded_at,
        job_matches=job_matches_schema
    )


@router.get("/{resume_id}/matches", response_model=JobMatchSchema)
async def get_resume_job_matches(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume_obj = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()

    if not resume_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    if resume_obj.job_match:
        return JobMatchSchema(
            recommended_roles=resume_obj.job_match.recommended_roles_json,
            summary=resume_obj.job_match.summary
        )

    # Generate if missing
    parsed_json = resume_obj.parsed_json or {}
    match_dict = await match_roles(parsed_json)
    job_match_obj = JobMatch(
        resume_id=resume_obj.id,
        recommended_roles_json=match_dict.get("recommended_roles", []),
        summary=match_dict.get("summary", "")
    )
    db.add(job_match_obj)
    db.commit()
    db.refresh(job_match_obj)

    return JobMatchSchema(
        recommended_roles=job_match_obj.recommended_roles_json,
        summary=job_match_obj.summary
    )
