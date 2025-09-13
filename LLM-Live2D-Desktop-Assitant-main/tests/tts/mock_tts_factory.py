"""
Mock TTS factory for testing purposes.
"""

from typing import Type
from tts.tts_interface import TTSInterface
from .mock_tts import MockTTSEngine


class MockTTSFactory:
    """
    A mock TTS factory that returns mock TTS engines for testing.
    """
    
    @staticmethod
    def get_tts_engine(engine_type, **kwargs) -> Type[TTSInterface]:
        """
        Get a mock TTS engine based on the engine type.
        
        Args:
            engine_type: The type of TTS engine to create
            **kwargs: Additional arguments for the TTS engine
            
        Returns:
            A mock TTS engine
        """
        # For testing purposes, we'll just return a MockTTSEngine regardless of the engine_type
        # This allows us to test the factory pattern without needing actual TTS engines
        return MockTTSEngine(voice=kwargs.get('voice'))
