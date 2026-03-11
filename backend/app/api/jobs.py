"""Job management API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.job import Job, JobStatus
from app.schemas.job import (
    JobCreate, JobUpdate, JobResponse, JobListResponse,
    JDGenerateRequest, JDGenerateResponse,
)
from app.api.auth import get_current_user, require_admin
from app.services.jd_author import generate_job_description, create_jd_embedding_text
from app.services.embedding import generate_embedding
from app.services.audit import create_audit_log

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.get("", response_model=JobListResponse)
async def list_jobs(
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """List all jobs (public for applicants, all for admin)."""
    query = db.query(Job)
    if status_filter:
        query = query.filter(Job.status == JobStatus(status_filter))
    total = query.count()
    jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    return JobListResponse(jobs=jobs, total=total)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a single job by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new job posting (admin only)."""
    job = Job(
        **job_data.model_dump(),
        created_by=current_user.id,
    )

    # Generate embedding for the job
    embedding_text = create_jd_embedding_text(job_data.model_dump())
    try:
        job.embedding = generate_embedding(embedding_text)
    except Exception:
        pass  # Continue without embedding if it fails

    db.add(job)
    db.commit()
    db.refresh(job)

    create_audit_log(
        db, action="job_created", user_id=current_user.id,
        entity_type="job", entity_id=job.id,
        details=f"Created job: {job.title}",
    )

    return job


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update a job posting (admin only)."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = job_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "status":
            setattr(job, key, JobStatus(value))
        else:
            setattr(job, key, value)

    # Re-generate embedding if description changed
    if "description" in update_data or "requirements" in update_data:
        embedding_text = create_jd_embedding_text({
            "title": job.title,
            "department": job.department,
            "description": job.description,
            "requirements": job.requirements,
        })
        try:
            job.embedding = generate_embedding(embedding_text)
        except Exception:
            pass

    db.commit()
    db.refresh(job)

    create_audit_log(
        db, action="job_updated", user_id=current_user.id,
        entity_type="job", entity_id=job.id,
        details=f"Updated job: {job.title}",
    )

    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a job posting (admin only)."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()

    create_audit_log(
        db, action="job_deleted", user_id=current_user.id,
        entity_type="job", entity_id=job_id,
        details=f"Deleted job ID: {job_id}",
    )


@router.post("/generate-jd", response_model=JDGenerateResponse)
async def generate_jd(
    request: JDGenerateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Generate a job description using AI (admin only)."""
    result = generate_job_description(
        title=request.title,
        department=request.department,
        seniority_level=request.seniority_level,
        key_skills=request.key_skills,
        additional_notes=request.additional_notes,
    )

    create_audit_log(
        db, action="jd_generated", user_id=current_user.id,
        entity_type="job",
        details=f"AI generated JD for: {request.title}",
        prompt_text=f"Title: {request.title}, Dept: {request.department}, Level: {request.seniority_level}",
        response_text=result.get("description", "")[:500],
    )

    return JDGenerateResponse(**result)
