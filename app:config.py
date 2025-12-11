import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
JWT_ALGO = "HS256"
