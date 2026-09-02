from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.database import resumes_collection
from app.schemas.resume import ResumeUploadResponse, ResumeResponse
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from bson import ObjectId
import fitz
import os

router = APIRouter(
    prefix="/api/resumes",
    tags=["Resumes"]
)


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only pdf files are allowed"
        )

    contents = await file.read()

    document = fitz.open(
        stream=contents,
        filetype="pdf"
    )

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    resume = {
        "filename": file.filename,
        "content_type": file.content_type,
        "text": text
    }

    result = resumes_collection.insert_one(resume)

    resume_id = str(result.inserted_id)

    langchain_document = Document(
        page_content=text,
        metadata={
            "filename": file.filename,
            "resume_id": resume_id
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
        resume_id
    )

    os.makedirs(
        vectorstore_path,
        exist_ok=True
    )

    vectorstore.save_local(vectorstore_path)

    return {
        "resume_id": resume_id,
        "filename": file.filename,
        "content_type": file.content_type
    }


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: str):

    if not ObjectId.is_valid(resume_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid resume ID"
        )

    resume = resumes_collection.find_one(
        {"_id": ObjectId(resume_id)}
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found in database"
        )

    return {
        "resume_id": str(resume["_id"]),
        "filename": resume["filename"],
        "content_type": resume["content_type"],
        "text": resume["text"]
    }

@router.get("/{resume_id}/search")
async def search_resume(
    resume_id:str,
    query:str
):
    if not ObjectId.is_valid(resume_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid resume ID"
        )

    vectorstore_path = os.path.join(
        "data",
        "vectorstore",
        resume_id
    )
    
    if not os.path.exists(vectorstore_path):
        raise HTTPException(
            status_code=404,
            detail="Vector store not found"
        )
    
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    vectorstore = FAISS.load_local(
        vectorstore_path,
        embeddings,
        allow_dangerous_deserialization=True
    )   

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )

    results = retriever.invoke(query)

    llm=ChatOllama(
        model="llama3.1",
        temperature=0
    )

    context = "\n\n".join(
        document.page_content
        for document in results
    )

    prompt = f"""
You are an AI resume assistant.

Answer the user's question using only the provided resume context.

Resume context:
{context}

Question:
{query}

If the answer cannot be found in the resume context, say that the information is not available in the resume.
"""

    response = llm.invoke(prompt)

    return {
        "query": query,
        "answer": response.content,
        "sources": [
            {
                "content": document.page_content,
                "metadata": document.metadata
            }
            for document in results
        ]
    }