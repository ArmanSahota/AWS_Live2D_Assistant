"""
Mock TTS engine for testing purposes.
"""

import os
from typing import Optional

from tts.tts_interface import TTSInterface


class MockTTSEngine(TTSInterface):
    """
    A mock TTS engine that doesn't actually generate audio files,
    but simulates the behavior for testing purposes.
    """

    def __init__(self, voice: Optional[str] = None):
        """
        Initialize the mock TTS engine.

        Args:
            voice: Optional voice name to use
        """
        self.voice = voice
        self.generated_texts = []
        self.file_extension = "wav"
        self.cache_dir = "./cache"
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def generate_audio(self, text: str, file_name_no_ext=None) -> str:
        """
        Mock generating speech audio file.
        
        Args:
            text: The text to convert to speech
            file_name_no_ext: Optional file name without extension
            
        Returns:
            The path to the "generated" audio file (which isn't actually created)
        """
        # Store the text for later verification
        self.generated_texts.append(text)
        
        # Generate a file path but don't actually create the file
        file_path = self.generate_cache_file_name(file_name_no_ext, self.file_extension)
        
        # Simulate file creation by touching the file
        with open(file_path, 'w') as f:
            f.write(f"Mock audio content for: {text}")
            
        return file_path
