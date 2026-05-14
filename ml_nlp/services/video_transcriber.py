"""
Video Transcription Service
ML/NLP Agent - Audio Processing Layer
Transcribes video/audio to text using Whisper
"""
from typing import Dict, Optional
import os
import logging

logger = logging.getLogger(__name__)

class VideoTranscriber:
    """Transcribe video/audio files using OpenAI Whisper"""
    
    def __init__(self, model_size: str = "medium"):
        """Initialize Whisper model"""
        try:
            import whisper
            self.model = whisper.load_model(model_size)
            self.model_size = model_size
            logger.info(f"✅ Whisper {model_size} model loaded (Premium Quality)")
        except ImportError:
            logger.error("Whisper not installed. Install with: pip install openai-whisper")
            raise
    
    def transcribe(
        self,
        video_path: str,
        language: Optional[str] = None
    ) -> Dict:
        """
        Transcribe video/audio file
        Returns: {text, language, duration, segments}
        """
        try:
            # Validate file exists
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"File not found: {video_path}")
            
            # Extract audio from video if needed
            audio_path = self._extract_audio_if_needed(video_path)
            
            # Transcription prompt centered on Darija and medical advice
            # This helps Whisper understand the context and accent better
            darija_prompt = (
                "Hada vidyo dyal n-nasa'ih t-ti-ibbiya f l-Maghrib bi-d-darija. "
                "The following is medical advice in Moroccan Darija Arabic. "
                "It contains health claims and doctors speaking."
            )
            
            # Transcribe with improved parameters
            result = self.model.transcribe(
                audio_path,
                language=language or "ar",
                verbose=False,
                initial_prompt=darija_prompt,
                fp16=False # Ensure CPU compatibility
            )
            
            # Clean up extracted audio
            if audio_path != video_path and os.path.exists(audio_path):
                os.remove(audio_path)
            
            return {
                "text": result["text"],
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", []),
                "duration": result.get("duration", 0),
                "confidence": self._estimate_confidence(result)
            }
        
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    def _extract_audio_if_needed(self, file_path: str) -> str:
        """Extract audio from video file if needed"""
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv']
        audio_extensions = ['.mp3', '.wav', '.m4a', '.aac']
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # If already audio, return as-is
        if file_ext in audio_extensions:
            return file_path
        
        # Extract audio from video
        if file_ext in video_extensions:
            try:
                from moviepy.editor import VideoFileClip
                audio_path = file_path.replace(file_ext, '.wav')
                
                video = VideoFileClip(file_path)
                video.audio.write_audiofile(audio_path, verbose=False, logger=None)
                video.close()
                
                return audio_path
            
            except ImportError:
                logger.error("MoviePy not installed. Install with: pip install moviepy")
                raise
        
        raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _estimate_confidence(self, transcription_result: dict) -> float:
        """Estimate transcription confidence"""
        # Simple heuristic: based on no_speech_prob if available
        no_speech_prob = transcription_result.get("no_speech_prob", 0.0)
        return max(0.0, 1.0 - no_speech_prob)


class AudioProcessor:
    """Process audio for medical claim extraction"""
    
    def __init__(self):
        self.transcriber = VideoTranscriber()
    
    def process_video(self, video_path: str, language: Optional[str] = None) -> Dict:
        """
        Process video: transcribe → extract claims
        """
        # Transcribe
        transcription = self.transcriber.transcribe(video_path, language)
        
        # Extract claims from transcription
        from ml_nlp.pipeline.claim_extractor_v2 import get_claim_extractor
        extractor = get_claim_extractor()
        
        claims = []
        for segment in transcription.get("segments", []):
            text = segment.get("text", "")
            if len(text) > 10:
                try:
                    claim_data = extractor.extract(text, language)
                    claim_data["timestamp"] = {
                        "start": segment.get("start", 0),
                        "end": segment.get("end", 0)
                    }
                    claims.append(claim_data)
                except Exception as e:
                    logger.warning(f"Failed to extract claim from segment: {e}")
        
        return {
            "video_path": video_path,
            "transcription": transcription["text"],
            "language": transcription["language"],
            "claims": claims,
            "total_duration": transcription["duration"],
            "transcription_confidence": transcription["confidence"]
        }


# Global instances
_transcriber_instance = None

def get_transcriber() -> VideoTranscriber:
    """Get or create singleton instance"""
    global _transcriber_instance
    if _transcriber_instance is None:
        _transcriber_instance = VideoTranscriber()
    return _transcriber_instance
