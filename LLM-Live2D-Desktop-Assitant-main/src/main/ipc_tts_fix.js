// TTS Fix for ipc.js - Replace lines 282-301
// This fixes the escapedText undefined error

    return new Promise((resolve, reject) => {
      try {
        // Create a Python process to generate speech using pyttsx3TTS
        // Fix Windows path escaping issue by using raw strings
        const tempFileFixed = tempFile.replace(/\\/g, '/');
        
        // FIX: Escape text to prevent Python code injection
        const escapedText = text.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n');
        
        const pythonProcess = spawn('python', [
          '-c', 
          `
import sys
sys.path.append('${process.cwd().replace(/\\/g, '/')}')
from tts.tts_factory import TTSFactory
engine = TTSFactory.get_tts_engine("pyttsx3TTS")
# Generate audio with pyttsx3TTS
file_path = engine.generate_audio("${escapedText}", "${tempFileFixed}")
print(file_path)
          `
        ]);