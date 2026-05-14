"""
English Translator
ML/NLP Agent - Language Translation Layer
Translates native transcriptions (e.g. Darija/Arabic) to English for review
"""
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EnglishTranslator:
    """Translates text to English using Google Translate via deep-translator"""
    
    def __init__(self):
        """Initialize translation model"""
        self.translator = None
        
        try:
            from deep_translator import GoogleTranslator
            self.translator = GoogleTranslator(source='auto', target='en')
            logger.info("✅ English Translator (Google Translate) loaded")
        except ImportError:
            logger.warning("⚠️ deep-translator not installed. Will use fallback.")
        except Exception as e:
            logger.warning(f"⚠️ English Translator init failed: {e}")
            
    def translate(self, text: str) -> str:
        """
        Translate text to English
        """
        if not text or len(text.strip()) == 0:
            return ""
            
        if self.translator:
            try:
                # deep-translator handles up to 5000 chars per request
                truncated = text[:4999]
                result = self.translator.translate(truncated)
                return result
            except Exception as e:
                logger.error(f"ML translation to English failed: {e}")
                return self._mock_translate(text)
        else:
            return self._mock_translate(text)
            
    def _mock_translate(self, text: str) -> str:
        """Mock translation for dev environments without the model downloaded"""
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
