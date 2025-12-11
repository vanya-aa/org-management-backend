from pydantic import BaseModel, EmailStr

class OrgCreate(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class OrgUpdate(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class AdminLogin(BaseModel):
    email: EmailStr
    password: str
