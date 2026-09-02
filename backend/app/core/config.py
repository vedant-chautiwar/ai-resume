import os
from dotenv import load_dotenv
load_dotenv()

MONGODB_URI=os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")
MONGODB_DATABASE=os.getenv("MONGODB_DATABASE")
FRONTEND_URL=os.getenv("FRONTEND_URL")
