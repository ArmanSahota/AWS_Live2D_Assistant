from pywhispercpp.model import Model
import logging
import numpy as np
from .asr_interface import ASRInterface

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("WhisperCPP_ASR")

class VoiceRecognition(ASRInterface):

    def __init__(
        self,
        model_name: str = "base",
        model_dir="asr/models",
        language: str = "en",
        print_realtime=False,
        print_progress=False,
        **kwargs
    ) -> None:
        logger.info(f"Initializing WhisperCPP with model: {model_name}, language: {language}")
        
        self.model = Model(
            model=model_name,
            models_dir=model_dir,
            language=language,
            print_realtime=print_realtime,
            print_progress=print_progress,
            **kwargs
        )
        self.asr_with_vad = None
        logger.info("WhisperCPP model initialized successfully")

    # Implemented in asr_interface.py
    # def transcribe_with_local_vad(self) -> str:

    def transcribe_np(self, audio: np.ndarray) -> str:
        logger.info(f"Starting transcription with WhisperCPP, audio length: {len(audio)}")
        
        # Define a callback to log each segment as it's transcribed
        def segment_callback(segment):
            logger.info(f"Transcribed segment: {segment.text}")
            # Send a ping to track data flow
            logger.info(f"PATH_PING: WhisperCPP -> transcription -> {segment.text}")
            return segment
        
        segments = self.model.transcribe(audio, new_segment_callback=segment_callback)
        full_text = ""
        for segment in segments:
            full_text += segment.text
        
        logger.info(f"Full transcription: {full_text}")
        return full_text
