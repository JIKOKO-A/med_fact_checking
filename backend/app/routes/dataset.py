"""
Dataset Retrieval Endpoints
Backend Agent - Data Layer
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas import ClaimDataResponse, VerificationResult
from app.models.claim import ClaimRecord

router = APIRouter(prefix="/api/v1/dataset", tags=["dataset"])

@router.get("/claims", response_model=ClaimDataResponse)
def get_claims(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    domain: Optional[str] = None,
    label: Optional[str] = None,
    min_confidence: float = Query(0.0, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """
    Retrieve claims from database with filtering
    - Pagination support
    - Filter by domain, verification label, confidence
    """
    query = db.query(ClaimRecord)
    
    filters_applied = {}
    
    if domain:
        query = query.filter(ClaimRecord.medical_domain == domain)
        filters_applied["domain"] = domain
    
    if label:
        query = query.filter(ClaimRecord.verification_label == label)
        filters_applied["label"] = label
    
    if min_confidence > 0:
        query = query.filter(ClaimRecord.confidence_score >= min_confidence)
        filters_applied["min_confidence"] = min_confidence
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    claims = query.order_by(
        ClaimRecord.created_at.desc()
    ).offset((page - 1) * per_page).limit(per_page).all()
    
    # Convert to response schema
    claim_data = [
        VerificationResult(
            original_text=c.original_text,
            original_language=c.original_language,
            darija_latin=c.darija_latin or "",
            darija_arabic=c.darija_arabic or "",
            claim=c.claim,
            claim_type=c.claim_type or "",
            verification_label=c.verification_label,
            explanation=c.explanation or "",
            confidence_score=c.confidence_score,
            source_url=c.source_url,
            medical_domain=c.medical_domain or ""
        )
        for c in claims
    ]
    
    return ClaimDataResponse(
        total_count=total_count,
        page=page,
        per_page=per_page,
        claims=claim_data,
        filters_applied=filters_applied
    )

@router.get("/stats/domains")
def get_domain_distribution(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get distribution of claims by medical domain"""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    domains = db.query(
        ClaimRecord.medical_domain,
        func.count(ClaimRecord.id).label("count")
    ).filter(
        ClaimRecord.created_at >= start_date
    ).group_by(ClaimRecord.medical_domain).all()
    
    return {
        "domain_distribution": {domain: count for domain, count in domains},
        "period_days": days
    }

@router.get("/export/csv")
def export_claims_csv(
    domain: Optional[str] = None,
    label: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export claims as CSV (for analytics)"""
    # To implement: return streaming CSV response
    raise NotImplementedError("CSV export in development")
