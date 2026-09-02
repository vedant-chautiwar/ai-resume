from pydantic import BaseModel

class ResumeUploadResponse(BaseModel):
    resume_id: str
    filename:str
    content_type:str

class ResumeResponse(BaseModel):
    resume_id: str
    filename:str
    content_type:str
    text:str
