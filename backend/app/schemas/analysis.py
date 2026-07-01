from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class JobDescriptionCreate(BaseModel):
    title: Optional[str] = None
    raw_text: str


class JobDescriptionOut(BaseModel):
    id: int
    title: Optional[str]
    raw_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeOut(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    resume_id: int
    job_description_id: int


class AnalysisOut(BaseModel):
    id: int
    resume_id: int
    job_description_id: int
    ats_score: float
    skill_match_score: float
    experience_match_score: float
    education_match_score: float
    keyword_density_score: float
    formatting_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    recommended_certifications: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
