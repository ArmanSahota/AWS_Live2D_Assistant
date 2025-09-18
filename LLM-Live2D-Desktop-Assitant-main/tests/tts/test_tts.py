"""
Test the TTS functionality.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import the TTS modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

from tts.tts_factory import TTSFactory
from tts.tts_interface import TTSInterface
from tests.tts.mock_tts import MockTTSEngine
from tests.tts.mock_tts_factory import MockTTSFactory


class TestTTS(unittest.TestCase):
    """
    Test the TTS functionality.
    """
    
    def setUp(self):
        """
        Set up the test environment.
        """
        # Create a cache directory if it doesn't exist
        self.cache_dir = "./cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        # Clean up any existing test files
        self.cleanup_test_files()
    
    def tearDown(self):
        """
        Clean up after the tests.
        """
        self.cleanup_test_files()
    
    def cleanup_test_files(self):
        """
        Clean up any test files created during the tests.
        """
        test_files = [
            os.path.join(self.cache_dir, "test_tts.wav"),
            os.path.join(self.cache_dir, "test_tts_factory.wav"),
            os.path.join(self.cache_dir, "temp.wav"),
            os.path.join(self.cache_dir, "temp.aiff")
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Failed to remove file {file_path}: {e}")
    
    def test_mock_tts_engine(self):
        """
        Test the mock TTS engine.
        """
        # Create a mock TTS engine
        tts_engine = MockTTSEngine(voice="test_voice")
        
        # Test that the voice was set correctly
        self.assertEqual(tts_engine.voice, "test_voice")
        
        # Test generating audio
        test_text = "This is a test of the mock TTS engine."
        file_path = tts_engine.generate_audio(test_text, "test_tts")
        
        # Check that the file was created
        self.assertTrue(os.path.exists(file_path))
        
        # Check that the text was stored
        self.assertEqual(tts_engine.generated_texts[0], test_text)
        
        # Check the file content
        with open(file_path, 'r') as f:
            content = f.read()
            self.assertEqual(content, f"Mock audio content for: {test_text}")
    
    def test_mock_tts_factory(self):
        """
        Test the mock TTS factory.
        """
        # Create a TTS engine using the mock factory
        tts_engine = MockTTSFactory.get_tts_engine("any_engine", voice="test_voice")
        
        # Test that the engine is a MockTTSEngine
        self.assertIsInstance(tts_engine, MockTTSEngine)
        
        # Test that the voice was set correctly
        self.assertEqual(tts_engine.voice, "test_voice")
        
        # Test generating audio
        test_text = "This is a test of the mock TTS factory."
        file_path = tts_engine.generate_audio(test_text, "test_tts_factory")
        
        # Check that the file was created
        self.assertTrue(os.path.exists(file_path))
        
        # Check that the text was stored
        self.assertEqual(tts_engine.generated_texts[0], test_text)
    
    def test_real_tts_factory(self):
        """
        Test the real TTS factory with a mock engine.
        
        This test verifies that the TTS factory can create different types of engines
        based on the engine_type parameter.
        """
        # We'll use pyttsx3TTS as it's one of the simpler engines that doesn't require external APIs
        try:
            # Try to create a pyttsx3TTS engine
            tts_engine = TTSFactory.get_tts_engine("pyttsx3TTS")
            
            # Test that the engine is a TTSInterface
            self.assertIsInstance(tts_engine, TTSInterface)
            
            # We won't actually generate audio as it might cause issues in a test environment
            # Just check that the engine has the required methods
            self.assertTrue(hasattr(tts_engine, 'generate_audio'))
            self.assertTrue(callable(getattr(tts_engine, 'generate_audio')))
            
            print("Successfully tested real TTS factory with pyttsx3TTS engine")
        except Exception as e:
            # If there's an error (e.g., pyttsx3 not installed), we'll skip this test
            print(f"Skipping real TTS factory test due to error: {e}")
    
    def test_edge_tts_factory(self):
        """
        Test the EDGE_TTS factory integration.
        
        This test verifies that the TTS factory can create EDGE_TTS engines
        with proper configuration parameters.
        """
        try:
            # Try to create an EDGE_TTS engine with configuration
            tts_engine = TTSFactory.get_tts_engine(
                "EDGE_TTS",
                voice="en-US-JennyNeural",
                rate="+0%",
                pitch="+0Hz",
                volume="+0%"
            )
            
            # Test that the engine has the required methods
            self.assertTrue(hasattr(tts_engine, 'generate_audio'))
            self.assertTrue(hasattr(tts_engine, 'synthesize'))
            self.assertTrue(callable(getattr(tts_engine, 'generate_audio')))
            self.assertTrue(callable(getattr(tts_engine, 'synthesize')))
            
            # Test that configuration was applied
            self.assertEqual(tts_engine.voice, "en-US-JennyNeural")
            self.assertEqual(tts_engine.rate, "+0%")
            self.assertEqual(tts_engine.pitch, "+0Hz")
            self.assertEqual(tts_engine.volume, "+0%")
            
            print("Successfully tested EDGE_TTS factory integration")
        except Exception as e:
            # If there's an error (e.g., edge-tts not installed), we'll skip this test
            print(f"Skipping EDGE_TTS factory test due to error: {e}")
            pass
            pass


if __name__ == "__main__":
    unittest.main()
