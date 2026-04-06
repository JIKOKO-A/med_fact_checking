"""
Database Models for Claims and Verification
Backend Agent - Models Layer
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class ClaimRecord(Base):
    """Store verified claims and their metadata"""
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(Text, nullable=False)
    original_language = Column(String(50), default="unknown")
    
    # Darija translations
    darija_latin = Column(Text, nullable=True)
    darija_arabic = Column(Text, nullable=True)
    
    # Claim information
    claim = Column(Text, nullable=False)
    claim_type = Column(String(100), nullable=True)  # health, vaccine, medication, etc.
    
    # Verification results
    verification_label = Column(String(50), nullable=False)  # true, false, partially_true, unverifiable
    explanation = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.0)
    
    # Source information
    source_url = Column(String(500), nullable=True)
    medical_domain = Column(String(100), nullable=True)  # cardiology, oncology, etc.
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(String(100), nullable=True, index=True)
    
    # Video metadata
    video_file_path = Column(String(500), nullable=True)
    transcription = Column(Text, nullable=True)
    
    # Additional metadata
    raw_response = Column(JSON, nullable=True)  # Store LLM response for debugging

    def __repr__(self):
        return f"<ClaimRecord(id={self.id}, claim='{self.claim[:50]}...', label='{self.verification_label}')>"


class VerificationLog(Base):
    """Track all verification attempts for analytics"""
    __tablename__ = "verification_logs"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, nullable=True)
    
    # Request info
    input_text = Column(Text, nullable=False)
    input_type = Column(String(20), default="text")  # text, video, audio
    
    # Response info
    processing_time_ms = Column(Float, default=0.0)
    status = Column(String(50), default="success")  # success, failed, partial
    error_message = Column(Text, nullable=True)
    
    # Analytics
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    model_version = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    def __repr__(self):
        return f"<VerificationLog(id={self.id}, status='{self.status}', time={self.processing_time_ms}ms)>"


class Statistics(Base):
    """Store aggregated statistics for dashboard"""
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, index=True)
    
    # Daily statistics
    date = Column(String(10), unique=True, index=True)  # YYYY-MM-DD
    
    # Counts
    total_claims = Column(Integer, default=0)
    verified_true = Column(Integer, default=0)
    verified_false = Column(Integer, default=0)
    verified_partial = Column(Integer, default=0)
    unverifiable = Column(Integer, default=0)
    
    # Domain distribution
    domain_stats = Column(JSON, default={})  # {"cardiology": 10, "oncology": 5, ...}
    
    # Confidence metrics
    avg_confidence = Column(Float, default=0.0)
    
    # Updated timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Statistics(date='{self.date}', total={self.total_claims})>"
