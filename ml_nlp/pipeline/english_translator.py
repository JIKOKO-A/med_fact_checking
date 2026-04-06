"""
English Translator
ML/NLP Agent - Language Translation Layer
Translates native transcriptions (e.g. Darija/Arabic) to English for review
"""
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EnglishTranslator:
    """Translates text to English using local transformers model"""
    
    def __init__(self):
        """Initialize translation model"""
        self.translator = None
        
        # Try to load local transformers model
        try:
            from transformers import pipeline
            # Helsinki-NLP/opus-mt-ar-en is great for local Arabic to English
            self.translator = pipeline(
                "translation", 
                model="Helsinki-NLP/opus-mt-ar-en"
            )
            logger.info("✅ English Translator (Helsinki-NLP/opus-mt-ar-en) loaded")
        except Exception as e:
            logger.warning(f"⚠️  English Translator ML model not available: {e}. Will use mock fallback.")
            
        logger.info("✅ English Translator initialized")
        
    def translate(self, text: str) -> str:
        """
        Translate text to English
        """
        if not text or len(text.strip()) == 0:
            return ""
            
        if self.translator:
            try:
                # The model requires sentences. We can truncate if extremely long, or use as is
                # Pipeline takes input strings directly. Keep it within 512 tokens.
                truncated = text[:1500] 
                result = self.translator(truncated)
                return result[0]['translation_text']
            except Exception as e:
                logger.error(f"ML translation to English failed: {e}")
                return self._mock_translate(text)
        else:
            return self._mock_translate(text)
            
    def _mock_translate(self, text: str) -> str:
        """Mock translation for dev environments without the model downloaded"""
        # Basic mock, maybe matching some known phrases or just returning English warning
        mock_map = {
            "سميا تتالح بوايل برد فقق": "Fever can only be treated with cold water.",
            "الحمى تعالج بالماء البارد فقط": "Fever is treated with cold water only."
        }
        for k, v in mock_map.items():
            if k in text:
                return v
        
        return f"[English translation of transcription: {text[:100]}...]"

# Global instance
_english_translator_instance: Optional[EnglishTranslator] = None

def get_english_translator() -> EnglishTranslator:
    """Get or create singleton instance"""
    global _english_translator_instance
    if _english_translator_instance is None:
        _english_translator_instance = EnglishTranslator()
    return _english_translator_instance
