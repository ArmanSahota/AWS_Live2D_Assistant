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
        
        # Enhanced diagnostic logging
        print(f"\n[ASR DIAGNOSTIC] Input audio shape: {audio.shape}")
        print(f"[ASR DIAGNOSTIC] Input audio dtype: {audio.dtype}")
        print(f"[ASR DIAGNOSTIC] Audio length: {len(audio)} samples ({len(audio)/16000:.2f} seconds)")
        
        if len(audio) > 0:
            audio_min = np.min(audio)
            audio_max = np.max(audio)
            audio_mean = np.mean(audio)
            audio_std = np.std(audio)
            
            print(f"[ASR DIAGNOSTIC] Audio stats - Min: {audio_min:.4f}, Max: {audio_max:.4f}")
            print(f"[ASR DIAGNOSTIC] Audio stats - Mean: {audio_mean:.4f}, Std: {audio_std:.4f}")
            
            # Check for common audio issues
            zero_count = np.sum(audio == 0)
            if zero_count > len(audio) * 0.9:
                print(f"[ASR DIAGNOSTIC] WARNING: Audio is mostly silent ({zero_count}/{len(audio)} zeros)")
                
            if audio_max - audio_min < 0.01:
                print(f"[ASR DIAGNOSTIC] WARNING: Very low audio dynamic range")
                
            # Check sample rate assumptions
            if len(audio) < 1600:  # Less than 0.1 seconds at 16kHz
                print(f"[ASR DIAGNOSTIC] WARNING: Audio too short for reliable transcription")
        else:
            print(f"[ASR DIAGNOSTIC] ERROR: Empty audio array")
            return ""
        
        try:
            print(f"[ASR DIAGNOSTIC] Starting Whisper transcription...")
            segments, info = self.model.transcribe(
                audio,
                beam_size=5 if self.BEAM_SEARCH else 1,
                language=self.LANG,
                condition_on_previous_text=False,
            )
            
            print(f"[ASR DIAGNOSTIC] Transcription info: {info}")
            
            text_segments = []
            for i, segment in enumerate(segments):
                confidence = getattr(segment, 'avg_logprob', 'N/A')
                print(f"[ASR DIAGNOSTIC] Segment {i}: '{segment.text}' (confidence: {confidence})")
                text_segments.append(segment.text)
            
            if not text_segments:
                print(f"[ASR DIAGNOSTIC] WARNING: No text segments generated")
                logger.warning("No text transcribed from audio")
                return ""
            else:
                result = "".join(text_segments)
                print(f"[ASR DIAGNOSTIC] Final transcription: '{result}'")
                logger.info(f"Transcribed text: {result}")
                return result
                
        except Exception as e:
            print(f"[ASR DIAGNOSTIC] Transcription error: {e}")
            logger.error(f"Error transcribing audio: {e}")
            import traceback
            traceback.print_exc()
            return ""
