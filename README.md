# AI Resume Analyzer & ATS Score Predictor

A full-stack AI-powered web app that analyzes a resume against a job description and
produces an ATS (Applicant Tracking System) compatibility score, matched/missing
skills, strengths, weaknesses, improvement suggestions, and recommended
certifications — with a downloadable PDF report and full analysis history.

---

## Tech Stack

**Frontend:** React, Vite, Tailwind CSS, React Router, Axios, Framer Motion, Recharts, React Hook Form

**Backend:** FastAPI, Python 3.12, SQLAlchemy, JWT Auth, Pydantic, Uvicorn

**ML/NLP:** scikit-learn, sentence-transformers, PyTorch, spaCy, pandas, NumPy

**Resume Parsing:** pdfplumber, PyPDF2, python-docx

**Database:** PostgreSQL

**Deployment:** Docker, Docker Compose, Nginx

---

## Features

- Register / Login with JWT access + refresh tokens, bcrypt password hashing
- Upload resume as PDF or DOCX
- Paste or save job descriptions
- NLP pipeline: text cleaning, stopword removal, lemmatization, skill extraction,
  sentence embeddings, cosine similarity
- Weighted ATS scoring (0–100): skill match, experience match, education match,
  keyword density, formatting
- Matched vs. missing skills, strengths, weaknesses, actionable suggestions,
  recommended certifications
- Full analysis history per user
- Downloadable PDF report per analysis
- Admin dashboard: platform stats, user management
- Responsive glassmorphism dashboard UI with dark mode, charts, and animations

---

## Project Structure

```
ai-resume-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI app entrypoint
│   │   ├── core/                  # config, security (JWT/bcrypt)
│   │   ├── db/                    # SQLAlchemy models + session
│   │   ├── schemas/                # Pydantic request/response models
│   │   ├── api/routes/            # auth, resumes, analysis, history, reports, profile, admin
│   │   ├── ml/                    # extraction, preprocessing, skills data, ATS pipeline
│   │   └── utils/                 # PDF report generator
│   ├── tests/                     # pytest API tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/                 # Landing, Login, Register, Dashboard, Analyze, AnalysisResult, History, Profile, Admin
│   │   ├── components/            # Layout, ScoreGauge, ScoreBreakdownChart, SkillBadgeList, ProtectedRoute
│   │   ├── context/                # AuthContext, ThemeContext
│   │   └── api/client.js          # Axios instance with auto token refresh
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── scripts/
│   ├── setup.sh                   # local (non-Docker) dev setup
│   └── seed_admin.py              # promote a user to admin
└── docs/
```

---

## Quick Start — Docker (recommended)

```bash
git clone <your-repo-url>
cd ai-resume-analyzer

cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env and set a strong SECRET_KEY before deploying to production

docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API docs (Swagger): http://localhost:8000/docs
- Postgres: localhost:5432

First-time ML model downloads (spaCy `en_core_web_sm`, sentence-transformers
`all-MiniLM-L6-v2`) happen at build/first-run time and require internet access.
If those downloads are unavailable, the pipeline automatically falls back to a
lightweight bag-of-words similarity so the app still functions.

---

## Running Locally Without Docker

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

cp .env.example .env
# Point DATABASE_URL at a local Postgres instance, or use SQLite for quick testing:
#   DATABASE_URL=sqlite:///./dev.db

uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Visit http://localhost:5173.

---

## Environment Variables

### backend/.env

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | JWT signing secret — **change in production** | dev value |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `7` |
| `DATABASE_URL` | SQLAlchemy connection string | Postgres via docker-compose |
| `FRONTEND_URL` | Allowed CORS origin | `http://localhost:5173` |
| `MAX_UPLOAD_SIZE_MB` | Max resume upload size | `5` |
| `UPLOAD_DIR` | Local storage path for uploaded files | `uploads` |

### frontend/.env

| Variable | Description |
|---|---|
| `VITE_API_PROXY_TARGET` | Backend URL used by Vite's dev proxy for `/api` |

---

## API Overview

All endpoints are prefixed with `/api`. Full interactive docs at `/docs`.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Create a new account |
| POST | `/api/auth/login` | Log in, returns access + refresh tokens |
| POST | `/api/auth/refresh` | Exchange refresh token for a new access token |
| POST | `/api/auth/logout` | Logout (client discards tokens) |
| GET | `/api/auth/me` | Current user |
| POST | `/api/resumes/upload` | Upload a PDF/DOCX resume |
| GET | `/api/resumes` | List your resumes |
| DELETE | `/api/resumes/{id}` | Delete a resume |
| POST | `/api/job-descriptions` | Save a job description |
| GET | `/api/job-descriptions` | List your job descriptions |
| POST | `/api/analyze` | Run ATS analysis for a resume + job description |
| GET | `/api/analyses/{id}` | Get a specific analysis |
| GET | `/api/history` | List all past analyses |
| GET | `/api/reports/{analysis_id}` | Download PDF report |
| GET/PUT | `/api/profile` | View / update your profile |
| GET | `/api/admin/stats` | Platform-wide stats (admin only) |
| GET | `/api/admin/users` | List all users (admin only) |
| PUT | `/api/admin/users/{id}/toggle-active` | Enable/disable a user (admin only) |
| GET | `/api/admin/model-info` | Which ML/DL model is active + metadata (admin only) |

### Making a user an admin

```bash
cd backend
source venv/bin/activate
python ../scripts/seed_admin.py you@example.com
```

---

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

---

## Security Notes

- Passwords hashed with bcrypt (72-byte input truncation handled safely)
- JWT access + refresh token flow, tokens signed with `SECRET_KEY`
- File upload validation: extension allow-list (PDF/DOCX only) + size limit
- All resume/JD/analysis data is scoped per-user; queries filter by `user_id`
- Pydantic validates and sanitizes all request bodies
- SQLAlchemy ORM (parameterized queries) prevents SQL injection
- CORS restricted to `FRONTEND_URL`
- **Before deploying to production:** replace `SECRET_KEY` with a long random
  value, put the API behind HTTPS, and consider adding rate limiting and a
  token-blacklist store (e.g. Redis) for true server-side logout.

---

## How the ATS Score Is Calculated

The pipeline (`backend/app/ml/pipeline.py`) computes six component sub-scores
and then determines the final ATS score using a **3-tier model cascade**:

| Priority | Model | File | Condition |
|---|---|---|---|
| 1 | Deep Learning (PyTorch) | `saved_models/ats_dl_model.pt` | Trained DL model + sentence-transformers available |
| 2 | Classical ML (scikit-learn) | `saved_models/ats_score_model.joblib` | Trained ML model available |
| 3 | Heuristic weighted average | Built-in | Always available (fallback) |

The six component sub-scores are always computed by heuristic functions
regardless of which model produces the final score:

| Component | Weight (heuristic) | Method |
|---|---|---|
| Skill Match | 40% | Extracted skill taxonomy overlap between resume and JD |
| Experience Match | 15% | Years-of-experience regex + experience keyword density |
| Education Match | 10% | Degree-level keyword matching |
| Keyword Density | 15% | Token overlap between resume and JD (post-cleaning) |
| Formatting | 10% | Section-header presence, length, special-character ratio |
| Semantic Similarity | 10% | Cosine similarity of sentence embeddings (`all-MiniLM-L6-v2`), with a Jaccard-similarity fallback if the embedding model isn't available |

To check which model is currently active, use `GET /api/admin/model-info`
(requires admin credentials).

---

## Training the ML/DL Models

Training is **optional** — the app works out of the box with the heuristic
scorer. Train the models to improve scoring accuracy.

### Prerequisites

- Python 3.12 with all `requirements.txt` dependencies installed
- Internet access (for sentence-transformers model download on first run)

### Step 1: Generate training data

```bash
cd backend
python -m app.ml.data.generate_training_data
```

This creates `backend/app/ml/data/training_data.csv` with 2,500 labeled rows.
Uses a fixed random seed for reproducibility.

### Step 2: Train both models

```bash
python -m app.ml.train_classical && python -m app.ml.train_dl
```

**Expected output:**
- Classical ML: prints MAE, RMSE, R² for RandomForest and GradientBoosting,
  picks the winner, saves to `saved_models/ats_score_model.joblib`
- DL: prints loss per epoch, early-stops on val MAE, saves to
  `saved_models/ats_dl_model.pt`

**Expected runtime:** ~2–5 minutes total on a modern CPU.

### Step 3: Verify

```bash
# Check which model is loaded
curl -H "Authorization: Bearer <admin_token>" http://localhost:8000/api/admin/model-info

# Run the test suite
pytest tests/test_ml_pipeline.py -v
```

### Retraining

To retrain with fresh data, simply re-run steps 1 and 2. The old model files
are overwritten. The server picks up new models on next restart (models are
loaded lazily on first request and cached in memory).

### Docker deployment

If you train models *before* building the Docker image, the `COPY . .`
instruction includes `saved_models/` in the image. Otherwise the container
starts in heuristic-only mode.

---

## Future Improvements

- Multi-resume comparison against one job description
- Editable, admin-managed skill taxonomy (already modeled in `skill_database` table)
- Async/background job processing for large-batch analysis
- Redis-backed token blacklist for immediate logout revocation
- Resume version diffing to track score improvement over edits
