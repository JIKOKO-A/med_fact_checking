"""
Claim Extraction Pipeline
ML/NLP Agent - NLP Processing Layer (v2 - Production Ready)
Extracts medical claims from text with fallback mechanisms
"""
from typing import Dict, List, Tuple, Optional
import numpy as np
import logging
import re

logger = logging.getLogger(__name__)

class ClaimExtractor:
    """Extract and classify medical claims from text with resilience"""
    
    # Medical claim types
    CLAIM_TYPES = [
        "medication",
        "symptom_treatment",
        "disease_prevention",
        "vaccine",
        "diagnosis",
        "nutrition",
        "exercise",
        "drug_side_effect",
        "condition_description",
        "general_health"
    ]
    
    # Medical keywords for fallback classification
    KEYWORD_PATTERNS = {
        "medication": r"\b(drug|medicine|medication|pill|tablet|capsule|vaccine|treatment|therapy)\b",
        "symptom_treatment": r"\b(treat|cure|remedy|relieve|heal|symptom|pain|ache|fever|cough)\b",
        "disease_prevention": r"\b(prevent|protection|immune|resistant|strengthen|avoid|reduce risk)\b",
        "vaccine": r"\b(vaccine|vaccination|immunize|inoculate|jab|shot)\b",
        "diagnosis": r"\b(diagnose|diagnosed|disease|condition|syndrome|disorder|infection|illness)\b",
        "nutrition": r"\b(vitamin|mineral|nutrient|food|diet|eating|calorie|protein|fat|carb)\b",
        "exercise": r"\b(exercise|physical activity|workout|train|sport|fitness|movement)\b",
        "drug_side_effect": r"\b(side effect|adverse|reaction|effect|complication|risk|danger)\b",
        "condition_description": r"\b(causes|symptoms|characteristics|signs|manifestation)\b",
        "general_health": r"\b(health|wellness|healthy|medical)\b"
    }
    
    def __init__(self):
        """Initialize claim extractor with optional transformers support"""
        self.classifier = None
        self.ner_pipeline = None
        
        # Try to load transformers models, but continue if not available
        try:
            from transformers import pipeline
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            logger.info("✅ BART classifier loaded")
        except Exception as e:
            logger.warning(f"⚠️  BART classifier not available: {e}. Using keyword fallback.")
        
        try:
            from transformers import pipeline
            self.ner_pipeline = pipeline(
                "token-classification",
                model="dslim/bert-base-multilingual-cased-ner",
                aggregation_strategy="simple"
            )
            logger.info("✅ NER pipeline loaded")
        except Exception as e:
            logger.warning(f"⚠️  NER pipeline not available: {e}. Using keyword fallback.")
        
        logger.info("✅ Claim Extractor initialized(with fallback support)")
    
    def extract(
        self, 
        text: str, 
        language: str = "ar"
    ) -> Dict:
        """
        Extract claims from text with fallback mechanisms
        
        Returns: {
            claim: str,
            claim_type: str,
            entities: List[str],
            type_confidence: float,
            original_language: str,
            original_text: str,
            method: str (transformer|fallback)
        }
        """
        try:
            # Clean text
            text = self._clean_text(text)
            
            if len(text) < 10:
                raise ValueError("Text too short for claim extraction (min 10 chars)")
            
            # Try NER if available
            entities = []
            if self.ner_pipeline:
                try:
                    entities = self._extract_entities_ml(text)
                except Exception as e:
                    logger.warning(f"ML NER failed, using keyword fallback: {e}")
                    entities = self._extract_entities_keywords(text)
            else:
                entities = self._extract_entities_keywords(text)
            
            # Classify claim type
            claim_type = None
            type_confidence = 0.0
            method = "fallback"
            
            if self.classifier:
                try:
                    claim_type, type_confidence = self._classify_claim_type_ml(text)
                    method = "transformer"
                except Exception as e:
                    logger.warning(f"ML classifier failed, using keyword fallback: {e}")
                    claim_type, type_confidence = self._classify_claim_type_keywords(text)
            else:
                claim_type, type_confidence = self._classify_claim_type_keywords(text)
            
            # Extract main claim
            main_claim = self._extract_main_claim(text, entities)
            
            return {
                "claim": main_claim,
                "claim_type": claim_type,
                "entities": entities,
                "type_confidence": type_confidence,
                "original_language": language,
                "original_text": text,
                "method": method
            }
        
        except Exception as e:
            logger.error(f"Claim extraction failed: {e}", exc_info=True)
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = " ".join(text.split())
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        # Remove extra punctuation
        text = re.sub(r'[^\w\s\.\!\?\-]', '', text)
        return text.strip()
    
    # ============ ML-BASED EXTRACTION (when available) ============
    
    def _extract_entities_ml(self, text: str) -> List[str]:
        """Extract medical entities using NER ML model"""
        try:
            entities = self.ner_pipeline(text[:512])  # Truncate for BERT
            
            # Filter and deduplicate
            medical_entities = set()
            for ent in entities:
                if ent.get('entity_group') in ['MISC', 'PERSON', 'ORG', 'LOC']:
                    word = ent.get('word', '').strip()
                    if word and len(word) > 2:  # Filter very short tokens
                        medical_entities.add(word)
            
            return sorted(list(medical_entities))[:10]  # Top 10 entities
        
        except Exception as e:
            logger.warning(f"ML entity extraction failed: {e}")
            raise
    
    def _classify_claim_type_ml(self, text: str) -> Tuple[str, float]:
        """Classify claim type using BART zero-shot classifier"""
        try:
            result = self.classifier(text[:512], self.CLAIM_TYPES, multi_class=False)
            top_label = result['labels'][0]
            confidence = float(result['scores'][0])
            
            # Ensure valid confidence
            confidence = max(0.0, min(1.0, confidence))
            
            return top_label, confidence
        
        except Exception as e:
            logger.warning(f"ML classification failed: {e}")
            raise
    
    # ============ KEYWORD-BASED FALLBACK ============
    
    def _extract_entities_keywords(self, text: str) -> List[str]:
        """Extract entities using keyword matching (fallback)"""
        entities = set()
        text_lower = text.lower()
        
        # Extract medical terms using patterns
        for claim_type, pattern in self.KEYWORD_PATTERNS.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            entities.update(matches)
        
        # Also extract multi-word phrases
        phrases = re.findall(r'\b[A-Za-z]{3,}\s+[A-Za-z]{3,}\s+[A-Za-z]{3,}\b', text)
        entities.update(phrases)
        
        return sorted(list(entities))[:10]
    
    def _classify_claim_type_keywords(self, text: str) -> Tuple[str, float]:
        """Classify claim type using keyword patterns (fallback)"""
        text_lower = text.lower()
        scores = {}
        
        for claim_type, pattern in self.KEYWORD_PATTERNS.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            scores[claim_type] = len(matches)
        
        # Find best match
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        # Calculate confidence based on matches
        total_matches = sum(scores.values())
        confidence = 0.5  # Base confidence
        
        if best_score > 0:
            confidence = 0.5 + (best_score / max(total_matches, 1)) * 0.4  # 0.5-0.9
        
        return best_type, min(confidence, 0.95)
    
    # ============ MAIN CLAIM EXTRACTION ============
    
    def _extract_main_claim(self, text: str, entities: List[str]) -> str:
        """
        Extract the most relevant claim sentence
        
        Strategy: Prefer sentences with medical entities and content
        """
        # Split into sentences
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return text[:255]
        
        # Score sentences
        best_sentence = sentences[0]
        best_score = 0
        
        for sentence in sentences:
            score = 0
            sentence_lower = sentence.lower()
            
            # Score based on entity presence
            for entity in entities:
                if entity.lower() in sentence_lower:
                    score += 2
            
            # Score based on keyword presence
            for pattern in self.KEYWORD_PATTERNS.values():
                if re.search(pattern, sentence_lower, re.IGNORECASE):
                    score += 1
            
            # Prefer longer sentences with content
            if score > best_score or (score == best_score and len(sentence) > len(best_sentence)):
                best_score = score
                best_sentence = sentence
        
        # Ensure minimum meaningful length
        if len(best_sentence) < 10:
            best_sentence = text
        
        # Truncate to max length
        return best_sentence[:255]


# Global instance
_extractor_instance: Optional[ClaimExtractor] = None

def get_claim_extractor() -> ClaimExtractor:
    """Get or create singleton instance"""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = ClaimExtractor()
    return _extractor_instance
