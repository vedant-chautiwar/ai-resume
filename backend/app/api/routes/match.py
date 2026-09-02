from fastapi import APIRouter, HTTPException

from app.core.database import jobs_collection, matches_collection, resumes_collection
from app.schemas.match import MatchAnalysis, MatchCreate, MatchResponse

from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama, OllamaEmbeddings

from bson import ObjectId

import json
import os


router = APIRouter(
    prefix="/api/matches",
    tags=["Matches"]
)


def load_vectorstore(vectorstore_path: str):
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    return FAISS.load_local(
        vectorstore_path,
        embeddings,
        allow_dangerous_deserialization=True
    )


def join_document_text(documents):
    return "\n\n".join(
        document.page_content
        for document in documents
    )


def make_safe_match_analysis(data: MatchAnalysis):
    score = max(0, min(100, data.score))

    return MatchAnalysis(
        score=score,
        summary=data.summary,
        strong_matches=data.strong_matches,
        partial_matches=data.partial_matches,
        skill_gaps=data.skill_gaps,
        recommendation=data.recommendation,
        improvement_suggestions=data.improvement_suggestions
    )


def analyze_match_with_llm(resume_context: str, job_context: str):
    llm = ChatOllama(
        model="llama3.1",
        temperature=0
    )

    prompt = f"""
You are an AI resume and job matching assistant.

Compare the provided resume context with the job description context.

Provide a detailed evaluation grounded ONLY in the resume and job description contexts.

Return:
- score: number from 0 to 100 matching overall qualification fit percentage.
- summary: a concise paragraph (4 to 6 sentences) explaining overall candidate fit, strongest relevant background, main reason for match/mismatch, key strengths, and key limitations.
- strong_matches: list of core skills/requirements from the job description clearly demonstrated in the resume.
- partial_matches: list of requirements where candidate has related or transferable experience, but not exact demonstration.
- skill_gaps: list of key job requirements missing or insufficiently demonstrated in the resume.
- recommendation: simple classification ("Strong Fit", "Moderate Fit", or "Low Fit") followed by 1 to 2 sentences explaining why.
- improvement_suggestions: list of 3 to 6 practical, actionable suggestions for improving fit for this specific job based on skill gaps.

Resume context:
{resume_context}

Job description context:
{job_context}
"""

    try:
        structured_llm = llm.with_structured_output(MatchAnalysis)
        analysis = structured_llm.invoke(prompt)
        return make_safe_match_analysis(analysis)
    except Exception:
        # Some LangChain/Ollama versions may not support structured output well.
        # This fallback asks for JSON and parses it in a simple way.
        json_prompt = f"""
{prompt}

Return only valid JSON in this exact format:
{{
  "score": 75,
  "summary": "Candidate demonstrates relevant skills...",
  "strong_matches": ["React", "Python"],
  "partial_matches": ["Express.js API development"],
  "skill_gaps": ["Docker", "AWS"],
  "recommendation": "Moderate Fit: Strong web development background, but lacks container experience.",
  "improvement_suggestions": [
    "Learn Docker and containerization.",
    "Gain practical AWS deployment experience."
  ]
}}
"""

        response = llm.invoke(json_prompt)
        content = response.content.strip()

        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1:
            raise HTTPException(
                status_code=500,
                detail="Could not read match result from LLM"
            )

        try:
            json_text = content[start:end + 1]
            data = json.loads(json_text)
            analysis = MatchAnalysis(**data)
            return make_safe_match_analysis(analysis)
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Could not parse match result from LLM"
            )


@router.post("", response_model=MatchResponse)
async def create_match(match: MatchCreate):

    if not ObjectId.is_valid(match.resume_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid resume ID"
        )

    if not ObjectId.is_valid(match.job_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid job ID"
        )

    resume = resumes_collection.find_one(
        {"_id": ObjectId(match.resume_id)}
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found in database"
        )

    job = jobs_collection.find_one(
        {"_id": ObjectId(match.job_id)}
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found in database"
        )

    resume_vectorstore_path = os.path.join(
        "data",
        "vectorstore",
        match.resume_id
    )

    job_vectorstore_path = os.path.join(
        "data",
        "vectorstore",
        "jobs",
        match.job_id
    )

    if not os.path.exists(resume_vectorstore_path):
        raise HTTPException(
            status_code=404,
            detail="Resume vector store not found"
        )

    if not os.path.exists(job_vectorstore_path):
        raise HTTPException(
            status_code=404,
            detail="Job vector store not found"
        )

    try:
        resume_vectorstore = load_vectorstore(resume_vectorstore_path)
        job_vectorstore = load_vectorstore(job_vectorstore_path)

        resume_retriever = resume_vectorstore.as_retriever(
            search_kwargs={"k": 4}
        )

        job_retriever = job_vectorstore.as_retriever(
            search_kwargs={"k": 4}
        )

        resume_documents = resume_retriever.invoke(job["description"])
        job_documents = job_retriever.invoke(resume["text"][:1000])

        resume_context = join_document_text(resume_documents)
        job_context = join_document_text(job_documents)

        analysis = analyze_match_with_llm(
            resume_context,
            job_context
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not create match analysis"
        )

    match_data = {
        "resume_id": match.resume_id,
        "job_id": match.job_id,
        "score": analysis.score,
        "summary": analysis.summary,
        "strong_matches": analysis.strong_matches,
        "partial_matches": analysis.partial_matches,
        "skill_gaps": analysis.skill_gaps,
        "recommendation": analysis.recommendation,
        "improvement_suggestions": analysis.improvement_suggestions,
        "matched_skills": analysis.strong_matches,
        "missing_skills": analysis.skill_gaps,
        "weak_skills": analysis.partial_matches
    }

    result = matches_collection.insert_one(match_data)

    return {
        "match_id": str(result.inserted_id),
        **match_data
    }


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: str):

    if not ObjectId.is_valid(match_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid resume ID"
        )

    match = matches_collection.find_one(
        {"_id": ObjectId(match_id)}
    )

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Match not found in database"
        )

    return {
        "match_id": str(match["_id"]),
        "resume_id": match["resume_id"],
        "job_id": match["job_id"],
        "score": match["score"],
        "summary": match["summary"],
        "strong_matches": match.get("strong_matches", match.get("matched_skills", [])),
        "partial_matches": match.get("partial_matches", match.get("weak_skills", [])),
        "skill_gaps": match.get("skill_gaps", match.get("missing_skills", [])),
        "recommendation": match.get("recommendation", ""),
        "improvement_suggestions": match.get("improvement_suggestions", []),
        "matched_skills": match.get("matched_skills", match.get("strong_matches", [])),
        "missing_skills": match.get("missing_skills", match.get("skill_gaps", [])),
        "weak_skills": match.get("weak_skills", match.get("partial_matches", []))
    }
