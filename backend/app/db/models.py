from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship("Resume", back_populates="owner", cascade="all, delete-orphan")
    job_descriptions = relationship("JobDescription", back_populates="owner", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="owner", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    raw_text = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="resumes")
    analyses = relationship("Analysis", back_populates="resume", cascade="all, delete-orphan")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="job_descriptions")
    analyses = relationship("Analysis", back_populates="job_description", cascade="all, delete-orphan")


class SkillDatabase(Base):
    __tablename__ = "skill_database"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, index=True, nullable=False)
    category = Column(String(60), nullable=False, default="technical")  # technical | soft


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)

    ats_score = Column(Float, nullable=False)
    skill_match_score = Column(Float, nullable=False)
    experience_match_score = Column(Float, nullable=False)
    education_match_score = Column(Float, nullable=False)
    keyword_density_score = Column(Float, nullable=False)
    formatting_score = Column(Float, nullable=False)

    matched_skills = Column(JSON, nullable=False, default=list)
    missing_skills = Column(JSON, nullable=False, default=list)
    strengths = Column(JSON, nullable=False, default=list)
    weaknesses = Column(JSON, nullable=False, default=list)
    suggestions = Column(JSON, nullable=False, default=list)
    recommended_certifications = Column(JSON, nullable=False, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="analyses")
    resume = relationship("Resume", back_populates="analyses")
    job_description = relationship("JobDescription", back_populates="analyses")
    report = relationship("Report", back_populates="analysis", uselist=False, cascade="all, delete-orphan")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, unique=True)
    filepath = Column(String(500), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="report")
