from fastapi import FastAPI
from app.routers import org_routes, admin_routes

app = FastAPI(title="Organization Management Service")

app.include_router(org_routes.router)
app.include_router(admin_routes.router)

@app.get("/")
def root():
    return {"message": "Organization Management Service is running"}
