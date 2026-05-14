import logging,asyncio,time
from typing import Dict, Optional, List
import sys
import os

logger = logging.getLogger(__name__)

# Support both local and Docker paths for ml_nlp
local_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
docker_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if os.path.exists(os.path.join(local_root, "ml_nlp")) and local_root not in sys.path:
    sys.path.insert(0, local_root)
if os.path.exists(os.path.join(docker_root, "ml_nlp")) and docker_root not in sys.path:
    sys.path.insert(0, docker_root)

from ml_nlp.pipeline.claim_extractor_v2 import get_claim_extractor
from ml_nlp.pipeline.darija_translator import get_darija_translator
from ml_nlp.pipeline.rag_verifier import get_rag_verifier

class VerificationService:
    def __init__(self):
        try:
            self.claim_extractor = get_claim_extractor()
            self.darija_translator = get_darija_translator()
            self.rag_verifier = get_rag_verifier()
            logger.info("✅ VerificationService initialized with real ML pipeline")
        except Exception as e:
            logger.error(f"❌ Init failed: {e}", exc_info=True)
            raise
    
    async def verify_claim(self, text: str, language: str, db, user_id: Optional[str] = None) -> List[Dict]:
        start_time = time.time()
        if not text or len(text) < 10 or len(text) > 5000:
            raise ValueError("Text must be 10-5000 characters")
        
        # Run extractor
        claims_data = self.claim_extractor.extract(text, language)
        
        final_results = []
        from app.models.claim import ClaimRecord
        
        for claim_data in claims_data:
            claim_text = claim_data.get("claim", text)
            darija_data = self.darija_translator.translate(claim_text)
            verification = self.rag_verifier.verify(claim_text)
            
            # Ensure all fields for VerificationResult schema are present
            res_dict = {
                "original_text": text,
                "original_language": language,
                "darija_latin": darija_data.get("latin", ""),
                "darija_arabic": darija_data.get("arabic", ""),
                "claim": claim_text,
                "claim_type": claim_data.get("claim_type", "general"),
                "verification_label": verification.get("label", "unverifiable"),
                "explanation": verification.get("explanation", "Verification processing complete."),
                "confidence_score": float(verification.get("confidence", 0.0)),
                "medical_domain": verification.get("domain", "general_medicine"),
                "source_url": verification.get("source_url", ""),
                "processing_time_ms": round((time.time() - start_time) * 1000, 2)
            }

            # Create database record
            new_claim = ClaimRecord(
                original_text=res_dict["original_text"],
                original_language=res_dict["original_language"],
                darija_latin=res_dict["darija_latin"],
                darija_arabic=res_dict["darija_arabic"],
                claim=res_dict["claim"],
                claim_type=res_dict["claim_type"],
                verification_label=res_dict["verification_label"],
                explanation=res_dict["explanation"],
                confidence_score=res_dict["confidence_score"],
                medical_domain=res_dict["medical_domain"],
                source_url=res_dict["source_url"],
                user_id=user_id
            )
            db.add(new_claim)
            db.commit()
            db.refresh(new_claim)
            
            res_dict["claim_id"] = new_claim.id
            res_dict["timestamp"] = new_claim.created_at
            final_results.append(res_dict)
            
        return final_results

    async def verify_video_url(self, url: str, language: str, db, user_id: Optional[str] = None) -> Dict:
        start_time = time.time()
        from app.services.video_fetcher import video_fetcher
        
        # Download audio from URL (use thread for blocking yt-dlp)
        audio_path = await asyncio.to_thread(video_fetcher.download_audio, url)
        
        try:
            import sys
            import os
            # Ensure ml_nlp is in path - correctly resolve to /app/ml_nlp
            # From /app/app/services/verification.py, go up two levels to /app
            ml_nlp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            if ml_nlp_path not in sys.path:
                sys.path.insert(0, ml_nlp_path)
                
            from ml_nlp.services.video_transcriber import get_transcriber
            from ml_nlp.pipeline.english_translator import get_english_translator
            from ml_nlp.pipeline.darija_expert import get_darija_expert

            transcriber = get_transcriber()
            english_translator = get_english_translator()
            darija_expert = get_darija_expert()

            # Transcribe (use thread for blocking Whisper)
            transcription = await asyncio.to_thread(transcriber.transcribe, audio_path, language)
            raw_text = transcription.get("text", "")
            
            # --- 🕵️ 5th Agent: Transcription Quality Control ---
            full_text = darija_expert.refine_transcription(raw_text)
            
            if len(full_text) < 10:
                results = []
            else:
                # verify_claim is already async and returns a list
                results = await self.verify_claim(full_text[:5000], language, db, user_id)
                
            # Translate to English (use thread for blocking translation)
            raw_translation = ""
            if len(full_text) > 0:
                raw_translation = await asyncio.to_thread(english_translator.translate, full_text)
            
            # --- 🕵️ 5th Agent: Translation Quality Control ---
            english_text = darija_expert.refine_translation(full_text, raw_translation)
            logger.info(f"✅ English translation complete & refined (length: {len(english_text)})")
                
            return {
                "transcription": full_text,
                "english_translation": english_text,
                "verification_results": results,
                "processing_time_ms": round((time.time() - start_time) * 1000, 2)
            }
        finally:
            import os
            if os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except Exception:
                    pass

    async def verify_batch(self, texts: List[str], language: str, db, user_id: Optional[str] = None) -> List:
        from app.schemas import VerificationResult
        results = []
        for text in texts:
            res_list = await self.verify_claim(text, language, db, user_id)
            for res in res_list:
                results.append(VerificationResult(**res))
        return results

    def get_verification_stats(self, db, days: int = 7) -> Dict:
        from app.models.claim import ClaimRecord
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        claims = db.query(ClaimRecord).filter(ClaimRecord.created_at >= start_date).all()
        
        total = len(claims)
        true_c = sum(1 for c in claims if c.verification_label == "true")
        false_c = sum(1 for c in claims if c.verification_label == "false")
        partial_c = sum(1 for c in claims if c.verification_label == "partially_true")
        unverifiable_c = sum(1 for c in claims if c.verification_label == "unverifiable")
        
        avg_conf = sum(c.confidence_score for c in claims) / total if total > 0 else 0.0
        
        domain_dist = {}
        for c in claims:
            dom = c.medical_domain or "unknown"
            domain_dist[dom] = domain_dist.get(dom, 0) + 1
            
        mis_rate = (false_c + partial_c) / total if total > 0 else 0.0
        
        return {
            "total_verified": total,
            "true_count": true_c,
            "false_count": false_c,
            "partial_count": partial_c,
            "unverifiable_count": unverifiable_c,
            "avg_confidence_score": avg_conf,
            "domain_distribution": domain_dist,
            "misinformation_rate": mis_rate
        }

verification_service = VerificationService()
