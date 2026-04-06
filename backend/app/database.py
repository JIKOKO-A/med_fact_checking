"""
Database Configuration and Session Management
Backend Agent - Database Layer
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os

# Database URL from environment (REQUIRED for production)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    os.getenv(
        "SQLALCHEMY_DATABASE_URL",
        "postgresql://medical_user:secure_password_123@localhost:5432/medical_factcheck"
    )
)

if "user:password" in DATABASE_URL:
    import warnings
    warnings.warn(
        "⚠️  SECURITY: Default credentials detected.Set DATABASE_URL environment variable with secure credentials.",
        RuntimeWarning
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)
