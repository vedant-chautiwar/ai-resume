from pydantic import BaseModel

class JobCreate(BaseModel):
    title:str
    description:str

class JobResponse(BaseModel):
    job_id:str
    title:str
    description:str