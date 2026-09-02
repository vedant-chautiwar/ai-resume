from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.job import router as job_router
from app.api.routes.match import router as match_router
from app.api.routes.resume import router as resume_router
from app.core.config import FRONTEND_URL

app = FastAPI(title="AI Resume Matcher API")

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

if FRONTEND_URL:
    allowed_origins.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(resume_router)
app.include_router(job_router)
app.include_router(match_router)

@app.get("/")
def root():
    return {
        "message": "AI Resume Matcher API is running"
    }
