"""
Health Check Endpoints
Backend Agent - Health Monitoring
"""
from fastapi import APIRouter, status
from app.schemas import HealthCheckResponse
from datetime import datetime
from sqlalchemy import text

router = APIRouter(prefix="/api/v1/health", tags=["health"])

@router.get("/", response_model=HealthCheckResponse)
def health_check():
    """Health check endpoint for monitoring"""
    
    # Check database
    db_status = "healthy"
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        db_status = "unhealthy"
    
    # Check Redis
    redis_status = "healthy"
    try:
        from app.services.cache import cache_service
        cache_service.client.ping()
    except Exception as e:
        redis_status = "unhealthy"
    
    # Check ML service
    ml_status = "healthy"
    try:
        import sys
        import os
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        if root_path not in sys.path:
            sys.path.insert(0, root_path)
            
        from ml_nlp.pipeline.claim_extractor_v2 import get_claim_extractor
        from ml_nlp.pipeline.rag_verifier import get_rag_verifier
        get_claim_extractor()
        get_rag_verifier()
    except Exception as e:
        ml_status = "unhealthy"
    
    overall_status = "healthy"
    if db_status != "healthy" or redis_status != "healthy" or ml_status != "healthy":
        overall_status = "degraded"
    if db_status == "unhealthy":
        overall_status = "unhealthy"
    
    return HealthCheckResponse(
        status=overall_status,
        database=db_status,
        redis=redis_status,
        ml_service=ml_status,
        version="1.0.0"
    )

@router.get("/ready")
def readiness_check():
    """Kubernetes readiness probe"""
    return {"ready": True, "timestamp": datetime.utcnow()}

