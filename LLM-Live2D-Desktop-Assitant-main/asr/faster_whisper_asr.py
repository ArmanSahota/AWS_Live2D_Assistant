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
        compute_type: str = None,
    ) -> None:
        # Validate model_path
        if model_path is None:
            logger.warning("model_path is None, using default 'base'")
            model_path = "base"
            
        self.MODEL_PATH = model_path
        self.LANG = language    

        logger.info(f"Initializing Faster Whisper with model: {model_path}, language: {language}")
        
        # Determine compute type based on device
        if compute_type is None:
            compute_type = "int8"  # Default to int8 for CPU compatibility
            logger.info(f"No compute_type specified, defaulting to {compute_type}")
        
        # Force CPU mode to avoid CUDA errors
        try:
            logger.info(f"Using CPU for Faster Whisper with compute_type={compute_type}")
            self.model = WhisperModel(
                model_size_or_path=model_path, 
                device="cpu", 
                compute_type=compute_type, 
                download_root=download_root,
                local_files_only=False
            )
            logger.info("Faster Whisper model initialized successfully on CPU")
        except Exception as e:
            logger.error(f"Error initializing Faster Whisper model: {e}")
            # Try with different compute type as fallback
            fallback_compute = "float32" if compute_type != "float32" else "int8"
            try:
                logger.info(f"Trying with {fallback_compute} compute type as fallback")
                self.model = WhisperModel(
                    model_size_or_path=model_path, 
                    device="cpu", 
                    compute_type=fallback_compute,
                    download_root=download_root,
                    local_files_only=False
                )
                logger.info(f"Faster Whisper model initialized successfully with {fallback_compute} compute")
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
