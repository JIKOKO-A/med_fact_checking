"""
Pydantic Schemas for Request/Response Validation
Backend Agent - API Contracts
"""
from pydantic import BaseModel, Field, FileUrl
from typing import Optional, Dict, Any
from datetime import datetime

# ============ REQUEST SCHEMAS ============

class VerifyRequest(BaseModel):
    """Schema for text verification endpoint"""
    text: str = Field(..., min_length=10, max_length=5000, description="Text to verify")
    user_id: Optional[str] = Field(None, description="User identifier for tracking")
    language: Optional[str] = Field("ar", description="Original language code")

class VideoUploadRequest(BaseModel):
    """Schema for video upload endpoint"""
    file_path: str = Field(..., description="Path to uploaded video file")
    user_id: Optional[str] = Field(None, description="User identifier")
    video_type: Optional[str] = Field("mp4", description="Video format")

class VerifyVideoUrlRequest(BaseModel):
    """Schema for video URL extraction and verification"""
    url: str = Field(..., description="URL of the video to fetch and verify")
    user_id: Optional[str] = Field(None, description="User identifier for tracking")
    language: Optional[str] = Field("ar", description="Original language code")


# ============ RESPONSE SCHEMAS ============

class VerificationResult(BaseModel):
    """Complete verification result matching ML/NLP output schema"""
    original_text: str
    original_language: str
    darija_latin: str
    darija_arabic: str
    claim: str
    claim_type: str
    verification_label: str  # true, false, partially_true, unverifiable
    explanation: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    source_url: Optional[str] = None
    medical_domain: str
    processing_time_ms: Optional[float] = None

    class Config:
        schema_extra = {
            "example": {
                "original_text": "الحمى تعالج بالماء البارد فقط",
                "original_language": "ar",
                "darija_latin": "semma ttal7 b wayl brrd fqq",
                "darija_arabic": "سميا تتالح بوايل برد فقق",
                "claim": "Fever can only be treated with cold water",
                "claim_type": "treatment",
                "verification_label": "false",
                "explanation": "Fever requires medical intervention including medication...",
                "confidence_score": 0.95,
                "source_url": "https://medical-source.com/fever-treatment",
                "medical_domain": "general_medicine",
                "processing_time_ms": 1250.5
            }
        }

class VerifyResponse(BaseModel):
    """Response for verify endpoint"""
    success: bool
    data: VerificationResult
    claim_id: int
    timestamp: datetime
    message: Optional[str] = None

class VideoProcessingResponse(BaseModel):
    """Response for video processing"""
    success: bool
    job_id: str
    status: str  # pending, processing, completed, failed
    transcription: Optional[str] = None
    english_translation: Optional[str] = None
    verification_results: Optional[list[VerificationResult]] = None
    error: Optional[str] = None
    estimated_time_remaining_seconds: Optional[float] = None

class ClaimDataResponse(BaseModel):
    """Response for dataset retrieval"""
    total_count: int
    page: int
    per_page: int
    claims: list[VerificationResult]
    filters_applied: Dict[str, Any]

class AnalyticsData(BaseModel):
    """Analytics dashboard data"""
    total_verified: int
    true_count: int
    false_count: int
    partial_count: int
    unverifiable_count: int
    avg_confidence_score: float
    domain_distribution: Dict[str, int]
    daily_trend: list[Dict[str, Any]]  # time series data
    misinformation_rate: float
    avg_processing_time_ms: float
    timestamp: datetime

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str  # healthy, degraded, unhealthy
    database: str
    redis: str
    ml_service: str
    version: str
