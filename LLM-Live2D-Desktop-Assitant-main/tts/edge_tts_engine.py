import os
import uuid
import asyncio
from pathlib import Path
from loguru import logger
import edge_tts  # async library

DEFAULT_VOICE = "en-US-JennyNeural"

class EdgeTTSEngine:
    """
    File-based Edge TTS engine.
    synthesize(text) -> (filepath, duration_seconds)
    """
    def __init__(self, voice=DEFAULT_VOICE, rate="+0%", pitch="+0Hz", volume="+0%", style=None, out_dir="cache/tts"):
        self.voice = voice or DEFAULT_VOICE
        self.rate = rate
        self.pitch = pitch
        self.volume = volume
        self.style = style
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    async def _async_synthesize_to_file(self, text: str):
        if not text or not text.strip():
            raise ValueError("EdgeTTSEngine: empty text")

        fname = f"edge_{uuid.uuid4().hex}.mp3"
        out_path = str(self.out_dir / fname)

        kwargs = {
            "text": text,
            "voice": self.voice,
            "rate": self.rate,
            "pitch": self.pitch,
            "volume": self.volume,
        }
        
        # Only add style if it's provided and not None
        if self.style:
            kwargs["style"] = self.style

        logger.info(f"[EdgeTTS] Synth: voice={self.voice} rate={self.rate} pitch={self.pitch} volume={self.volume}")
        logger.debug(f"[EdgeTTS] Text: {text[:120]}{'...' if len(text)>120 else ''}")

        comm = edge_tts.Communicate(**kwargs)
        await comm.save(out_path)

        # Duration probing using pydub
        duration = 0.0
        try:
            from pydub import AudioSegment
            ms = len(AudioSegment.from_file(out_path))
            duration = ms / 1000.0
        except Exception as e:
            logger.warning(f"[EdgeTTS] Could not calculate duration: {e}")
            # Fallback: estimate duration based on text length (rough approximation)
            duration = max(1.0, len(text) * 0.05)  # ~50ms per character

        return out_path, duration

    def synthesize(self, text: str):
        """Sync wrapper returning (filepath, duration_seconds)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already running, create a task instead of new event loop
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._async_synthesize_to_file(text))
                    return future.result()
        except RuntimeError:
            pass
        return asyncio.run(self._async_synthesize_to_file(text))

    def generate_audio(self, text: str, file_name_no_ext=None):
        """
        Legacy interface compatibility with existing TTS engines.
        Returns filepath only for backward compatibility.
        """
        filepath, duration = self.synthesize(text)
        return filepath