"""
Analytics Dashboard Endpoints
Backend Agent - Analytics Layer
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict

from app.database import get_db
from app.schemas import AnalyticsData
from app.services.verification import verification_service
from app.models.claim import ClaimRecord, VerificationLog

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/dashboard", response_model=AnalyticsData)
def get_dashboard_analytics(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics for dashboard
    - Verification counts by label
    - Domain distribution
    - Confidence metrics
    - Daily trend
    """
    stats = verification_service.get_verification_stats(db, days=days)
    
    # Get daily trend
    from sqlalchemy import func
    start_date = datetime.utcnow() - timedelta(days=days)
    
    daily_data = db.query(
        func.date(ClaimRecord.created_at).label("date"),
        ClaimRecord.verification_label,
        func.count(ClaimRecord.id).label("count")
    ).filter(
        ClaimRecord.created_at >= start_date
    ).group_by(
        func.date(ClaimRecord.created_at),
        ClaimRecord.verification_label
    ).all()
    
    # Format daily trend
    trend_dict = {}
    for date, label, count in daily_data:
        date_str = str(date)
        if date_str not in trend_dict:
            trend_dict[date_str] = {
                "date": date_str,
                "true": 0,
                "false": 0,
                "partial": 0,
                "unverifiable": 0
            }
        
        if label == "true":
            trend_dict[date_str]["true"] += count
        elif label == "false":
            trend_dict[date_str]["false"] += count
        elif label == "partially_true":
            trend_dict[date_str]["partial"] += count
        else:
            trend_dict[date_str]["unverifiable"] += count
    
    daily_trend = sorted(list(trend_dict.values()), key=lambda x: x["date"])
    
    # Get average processing time
    avg_time = db.query(
        func.avg(VerificationLog.processing_time_ms)
    ).filter(
        VerificationLog.created_at >= start_date
    ).scalar() or 0.0
    
    return AnalyticsData(
        total_verified=stats["total_verified"],
        true_count=stats["true_count"],
        false_count=stats["false_count"],
        partial_count=stats["partial_count"],
        unverifiable_count=stats["unverifiable_count"],
        avg_confidence_score=stats["avg_confidence_score"],
        domain_distribution=stats["domain_distribution"],
        daily_trend=daily_trend,
        misinformation_rate=stats["misinformation_rate"],
        avg_processing_time_ms=float(avg_time),
        timestamp=datetime.utcnow()
    )

@router.get("/trending")
def get_trending_claims(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get most recently verified claims"""
    claims = db.query(ClaimRecord).order_by(
        ClaimRecord.created_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": c.id,
            "claim": c.claim,
            "label": c.verification_label,
            "confidence": c.confidence_score,
            "domain": c.medical_domain,
            "created_at": c.created_at
        }
        for c in claims
    ]

@router.get("/confidence-distribution")
def get_confidence_distribution(
    bins: int = Query(10, ge=1, le=20),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get distribution of confidence scores"""
    from sqlalchemy import func
    start_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(ClaimRecord).filter(
        ClaimRecord.created_at >= start_date
    ).all()
    
    # Create bins
    bin_size = 1.0 / bins
    distribution = {f"{i*bin_size:.2f}-{(i+1)*bin_size:.2f}": 0 for i in range(bins)}
    
    for result in results:
        bin_index = min(int(result.confidence_score / bin_size), bins - 1)
        bin_label = f"{bin_index*bin_size:.2f}-{(bin_index+1)*bin_size:.2f}"
        distribution[bin_label] += 1
    
    return {"confidence_distribution": distribution, "period_days": days}
