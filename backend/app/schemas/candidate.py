"""Pydantic schemas for Candidate and Application operations."""

from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class CandidateBase(BaseModel):
    skills: Optional[str] = None
    experience_years: Optional[float] = None
    education: Optional[str] = None


class CandidateResponse(CandidateBase):
    id: int
    user_id: int
    resume_original_name: Optional[str] = None
    parsed_data: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CandidateDetailResponse(CandidateResponse):
    de_identified_data: Optional[dict] = None
    applications: Optional[List[Any]] = None


class CandidateListResponse(BaseModel):
    candidates: List[CandidateResponse]
    total: int


class ApplicationCreate(BaseModel):
    job_id: int
    cover_letter: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    match_score: Optional[float] = None
    match_reasoning: Optional[str] = None
    status: str
    cover_letter: Optional[str] = None
    applied_at: datetime

    model_config = {"from_attributes": True}


class ApplicationWithDetails(ApplicationResponse):
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    candidate_skills: Optional[str] = None
    job_title: Optional[str] = None


class ApplicationListResponse(BaseModel):
    applications: List[ApplicationWithDetails]
    total: int


class MatchResult(BaseModel):
    score: float
    reasoning: str
    strengths: List[str]
    gaps: List[str]


class CandidateCompareRequest(BaseModel):
    job_id: int
    application_ids: List[int]
    

class CandidateCompareSummary(BaseModel):
    application_id: int
    candidate_id: int
    candidate_name: Optional[str] = None
    strengths: List[str]
    gaps: List[str]


class CandidateCompareResponse(BaseModel):
    candidates: List[CandidateCompareSummary]
    analysis: str
    recommended_application_id: int
