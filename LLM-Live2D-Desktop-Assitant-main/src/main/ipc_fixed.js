// Fixed generateSpeech function section - lines 291-304
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