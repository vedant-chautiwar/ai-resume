from pymongo import MongoClient
from app.core.config import MONGODB_DATABASE,MONGODB_URI

client=MongoClient(MONGODB_URI)
db=client[MONGODB_DATABASE]
resumes_collection=db["resume"]
jobs_collection = db["jobs"]
matches_collection = db["matches"]
