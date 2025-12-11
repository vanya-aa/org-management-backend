from datetime import datetime, timedelta
from jose import jwt
from app.config import JWT_SECRET, JWT_ALGO

def create_token(admin_id, org_name):
    payload = {
        "admin_id": str(admin_id),
        "organization": org_name,
        "exp": datetime.utcnow() + timedelta(hours=8)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
