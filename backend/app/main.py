# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.db.database import Base, ENGINE 

app = FastAPI(
    title="City Vault Backend API",
    version="v1",
    openapi_url="/openapi.json",
)

# Create database tables upon startup (Development only)
# In production, use migrations (Alembic)
@app.on_event("startup")
def startup_db_tables():
    Base.metadata.create_all(bind=ENGINE)

# Set up CORS middleware to allow Vercel frontend access
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "City Vault API Running"}