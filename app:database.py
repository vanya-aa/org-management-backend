from pymongo import MongoClient
from app.config import MONGO_URL

client = MongoClient(MONGO_URL)

# master_db stores organization metadata and admin users
master_db = client["master_db"]
