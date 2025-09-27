# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.db.models import Base # Imports the declarative base from models.py

# Database connection engine
ENGINE = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

# SessionLocal is the class used to create a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

# Dependency to yield a database session (used in FastAPI endpoints)
def get_db():
    """Provides a database session for a single request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        # Ensures the session is closed after the request is complete
        db.close()