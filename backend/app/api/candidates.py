"""Candidate and Application API routes."""

import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.config import get_settings
from app.models.user import User, UserRole
from app.models.candidate import Candidate, Application, ApplicationStatus
from app.models.job import Job
from app.schemas.candidate import (
    CandidateResponse, CandidateDetailResponse, CandidateListResponse,
    ApplicationCreate, ApplicationResponse, ApplicationWithDetails, ApplicationListResponse,
    MatchResult,
)
from app.api.auth import get_current_user, require_admin
from app.services.resume_parser import process_resume
from app.services.embedding import generate_embedding
from app.services.matching import match_candidate_to_job, compare_candidates_with_llm
from app.services.audit import create_audit_log

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])
settings = get_settings()


@router.post("/upload-resume", response_model=CandidateResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload and parse a resume (applicants upload their own, admin can upload for candidates)."""
    # Validate file type
    allowed_extensions = {".pdf", ".docx", ".doc"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}",
        )

    # Save file
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{file_id}{ext}")

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Process resume
    try:
        result = process_resume(file_path)
    except Exception as e:
        os.remove(file_path)
        msg = str(e)
        if "insufficient_quota" in msg or "You exceeded your current quota" in msg:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="OpenAI quota exceeded. Please check your plan and billing details.",
            )
        if "Error code: 429" in msg:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="OpenAI rate limit or quota exceeded. Please retry later or check billing.",
            )
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {msg}")

    # Generate embedding from de-identified data
    try:
        embedding = generate_embedding(result["embedding_text"])
    except Exception:
        embedding = None

    # Create or update candidate profile
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
    if candidate:
        # Update existing
        candidate.resume_file_path = file_path
        candidate.resume_original_name = file.filename
        candidate.parsed_data = result["parsed_data"]
        candidate.de_identified_data = result["de_identified_data"]
        candidate.skills = ", ".join(result["parsed_data"].get("skills", []))
        candidate.experience_years = result["parsed_data"].get("experience_years")
        candidate.education = str(result["parsed_data"].get("education", ""))
        if embedding:
            candidate.embedding = embedding
    else:
        # Create new
        candidate = Candidate(
            user_id=current_user.id,
            resume_file_path=file_path,
            resume_original_name=file.filename,
            parsed_data=result["parsed_data"],
            de_identified_data=result["de_identified_data"],
            skills=", ".join(result["parsed_data"].get("skills", [])),
            experience_years=result["parsed_data"].get("experience_years"),
            education=str(result["parsed_data"].get("education", "")),
            embedding=embedding,
        )
        db.add(candidate)

    db.commit()
    db.refresh(candidate)

    create_audit_log(
        db, action="resume_uploaded", user_id=current_user.id,
        entity_type="candidate", entity_id=candidate.id,
        details=f"Resume uploaded: {file.filename}",
        prompt_text=f"File: {file.filename}, Size: {len(content)} bytes",
        response_text=f"Parsed skills: {candidate.skills[:200] if candidate.skills else 'N/A'}",
    )

    return candidate


@router.get("", response_model=CandidateListResponse)
async def list_candidates(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all candidates (admin only)."""
    query = db.query(Candidate)
    if search:
        query = query.filter(Candidate.skills.ilike(f"%{search}%"))
    total = query.count()
    candidates = query.order_by(Candidate.created_at.desc()).offset(skip).limit(limit).all()
    return CandidateListResponse(candidates=candidates, total=total)


@router.get("/{candidate_id}", response_model=CandidateDetailResponse)
async def get_candidate(
    candidate_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get candidate details (admin only)."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.post("/apply", response_model=ApplicationResponse)
async def apply_to_job(
    application_data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apply to a job position (applicant)."""
    # Check job exists and is active
    job = db.query(Job).filter(Job.id == application_data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status.value != "active":
        raise HTTPException(status_code=400, detail="This job is not accepting applications")

    # Check candidate has a profile
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
    if not candidate:
        raise HTTPException(status_code=400, detail="Please upload your resume first")

    # Check for existing application
    existing = db.query(Application).filter(
        Application.candidate_id == candidate.id,
        Application.job_id == application_data.job_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied for this job")

    # Compute match score
    match_score = None
    match_reasoning = None
    if candidate.embedding is not None and job.embedding is not None:
        try:
            match_result = match_candidate_to_job(
                candidate_embedding=list(candidate.embedding),
                job_embedding=list(job.embedding),
                candidate_data=candidate.de_identified_data or {},
                job_data={
                    "title": job.title,
                    "description": job.description,
                    "requirements": job.requirements,
                },
            )
            match_score = match_result["final_score"]
            match_reasoning = match_result.get("reasoning", "")

            create_audit_log(
                db, action="match_computed", user_id=current_user.id,
                entity_type="application",
                details=f"Match score: {match_score} for candidate {candidate.id} → job {job.id}",
                prompt_text=f"Candidate skills: {candidate.skills[:200] if candidate.skills else 'N/A'}",
                response_text=f"Score: {match_score}, Reasoning: {match_reasoning[:300]}",
            )
        except Exception:
            pass

    application = Application(
        candidate_id=candidate.id,
        job_id=application_data.job_id,
        match_score=match_score,
        match_reasoning=match_reasoning,
        cover_letter=application_data.cover_letter,
        status=ApplicationStatus.PENDING,
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return application


@router.get("/applications/job/{job_id}", response_model=ApplicationListResponse)
async def list_applications_for_job(
    job_id: int,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all applications for a specific job (admin only), sorted by match score."""
    query = db.query(Application).filter(Application.job_id == job_id)
    total = query.count()
    applications = query.order_by(Application.match_score.desc().nullslast()).offset(skip).limit(limit).all()

    result = []
    for app in applications:
        candidate = app.candidate
        user = candidate.user if candidate else None
        result.append(ApplicationWithDetails(
            id=app.id,
            candidate_id=app.candidate_id,
            job_id=app.job_id,
            match_score=app.match_score,
            match_reasoning=app.match_reasoning,
            status=app.status.value,
            cover_letter=app.cover_letter,
            applied_at=app.applied_at,
            candidate_name=user.full_name if user else None,
            candidate_email=user.email if user else None,
            candidate_skills=candidate.skills if candidate else None,
            job_title=app.job.title if app.job else None,
        ))

    return ApplicationListResponse(applications=result, total=total)


@router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: int,
    new_status: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update application status (admin only)."""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = ApplicationStatus(new_status)
    db.commit()

    create_audit_log(
        db, action="status_updated", user_id=current_user.id,
        entity_type="application", entity_id=application_id,
        details=f"Application {application_id} status → {new_status}",
    )

    return {"message": "Status updated", "status": new_status}


@router.get("/my/applications", response_model=ApplicationListResponse)
async def my_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current applicant's applications."""
    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
    if not candidate:
        return ApplicationListResponse(applications=[], total=0)

    applications = db.query(Application).filter(
        Application.candidate_id == candidate.id
    ).order_by(Application.applied_at.desc()).all()

    result = []
    for app in applications:
        result.append(ApplicationWithDetails(
            id=app.id,
            candidate_id=app.candidate_id,
            job_id=app.job_id,
            match_score=app.match_score,
            match_reasoning=app.match_reasoning,
            status=app.status.value,
            cover_letter=app.cover_letter,
            applied_at=app.applied_at,
            job_title=app.job.title if app.job else None,
        ))

    return ApplicationListResponse(applications=result, total=len(result))
