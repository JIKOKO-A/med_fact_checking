"""
Claim Extraction Pipeline
ML/NLP Agent - NLP Processing Layer
Extracts medical claims from text using transformers
"""
from typing import Dict, List, Tuple
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import logging

logger = logging.getLogger(__name__)

class ClaimExtractor:
    """Extract and classify medical claims from text"""
    
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
    
    def __init__(self):
        """Initialize models for claim extraction"""
        # Zero-shot classification for general claim detection
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0  # GPU if available
        )
        
        # NER model for medical entity recognition
        self.ner_pipeline = pipeline(
            "token-classification",
            model="dslim/bert-base-multilingual-cased-ner",
            aggregation_strategy="simple"
        )
        
        logger.info("✅ Claim Extractor initialized")
    
    def extract(
        self, 
        text: str, 
        language: str = "ar"
    ) -> Dict:
        """
        Extract claims from text
        Returns: {claim, claim_type, entities, confidence}
        """
        try:
            # Clean text
            text = self._clean_text(text)
            
            if len(text) < 10:
                raise ValueError("Text too short for claim extraction")
            
            # Extract entities (health-related terms)
            entities = self._extract_entities(text)
            
            # Classify claim type
            claim_type, type_confidence = self._classify_claim_type(text)
            
            # Summarize/identify main claim
            main_claim = self._extract_main_claim(text, entities)
            
            return {
                "claim": main_claim,
                "claim_type": claim_type,
                "entities": entities,
                "type_confidence": type_confidence,
                "original_language": language,
                "original_text": text
            }
        
        except Exception as e:
            logger.error(f"Claim extraction failed: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = " ".join(text.split())
        # Remove URLs
        import re
        text = re.sub(r'http\S+|www\S+', '', text)
        return text.strip()
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract medical entities using NER"""
        try:
            entities = self.ner_pipeline(text[:512])  # Truncate for BERT
            
            # Filter and deduplicate
            medical_entities = set()
            for ent in entities:
                if ent['entity_group'] in ['MISC', 'PERSON', 'ORG']:
                    medical_entities.add(ent['word'].strip())
            
            return list(medical_entities)[:10]  # Top 10 entities
        
        except Exception as e:
            logger.warning(f"Entity extraction failed: {e}")
            return []
    
    def _classify_claim_type(self, text: str) -> Tuple[str, float]:
        """Classify the type of medical claim"""
        try:
            result = self.classifier(text[:512], self.CLAIM_TYPES, multi_class=False)
            top_label = result['labels'][0]
            confidence = float(result['scores'][0])
            return top_label, confidence
        
        except Exception as e:
            logger.warning(f"Claim type classification failed: {e}")
            return "general_health", 0.5
    
    def _extract_main_claim(self, text: str, entities: List[str]) -> str:
        """Extract the main claim from text"""
        # Strategy: Find sentences with most medical entities
        sentences = text.split('.')
        
        best_sentence = ""
        max_entities = 0
        
        for sent in sentences:
            entity_count = sum(1 for ent in entities if ent.lower() in sent.lower())
            if entity_count > max_entities:
                max_entities = entity_count
                best_sentence = sent.strip()
        
        # If no sentence with entities, use first meaningful sentence
        if not best_sentence:
            best_sentence = sentences[0].strip() if sentences else text
        
        # Remove duplicates and return
        return best_sentence[:255] if best_sentence else text[:255]


# Global instance
_extractor_instance = None

def get_claim_extractor() -> ClaimExtractor:
    """Get or create singleton instance"""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = ClaimExtractor()
    return _extractor_instance
