import numpy as np
from faster_whisper import WhisperModel
from .asr_interface import ASRInterface
from loguru import logger


class VoiceRecognition(ASRInterface):

    BEAM_SEARCH = True
    # SAMPLE_RATE # Defined in asr_interface.py

    def __init__(
        self,
        model_path: str = "distil-medium.en",
        download_root: str = None,
        language: str = None,
        device: str = "auto",
    ) -> None:
        self.MODEL_PATH = model_path
        self.LANG = language    

        logger.info(f"Initializing Faster Whisper with model: {model_path}, language: {language}")
        # Force CPU mode to avoid CUDA errors
        try:
            logger.info("Using CPU for Faster Whisper (avoiding CUDA errors)")
            self.model = WhisperModel(model_path, device="cpu", compute_type="float16", local_files_only=False)
            logger.info("Faster Whisper model initialized successfully on CPU")
        except Exception as e:
            logger.error(f"Error initializing Faster Whisper model: {e}")
            # Try with different compute type as fallback
            try:
                logger.info("Trying with int8 compute type as fallback")
                self.model = WhisperModel(model_path, device="cpu", compute_type="int8", local_files_only=False)
                logger.info("Faster Whisper model initialized successfully with int8 compute")
            except Exception as e2:
                logger.error(f"Error in fallback initialization: {e2}")
                raise

        self.asr_with_vad = None

    # Implemented in asr_interface.py
    # def transcribe_with_local_vad(self) -> str:

    def transcribe_np(self, audio: np.ndarray) -> str:
        logger.info("Transcribing audio with Faster Whisper...")
        
        try:
            segments, info = self.model.transcribe(
                audio,
                beam_size=5 if self.BEAM_SEARCH else 1,
                language=self.LANG,
                condition_on_previous_text=False,
            )

            text = [segment.text for segment in segments]
            
            if not text:
                logger.warning("No text transcribed from audio")
                return ""
            else:
                result = "".join(text)
                logger.info(f"Transcribed text: {result}")
                return result
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return ""
