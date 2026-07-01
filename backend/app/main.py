from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.database import Base, engine, SessionLocal
from app.db import models
from app.ml.skills_data import ALL_SKILLS, TECHNICAL_SKILLS
from app.api.routes import auth, resumes, analysis, history, reports, profile, admin

Base.metadata.create_all(bind=engine)


def seed_skill_database():
    db = SessionLocal()
    try:
        existing_count = db.query(models.SkillDatabase).count()
        if existing_count == 0:
            for skill in ALL_SKILLS:
                category = "technical" if skill in TECHNICAL_SKILLS else "soft"
                db.add(models.SkillDatabase(name=skill, category=category))
            db.commit()
    finally:
        db.close()


seed_skill_database()

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Resume Analyzer & ATS Score Predictor API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(analysis.router)
app.include_router(history.router)
app.include_router(reports.router)
app.include_router(profile.router)
app.include_router(admin.router)


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


from fastapi.staticfiles import StaticFiles
import os

frontend_dist = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
