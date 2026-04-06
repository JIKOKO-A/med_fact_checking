"""
Darija (Moroccan Arabic) Translator
ML/NLP Agent - Language Translation Layer
Translates medical claims to Moroccan Darija in both Latin and Arabic scripts
"""
from typing import Dict
import re
import logging

logger = logging.getLogger(__name__)

class DarijaTranslator:
    """Translates text to Moroccan Darija (Latin & Arabic scripts)"""
    
    def __init__(self):
        """Initialize translation models and rules"""
        self.arabic_to_latin_map = self._build_transliteration_map()
        self.medical_terminology = self._load_medical_terms()
        logger.info("✅ Darija Translator initialized")
    
    def translate(
        self, 
        text: str,
        target_scripts: list = ["latin", "arabic"]
    ) -> Dict[str, str]:
        """
        Translate to Moroccan Darija
        Returns: {latin, arabic}
        """
        try:
            results = {}
            
            # Translate to Arabic script (traditional)
            if "arabic" in target_scripts:
                results["arabic"] = self._to_darija_arabic(text)
            
            # Translate to Latin script (Moroccan transliteration)
            if "latin" in target_scripts:
                results["latin"] = self._to_darija_latin(text)
            
            return results
        
        except Exception as e:
            logger.error(f"Darija translation failed: {e}")
            raise
    
    def _build_transliteration_map(self) -> Dict[str, str]:
        """Arabic to Latin script mappings for Darija"""
        return {
            'أ': 'a', 'ا': 'a', 'ب': 'b', 'ت': 't', 'ث': 'th',
            'ج': 'j', 'ح': '7', 'خ': 'kh', 'د': 'd', 'ذ': 'dh',
            'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'sh', 'ص': 's9',
            'ض': 'd9', 'ط': 't9', 'ظ': 'z9', 'ع': '3', 'غ': 'gh',
            'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm',
            'ن': 'n', 'ه': 'h', 'و': 'w', 'ي': 'y',
            'ة': 'a', 'ى': 'a',
            # Darija specific
            'د': 'd'
        }
    
    def _load_medical_terms(self) -> Dict[str, Dict]:
        """Medical terminology translations (Arabic → Darija)"""
        return {
            "حمى": {"latin": "smia", "darija": "سميا"},
            "الدواء": {"latin": "dwa", "darija": "دوا"},
            "الألم": {"latin": "l3am", "darija": "العام"},
            "علاج": {"latin": "3laj", "darija": "علاج"},
            "المرض": {"latin": "mrad", "darija": "مرض"},
            "اللقاح": {"latin": "lqa7", "darija": "اللقاح"},
            "الفيروس": {"latin": "virus", "darija": "فيروس"},
            "الجسم": {"latin": "jssem", "darija": "الجسم"},
            "الصحة": {"latin": "s7a", "darija": "الصحة"},
            "الطبيب": {"latin": "tbib", "darija": "الطبيب"},
            "المستشفى": {"latin": "sstf9a", "darija": "المستشفى"},
            "الدم": {"latin": "dem", "darija": "الدم"},
            "الضغط": {"latin": "d9ght", "darija": "الضغط"},
            "السكري": {"latin": "skry", "darija": "السكري"},
            "العين": {"latin": "3in", "darija": "العين"},
            "الأسنان": {"latin": "snnan", "darija": "الأسنان"},
            "المعدة": {"latin": "m3da", "darija": "المعدة"},
            "الرأس": {"latin": "ras", "darija": "الرأس"},
            "الحلق": {"latin": "l7lq", "darija": "الحلق"},
        }
    
    def _to_darija_arabic(self, text: str) -> str:
        """Convert formal MSA to Moroccan Darija (Arabic script)"""
        # Apply medical terminology first
        result = text
        for msa_term, translations in self.medical_terminology.items():
            result = result.replace(msa_term, translations["darija"])
        
        # Apply morphological rules for Darija
        result = self._apply_darija_rules(result)
        
        return result
    
    def _to_darija_latin(self, text: str) -> str:
        """Convert to Moroccan Darija Latin script (Moroccan transcription)"""
        # First convert to Darija Arabic
        darija_arabic = self._to_darija_arabic(text)
        
        # Then transliterate to Latin
        result = self._arabic_to_latin(darija_arabic)
        
        # Clean up
        result = re.sub(r'\s+', ' ', result).strip().lower()
        
        return result
    
    def _apply_darija_rules(self, text: str) -> str:
        """Apply Moroccan Darija morphological rules"""
        # Define Darija-specific transformations
        darija_rules = [
            # Remove formal markers
            (r'ال', 'ل'),  # Reduce "al-" prefix
            (r'ة$', 'ا'),  # Final "ة" to "ا"
            # Common morphological changes
            (r'ـه$', 'و'),  # Final "ه" to "و"
        ]
        
        result = text
        for pattern, replacement in darija_rules:
            result = re.sub(pattern, replacement, result)
        
        # Apply medical term substitutions
        for msa, darija_form in self.medical_terminology.items():
            result = result.replace(msa, darija_form["darija"])
        
        return result
    
    def _arabic_to_latin(self, text: str) -> str:
        """Transliterate Arabic to Latin script"""
        result = ""
        
        for char in text:
            if char in self.arabic_to_latin_map:
                result += self.arabic_to_latin_map[char]
            else:
                result += char
        
        # Post-processing
        result = re.sub(r'9', 'ss', result)  # Multiple 's' sounds
        result = re.sub(r'3', 'ayn', result)  # Ayn sound
        result = re.sub(r'7', 'h', result)  # Guttural H
        
        return result.lower()


# Global instance
_translator_instance = None

def get_darija_translator() -> DarijaTranslator:
    """Get or create singleton instance"""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = DarijaTranslator()
    return _translator_instance
