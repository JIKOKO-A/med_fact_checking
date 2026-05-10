import logging,asyncio,time
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class DummyClaimExtractor:
    def extract(self, text, lang):
        return {"claim": text, "claim_type": "general", "entities": []}

class DummyTranslator:
    def translate(self, text, scripts=None):
        return {"latin": text, "arabic": text}

class DummyRAGVerifier:
    def verify(self, claim, claim_type="general", language="ar"):
        return {"label": "true", "confidence": 0.8, "explanation": "Verified", "domain": "general_medicine"}

class VerificationService:
    def __init__(self):
        try:
            self.claim_extractor = DummyClaimExtractor()
            self.darija_translator = DummyTranslator()
            self.rag_verifier = DummyRAGVerifier()
            logger.info("? VerificationService initialized")
        except Exception as e:
            logger.error(f"? Init failed: {e}", exc_info=True)
            raise
    
    async def verify_claim(self, text: str, language: str, db, user_id: Optional[str] = None) -> Dict:
        start_time = time.time()
        if not text or len(text) < 10 or len(text) > 5000:
            raise ValueError("Text must be 10-5000 characters")
        
        # Run extractor and translator (mocked or synchronous for now)
        claim_data = self.claim_extractor.extract(text, language)
        darija_data = self.darija_translator.translate(claim_data["claim"])
        verification = self.rag_verifier.verify(claim_data["claim"])
        
        # Ensure all fields for VerificationResult schema are present
        res_dict = {
            "original_text": text,
            "original_language": language,
            "darija_latin": darija_data.get("latin", ""),
            "darija_arabic": darija_data.get("arabic", ""),
            "claim": claim_data.get("claim", text),
            "claim_type": claim_data.get("claim_type", "general"),
            "verification_label": verification.get("label", "unverifiable"),
            "explanation": verification.get("explanation", "Verification processing complete."),
            "confidence_score": float(verification.get("confidence", 0.0)),
            "medical_domain": verification.get("domain", "general_medicine"),
            "processing_time_ms": round((time.time() - start_time) * 1000, 2)
        }

        # Create database record
        from app.models.claim import ClaimRecord
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
            user_id=user_id
        )
        db.add(new_claim)
        db.commit()
        db.refresh(new_claim)
        
        return res_dict

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
                # verify_claim is already async
                vr = await self.verify_claim(full_text[:5000], language, db, user_id)
                results = [vr]
                
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
            res = await self.verify_claim(text, language, db, user_id)
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
