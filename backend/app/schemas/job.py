"""Pydantic schemas for Job operations."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobBase(BaseModel):
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    seniority_level: Optional[str] = None
    description: str
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    salary_range: Optional[str] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    seniority_level: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    salary_range: Optional[str] = None
    status: Optional[str] = None


class JobResponse(JobBase):
    id: int
    status: str
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int


class JDGenerateRequest(BaseModel):
    title: str
    department: Optional[str] = None
    seniority_level: Optional[str] = None
    key_skills: Optional[str] = None
    additional_notes: Optional[str] = None


class JDGenerateResponse(BaseModel):
    description: str
    requirements: str
    benefits: str
