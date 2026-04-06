"""
Verification Endpoints - Medical Claim Verification API
Backend Agent - API Layer
Production-ready endpoints with comprehensive error handling and validation
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import time
import logging
import uuid

from app.database import get_db
from app.schemas import VerifyRequest, VerifyResponse, VerificationResult
from app.services.verification import verification_service
from app.services.cache import cache_service
from app.models.claim import ClaimRecord

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/verify", tags=["verify"])

@router.post("/", response_model=VerifyResponse)
async def verify_claim(
    request: VerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Verify a medical claim with full pipeline
    
    Pipeline:
    1. Input validation
    2. Claim extraction
    3. Darija translation
    4. LLM verification
    5. Database storage
    6. Response formatting
    
    Returns: VerifyResponse with verification result and claim ID
    """
    try:
        logger.info(f"📋 Starting verification (lang={request.language}, user={request.user_id})")
        start_time = time.time()
        
        # Validate input
        if not request.text or len(request.text) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text must be between 10 and 5000 characters"
            )
        
        # Run verification pipeline
        result = await verification_service.verify_claim(
            text=request.text,
            language=request.language or "ar",
            db=db,
            user_id=request.user_id
        )
        
        # Retrieve created claim record
        claim = db.query(ClaimRecord).filter(
            ClaimRecord.original_text == request.text
        ).order_by(ClaimRecord.created_at.desc()).first()
        
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        
        logger.info(f"✅ Verification complete (id={claim.id if claim else 'N/A'}, time={elapsed_ms}ms)")
        
        return VerifyResponse(
            success=True,
            data=result,
            claim_id=claim.id if claim else 0,
            timestamp=claim.created_at if claim else None,
            message=f"Claim verified in {elapsed_ms}ms"
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification failed. Please try again later."
        )

from app.schemas import VerifyVideoUrlRequest, VideoProcessingResponse
@router.post("/video-url", response_model=VideoProcessingResponse)
async def verify_video_url_endpoint(
    request: VerifyVideoUrlRequest,
    db: Session = Depends(get_db)
):
    """
    Verify medical claims straight from a Video URL
    """
    try:
        logger.info(f"📋 Starting video URL verification ({request.url})")
        
        result = await verification_service.verify_video_url(
            url=request.url,
            language=request.language or "ar",
            db=db,
            user_id=request.user_id
        )
        
        return VideoProcessingResponse(
            success=True,
            job_id=str(uuid.uuid4()),
            status="completed",
            transcription=result.get("transcription"),
            english_translation=result.get("english_translation"),
            verification_results=result.get("verification_results", [])
        )
        
    except ValueError as e:
        logger.warning(f"Video validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Video Verification failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/batch", response_model=dict)
async def verify_batch(
    texts: list[str],
    language: str = "ar",
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Verify multiple claims concurrently
    
    Args:
        texts: List of claims to verify (max 10)
        language: Language code
        user_id: User identifier
    
    Returns:
        Job status with batch results
    """
    try:
        if len(texts) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 claims per batch"
            )
        
        job_id = str(uuid.uuid4())
        logger.info(f"🔄 Starting batch verification (job={job_id}, count={len(texts)})")
        
        results = await verification_service.verify_batch(
            texts=texts,
            language=language,
            db=db,
            user_id=user_id
        )
        
        return {
            "success": True,
            "job_id": job_id,
            "status": "completed",
            "count": len(results),
            "results": [r.model_dump() for r in results]
        }
    
    except Exception as e:
        logger.error(f"Batch verification failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch verification failed: {str(e)[:100]}"
        )

@router.get("/cached/{text_hash}", response_model=Optional[VerificationResult])
async def get_cached_result(text_hash: str, db: Session = Depends(get_db)):
    """
    Retrieve cached verification result by text hash
    
    Args:
        text_hash: SHA256 hash of original text
    
    Returns:
        Cached verification result if exists
    """
    try:
        result = cache_service.get(f"verification:{text_hash}")
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cached result not found"
            )
        
        logger.info(f"✅ Cache hit for hash {text_hash[:16]}...")
        return VerificationResult(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cache retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cached result"
        )

@router.get("/recent/{user_id}")
async def get_recent_verifications(
    user_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent verifications for a user
    
    Args:
        user_id: User identifier
        limit: Number of results (max 50)
    
    Returns:
        List of recent claims
    """
    try:
        if limit > 50:
            limit = 50
        
        claims = db.query(ClaimRecord).filter(
            ClaimRecord.user_id == user_id
        ).order_by(
            ClaimRecord.created_at.desc()
        ).limit(limit).all()
        
        return {
            "success": True,
            "user_id": user_id,
            "count": len(claims),
            "claims": [
                {
                    "id": c.id,
                    "claim": c.claim,
                    "verification_label": c.verification_label,
                    "confidence_score": c.confidence_score,
                    "created_at": c.created_at.isoformat()
                }
                for c in claims
            ]
        }
    
    except Exception as e:
        logger.error(f"Failed to retrieve user claims: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve claims"
        )

@router.get("/stats")
async def get_verification_stats(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get verification statistics for dashboard
    
    Args:
        days: Number of days to aggregate (1-90)
    
    Returns:
        Aggregated statistics
    """
    try:
        if not (1 <= days <= 90):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Days must be between 1 and 90"
            )
        
        stats = verification_service.get_verification_stats(db, days=days)
        
        return {
            "success": True,
            "data": stats
        }
    
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )
