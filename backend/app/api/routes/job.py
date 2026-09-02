from fastapi import APIRouter, HTTPException

from app.core.database import jobs_collection
from app.schemas.job import JobCreate, JobResponse

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

from bson import ObjectId

import os


router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"]
)


@router.post("/", response_model=JobResponse)
async def create_job(job: JobCreate):

    job_data = {
        "title": job.title,
        "description": job.description
    }

    result = jobs_collection.insert_one(job_data)

    job_id = str(result.inserted_id)

    langchain_document = Document(
        page_content=job.description,
        metadata={
            "title": job.title,
            "job_id": job_id
        }
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = text_splitter.split_documents(
        [langchain_document]
    )

    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    vectorstore_path = os.path.join(
        "data",
        "vectorstore",
        "jobs",
        job_id
    )

    os.makedirs(
        vectorstore_path,
        exist_ok=True
    )

    vectorstore.save_local(vectorstore_path)

    return {
        "job_id": job_id,
        "title": job.title,
        "description": job.description
    }


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):

    if not ObjectId.is_valid(job_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid job ID"
        )

    job = jobs_collection.find_one(
        {"_id": ObjectId(job_id)}
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found in database"
        )

    return {
        "job_id": str(job["_id"]),
        "title": job["title"],
        "description": job["description"]
    }

@router.get("/{job_id}/search")
async def search_job(
    job_id:str,
    query:str
):
    if not ObjectId.is_valid(job_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid job ID"
        )

    vectorstore_path=os.path.join(
        "data",
        "vectorstore",
        "jobs",
        job_id
    )

    if not os.path.exists(vectorstore_path):
        raise HTTPException(
            status_code=404,
            detail="Vector store not found"
        )

    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    vectorstore = FAISS.load_local(
        vectorstore_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )

    results = retriever.invoke(query)

    return {
        "query": query,
        "results": [
            {
                "content": document.page_content,
                "metadata": document.metadata
            }
            for document in results
        ]
    }