import abc
import os
import sys
from playsound3 import playsound


class TTSInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def generate_audio(self, text: str, file_name_no_ext=None) -> str:
        """
        Generate speech audio file using TTS.
        text: str
            the text to speak
        file_name_no_ext (optional and deprecated): str
            name of the file without file extension

        Returns:
        str: the path to the generated audio file

        """
        raise NotImplementedError

    def remove_file(self, filepath: str, verbose: bool = True) -> None:
        """
        Remove a file from the file system.

        This is a separate method instead of a part of the `play_audio_file_local()` because `play_audio_file_local()` is not the only way to play audio files. This method will be used to remove the audio file after it has been played.

        Parameters:
            filepath (str): The path to the file to remove.
            verbose (bool): If True, print messages to the console.
        """
        if not os.path.exists(filepath):
            print(f"File {filepath} does not exist")
            return
        try:
            print(f"Removing file {filepath}") if verbose else None
            os.remove(filepath)
        except Exception as e:
            print(f"Failed to remove file {filepath}: {e}")

    def play_audio_file_local(self, audio_file_path: str) -> None:
        """
        Play the audio file locally on this device with multiple fallback methods.
        
        audio_file_path: str
            the path to the audio file
        """
        print(f"[AUDIO FIX] Attempting to play audio file: {audio_file_path}")
        print(f"[AUDIO FIX] File exists: {os.path.exists(audio_file_path)}")
        
        if not os.path.exists(audio_file_path):
            print(f"[AUDIO FIX] ERROR: Audio file does not exist!")
            return
            
        # Method 1: Try playsound3 (original method)
        try:
            print(f"[AUDIO FIX] Method 1: Trying playsound3...")
            playsound(audio_file_path)
            print(f"[AUDIO FIX] ✓ playsound3 succeeded")
            return
        except Exception as e:
            print(f"[AUDIO FIX] ✗ playsound3 failed: {e}")
        
        # Method 2: Try pygame
        try:
            print(f"[AUDIO FIX] Method 2: Trying pygame...")
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(audio_file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            pygame.mixer.quit()
            print(f"[AUDIO FIX] ✓ pygame succeeded")
            return
        except Exception as e:
            print(f"[AUDIO FIX] ✗ pygame failed: {e}")
        
        # Method 3: Try system command
        try:
            print(f"[AUDIO FIX] Method 3: Trying system command...")
            import subprocess
            
            if sys.platform == "win32":
                # Windows: use start command
                subprocess.run(["start", "/wait", audio_file_path], shell=True, check=True)
            elif sys.platform == "darwin":
                # macOS: use afplay
                subprocess.run(["afplay", audio_file_path], check=True)
            else:
                # Linux: try multiple players
                players = ["aplay", "paplay", "mpg123", "ffplay"]
                for player in players:
                    try:
                        subprocess.run([player, audio_file_path], check=True, 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        print(f"[AUDIO FIX] ✓ {player} succeeded")
                        return
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                raise Exception("No suitable audio player found on Linux")
            
            print(f"[AUDIO FIX] ✓ System command succeeded")
            return
        except Exception as e:
            print(f"[AUDIO FIX] ✗ System command failed: {e}")
        
        # Method 4: Try winsound (Windows only)
        if sys.platform == "win32":
            try:
                print(f"[AUDIO FIX] Method 4: Trying winsound...")
                import winsound
                winsound.PlaySound(audio_file_path, winsound.SND_FILENAME)
                print(f"[AUDIO FIX] ✓ winsound succeeded")
                return
            except Exception as e:
                print(f"[AUDIO FIX] ✗ winsound failed: {e}")
        
        # If all methods fail
        print(f"[AUDIO FIX] ❌ ALL AUDIO PLAYBACK METHODS FAILED!")
        print(f"[AUDIO FIX] This explains why you can't hear the EdgeTTS audio.")
        print(f"[AUDIO FIX] Consider installing: pip install pygame")
        raise Exception("All audio playback methods failed")

    def generate_cache_file_name(self, file_name_no_ext=None, file_extension="wav"):
        """
        Generate a cross-platform cache file name.

        file_name_no_ext: str
            name of the file without extension
        file_extension: str
            file extension

        Returns:
        str: the path to the generated cache file
        """
        cache_dir = "./cache"
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        if file_name_no_ext is None:
            file_name_no_ext = "temp"

        file_name = f"{file_name_no_ext}.{file_extension}"
        return os.path.join(cache_dir, file_name)
