# app/main.py
import asyncio
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.api.core.config import settings
from app.api.v1.router import api_router
from app.api.db.database import ENGINE, get_db
from app.api.db.models import Base

app = FastAPI(
    title="City Vault Backend API",
    version="v1",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    try:
        # Test database connection
        async with ENGINE.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        
        # Create tables if they don't exist
        async with ENGINE.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables verified/created")
        
    except Exception as e:
        print(f"⚠️  Database connection failed: {str(e)}")
        print("⚠️  The API will run in a limited mode without database access")

# Set up CORS middleware to allow Vercel frontend access
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "API is running",
        "version": "1.0.0"
    }

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def read_root():
    return {"message": "City Vault API Running"}