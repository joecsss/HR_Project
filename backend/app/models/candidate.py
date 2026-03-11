"""Candidate and Application models."""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import enum
from sqlalchemy import Enum as SQLEnum

from app.database import Base


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEWING = "reviewing"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    OFFERED = "offered"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    resume_file_path = Column(String(500), nullable=True)
    resume_original_name = Column(String(255), nullable=True)
    parsed_data = Column(JSON, nullable=True)  # Full parsed resume data
    de_identified_data = Column(JSON, nullable=True)  # PII removed version
    skills = Column(Text, nullable=True)  # Extracted skills as comma-separated
    experience_years = Column(Float, nullable=True)
    education = Column(Text, nullable=True)
    embedding = Column(Vector(1536), nullable=True)  # De-identified embedding

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="candidate_profile")
    applications = relationship("Application", back_populates="candidate")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    match_score = Column(Float, nullable=True)  # 0-100
    match_reasoning = Column(Text, nullable=True)  # AI-generated reasoning
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False)
    cover_letter = Column(Text, nullable=True)

    # Timestamps
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")
