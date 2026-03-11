"""Job description model with embedding support."""

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import enum

from app.database import Base


class JobStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    employment_type = Column(String(100), nullable=True)  # full-time, part-time, contract
    seniority_level = Column(String(100), nullable=True)  # junior, mid, senior
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    salary_range = Column(String(255), nullable=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.DRAFT, nullable=False)
    embedding = Column(Vector(1536), nullable=True)  # text-embedding-3-small dimension

    # Foreign keys
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    created_by_user = relationship("User", back_populates="jobs_created")
    applications = relationship("Application", back_populates="job")
