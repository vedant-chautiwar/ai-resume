from pydantic import BaseModel


class MatchCreate(BaseModel):
    resume_id: str
    job_id: str


class MatchAnalysis(BaseModel):
    score: float
    summary: str
    strong_matches: list[str]
    partial_matches: list[str]
    skill_gaps: list[str]
    recommendation: str
    improvement_suggestions: list[str]


class MatchResponse(BaseModel):
    match_id: str
    resume_id: str
    job_id: str
    score: float
    summary: str
    strong_matches: list[str]
    partial_matches: list[str]
    skill_gaps: list[str]
    recommendation: str
    improvement_suggestions: list[str]
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    weak_skills: list[str] = []
