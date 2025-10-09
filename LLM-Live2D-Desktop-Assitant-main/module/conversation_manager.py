import threading
import queue
import random
import numpy as np
import os
import json
import uuid
from typing import Iterator
import asyncio
import platform
import time
from .computer_utils import get_clipboard_content, copy_selected_content, input_text as utils_input_text
if platform.system() == 'Darwin':
    from .computer_utils import control_computer as utils_control_computer
import re

class ConversationManager:
    def __init__(self, config, llm, asr, tts, live2d, translator, audio_manager, interrupt_manager, claude_api_key = None, verbose=False, loop=None):
        self.config = config
        self.llm = llm
        self.asr = asr
        self.tts = tts
        self.live2d = live2d
        self.translator = translator
        self.audio_manager = audio_manager
        self.interrupt_manager = interrupt_manager
        self.claude_api_key = claude_api_key
        self.loop = loop
        assert self.loop is not None, "loop is None"
        self.verbose = verbose
        self.heard_sentence = ""
        # self.functions = self.get_tool_functions()
        
    def get_prompt_and_image(self, user_input: str | np.ndarray | None = None, clipboard_data: dict | None = None) -> tuple[str, str | None]:
        image_base64 = None
        
        if clipboard_data:
            if "text" in clipboard_data:
                user_input += f"\nThe text from my clipboard (between two delimiter):###\n{clipboard_data['text']}###\n"
            
            if "image" in clipboard_data:
                image_base64 = clipboard_data["image"]
                
        return user_input, image_base64
        

    def conversation_chain(self, user_input=None, clipboard_data=None):
        if not self.interrupt_manager.wait_continue_flag(): 
            print(
                ">> Execution flag not set. In interruption state for too long. Exiting     conversation chain."
            )
            raise InterruptedError(
                "Conversation chain interrupted. Wait flag timeout reached."
            )

        color_code = random.randint(0, 3)
        c = [None] * 4
        c[0] = "\033[91m"
        c[1] = "\033[94m"
        c[2] = "\033[92m"
        c[3] = "\033[0m"

        print(f"{c[color_code]}New Conversation Chain started!")

        if user_input is None:
            user_input = self.get_user_input()
        elif isinstance(user_input, np.ndarray):
            print("transcribing...")
            user_input = self.asr.transcribe_np(user_input)

        if user_input.strip().lower() == self.config.get("EXIT_PHRASE", "exit").lower():
            print("Exiting...")
            exit()

        print(f"User input: {user_input}")

        prompt, image_base64 = self.get_prompt_and_image(user_input, clipboard_data)
        print(f"[CONVERSATION DEBUG] Got prompt: {prompt[:100]}...")
        
        # Add RAG context for manufacturing/technical queries
        print(f"[CONVERSATION DEBUG] Enhancing prompt with RAG...")
        enhanced_prompt = self._enhance_prompt_with_rag(prompt, user_input)
        print(f"[CONVERSATION DEBUG] Enhanced prompt length: {len(enhanced_prompt)} chars")
        
        print(f"[CONVERSATION DEBUG] Calling LLM chat_iter...")
        chat_completion: Iterator[str] = self.llm.chat_iter(enhanced_prompt, image_base64)
        print(f"[CONVERSATION DEBUG] Got chat_completion iterator")

        if not self.config.get("TTS_ON", False):
            full_response = ""
            for char in chat_completion:
                if self.interrupt_manager.in_interrupt():
                    self.interrupt_manager.interrupt_post_processing()
                    print("\nInterrupted!")
                    return None
                full_response += char
                print(char, end="")
            return full_response

        full_response = self.speak(chat_completion, user_input)
        if self.verbose:
            print(f"\nComplete response: [\n{full_response}\n]")

        print(f"{c[color_code]}Conversation completed.")
        return full_response

    def _enhance_prompt_with_rag(self, prompt: str, user_input: str) -> str:
        """
        Enhance the prompt with RAG context if relevant keywords are detected
        """
        # Check if RAG is available by trying to import the function
        try:
            from server import load_rag_context_for_vision
            rag_available = True
            print(f"[CONVERSATION RAG] RAG system available, proceeding with enhancement")
        except ImportError as e:
            print(f"[CONVERSATION RAG] RAG system not available: {e}, skipping enhancement")
            return prompt
        
        # Keywords that trigger RAG enhancement
        rag_keywords = [
            'error', 'e001', 'e002', 'e003', 'malfunction', 'troubleshoot', 'repair',
            'manufacturing', 'equipment', 'machine', 'safety', 'procedure', 'manual',
            'knowledge base', 'documentation', 'help', 'how to', 'what is'
        ]
        
        # Check if user input contains RAG-relevant keywords
        user_lower = user_input.lower()
        should_enhance = any(keyword in user_lower for keyword in rag_keywords)
        
        if should_enhance:
            try:
                print(f"[CONVERSATION RAG] Detected relevant query, enhancing with KB context")
                # RAG function already imported above
                rag_context = load_rag_context_for_vision(user_input, "")
                
                if rag_context and len(rag_context) > 50:
                    enhanced_prompt = f"""You are a manufacturing assistant with access to a comprehensive knowledge base.

{rag_context}

Based on the above knowledge base information and your general knowledge, please respond to: {prompt}

If the knowledge base contains relevant information, use it in your response. If not, provide general guidance while mentioning that specific documentation might be helpful."""
                    
                    print(f"[CONVERSATION RAG] Enhanced prompt with {len(rag_context)} characters of context")
                    return enhanced_prompt
                else:
                    print(f"[CONVERSATION RAG] No relevant context found in KB")
            except Exception as e:
                print(f"[CONVERSATION RAG] Error enhancing prompt: {e}")
        
        return prompt

    def get_user_input(self) -> str:
        if self.config.get("VOICE_INPUT_ON", False):
            print("Listening from the microphone...")
            return self.asr.transcribe_with_local_vad()
        else:
            return input("\n>> ")

    def speak(self, chat_completion: Iterator[str], user_input: str) -> str:
        print(f"[CONVERSATION TTS DEBUG] speak() method called")
        print(f"[CONVERSATION TTS DEBUG] - Input source: Normal conversation (not vision analysis)")
        print(f"[CONVERSATION TTS DEBUG] - TTS enabled: {self.config.get('TTS_ON', False)}")
        print(f"[CONVERSATION TTS DEBUG] - Will generate audio and play through speakers")
        
        full_response = ""
        if self.config.get("SAY_SENTENCE_SEPARATELY", True):
            full_response = self.speak_by_sentence_chain(
                chat_completion, user_input
            )
        else:
            full_response = ""
            for char in chat_completion:
                if self.interrupt_manager.in_interrupt():
                    print("\nInterrupted!")
                    self.interrupt_manager.interrupt_post_processing()
                    return None
                print(char, end="")
                full_response += char
            print("\n")
            
            if self.live2d:
                tts_target_sentence = self.live2d.remove_emotion_keywords(full_response[0])
            else:
                tts_target_sentence = full_response[0]
                
            if self.translator and self.config.get("TRANSLATE_AUDIO", False):
                print("Translating...")
                tts_target_sentence = self.translator.translate(tts_target_sentence)
                print(f"Translated: {tts_target_sentence}")

            filename = self.audio_manager.generate_audio_file(tts_target_sentence, "temp")

            if self.interrupt_manager.in_interrupt():
                self.audio_manager.play_audio_file(
                    sentence=full_response,
                    filepath=filename,
                    instrument_filepath=None
                )
            else:
                self.interrupt_manager.interrupt_post_processing()

        return full_response

    def speak_by_sentence_chain(self, chat_completion: Iterator[str], user_input: str) -> str:
        full_response = [""]

        sentence_queue = queue.Queue()
        audio_queue = queue.Queue()
        index = 0

        def producer_worker():
            nonlocal index
            try:
                sentence_buffer = ""
                for char in chat_completion:
                    if self.interrupt_manager.in_interrupt():
                        self.interrupt_manager.interrupt_post_processing()
                        print("Producer interrupted")
                        return None
                    
                    if char:
                        print(char, end="", flush=True)
                        sentence_buffer += char
                        full_response[0] += char
                        check_result = self.check(sentence_buffer)
                        if check_result == "sing-song":
                            match = re.search(r'\{.*?\}', sentence_buffer)
                            if match:
                                self.sing_song(match.group(0))
                                sentence_buffer = re.sub(r'\{.*?\}', '', sentence_buffer)
                            else:
                                print("Invalid JSON format in sing mode")
                        # elif check_result == "computer-control":
                        #     match = re.search(r'\{.*?\}', sentence_buffer)
                        #     if match:
                        #         future = asyncio.run_coroutine_threadsafe(
                        #             self.control_computer(match.group(0)),
                        #             self.loop
                        #         )
                        #         try:
                        #             _ = future.result() 
                        #         except Exception as e:
                        #             print(f"Error running control_computer coroutine: {e}")
                        #         sentence_buffer = re.sub(r'\{.*?\}', '', sentence_buffer)
                        #     else:
                        #         print("Invalid JSON format in computer control mode")
                        # elif check_result == "input-text":
                        #     match = re.search(r'\[text_input_start\](.*?)\[text_input_end\]', sentence_buffer, re.DOTALL)
                        #     if match:
                        #         text_to_input = match.group(1)
                        #         self.input_text(text_to_input)
                        #         sentence_buffer = ""
                        #     else:
                        #         match = re.search(r'\[text_input_start\](.*)', sentence_buffer, re.DOTALL)
                        #         if match:
                        #             text_to_input = match.group(1)
                        #             self.input_text(text_to_input)
                        #             sentence_buffer = "[text_input_start]"
                        elif check_result:
                            if self.verbose:
                                print("\n")
                            if self.interrupt_manager.in_interrupt():
                                self.interrupt_manager.interrupt_post_processing()
                                print("Producer interrupted")
                                return None
                            sentence_queue.put((index, sentence_buffer))
                            index += 1
                            sentence_buffer = ""

                if sentence_buffer:
                    if self.interrupt_manager.in_interrupt():
                        self.interrupt_manager.interrupt_post_processing()
                        print("Producer interrupted")
                        return None
                    print("\n")
                    sentence_queue.put((index, sentence_buffer))
                    index += 1

            except Exception as e:
                print(
                    f"Producer error: Error processing sentence.\n{e}",
                    "Producer stopped\n",
                )
                return
            finally:
                sentence_queue.put((None, None))

        def tts_worker():
            try:
                while True:
                    if self.interrupt_manager.in_interrupt():
                        self.interrupt_manager.interrupt_post_processing()
                        print("TTS worker interrupted")
                        return None
                    idx, sentence = sentence_queue.get()
                    if idx is None:
                        sentence_queue.put((None, None))
                        break

                    if self.live2d:
                        tts_target_sentence = self.live2d.remove_emotion_keywords(sentence)
                    else:
                        tts_target_sentence = sentence

                    if self.translator and self.config.get("TRANSLATE_AUDIO", False):
                        try:
                            print("Translating...")
                            tts_target_sentence = self.translator.translate(tts_target_sentence)
                            print(f"Translated: {tts_target_sentence}")
                        except Exception as e:
                            print(f"Error translating: {e}")
                            print(f"Text: {tts_target_sentence}")
                            print("Skipping...")

                    audio_filepath = self.audio_manager.generate_audio_file(
                        tts_target_sentence, file_name_no_ext=f"temp-{idx}"
                    )

                    if self.interrupt_manager.in_interrupt():
                        self.interrupt_manager.interrupt_post_processing()
                        print("TTS worker interrupted")
                        return None

                    audio_info = {
                        "index": idx,
                        "sentence": sentence,
                        "audio_filepath": audio_filepath,
                    }
                    audio_queue.put(audio_info)
            except Exception as e:
                print(
                    f"TTS worker error: Error generating audio for sentence.\n{e}",
                    "TTS worker stopped\n",
                )
                return
            finally:
                audio_queue.put(None)  

        def consumer_worker():
            expected_index = 0
            audio_buffer = {}
            self.heard_sentence = ""
            try:
                while True:
                    if self.interrupt_manager.in_interrupt():
                        self.interrupt_manager.interrupt_post_processing()
                        print("Consumer interrupted")
                        return None
                    audio_info = audio_queue.get()
                    if audio_info is None:
                        break

                    if audio_info:
                        self.heard_sentence += audio_info["sentence"]
                    idx = audio_info["index"]
                    audio_buffer[idx] = audio_info

                    while expected_index in audio_buffer:
                        info = audio_buffer.pop(expected_index)
                        if self.verbose:
                            print("\n")
                        self.audio_manager.play_audio_file(
                            sentence=info["sentence"],
                            filepath=info["audio_filepath"],
                            instrument_filepath=None
                        )
                        expected_index += 1

            except Exception as e:
                print(
                    f"Consumer error: Error playing audio.\n{e}",
                    "Consumer stopped\n",
                )
                return

        producer_thread = threading.Thread(target=producer_worker)
        tts_thread = threading.Thread(target=tts_worker)
        consumer_thread = threading.Thread(target=consumer_worker)

        producer_thread.start()
        tts_thread.start()
        consumer_thread.start()

        producer_thread.join()
        tts_thread.join()
        consumer_thread.join()

        return full_response[0]
    

    def check(self, text: str):
        """
        Check if the text contains a tool call / is the end of a sentence.
        """
        if ("sing_song" in text and "}" in text): 
            return "sing-song"
        
        # if ("computer_control" in text and "}" in text):
        #     return "computer-control"
        # if ("[text_input_start]" in text):
        #     return False if text.count('[') >= 2 and text.count(']') < 2 else "input-text"

        white_list = ["...", "Dr.", "Mr.", "Ms.", "Mrs.", "Jr.", "Sr.", "St.", "Ave.", "Rd.", 
                     "Blvd.", "Dept.", "Univ.", "Prof.", "Ph.D.", "M.D.", "U.S.", "U.K.", 
                     "U.N.", "E.U.", "U.S.A.", "U.K.", "U.S.S.R.", "U.A.E."]
        
        if any(text.strip().endswith(item) for item in white_list): 
            return False

        punctuation_blacklist = [".", "?", "!", "。", "；", "？", "！", "…", "〰", "〜", "～", "！"]
        return any(text.strip().endswith(punct) for punct in punctuation_blacklist)  # and not "sing_song" in text and not "computer_control" in text and not "input_text" in text

    def sing_song(self, sentence):
        print("sing mode activated")
        try:
            data = json.loads(sentence)
            song_name = data.get("song_name")
        except json.JSONDecodeError:
            print("Invalid JSON format in response")
            return

        if not song_name:
            self.audio_manager.play_text("This song, even I have yet to master.")
            return

        converted_vocal_path = os.path.join('./sing/converted_vocal', f'{song_name}.wav')
        instrument_path = os.path.join('./sing/instrument', f'{song_name}.wav')

        if not os.path.exists(converted_vocal_path) or not os.path.exists(instrument_path):
            self.audio_manager.play_text("This song, even I have yet to master.")
            return

        self.audio_manager.play_text(f"Please enjoy {song_name}")

        self.audio_manager.play_audio_file(
            sentence = song_name,
            filepath=converted_vocal_path,
            instrument_filepath = instrument_path
        )     
        
    # async def control_computer(self, sentence):
    #     print("computer control mode activated")
        
    #     if platform.system() != 'Darwin':
    #         self.audio_manager.play_text("This system is currently not supported.")
    #         return
        
    #     try:
    #         data = json.loads(sentence)
    #         instruction = data.get("computer_control")
    #     except json.JSONDecodeError:
    #         print("Invalid JSON format in response")
    #         return
        
    #     print("computer control mode activated")
        
    #     async def api_response_callback(response):
    #         data = json.loads(response.text)["content"]
    #         # print(json.dumps(data, indent=4))
            
    #         for item in data:
    #             if item["type"] == "text":
    #                 text = item["text"]
    #                 print(text)
    #                 self.audio_manager.play_text(text)
        
    #     await utils_control_computer(self.claude_api_key, instruction, api_response_callback)
        
    # def input_text(self, text):
    #     # print("input text mode activated")
    #     utils_input_text(text)
        
    # def get_tool_functions(self):
    #     return {
    #         "sing_song" : self.sing_song,
    #         "control_computer" : self.control_computer
    #     }
        
    # def call_tool_function(self, function_name, *args):
    #     if function_name in self.functions:
    #         self.functions[function_name](*args)
    #     else:
    #         print(f"Function {function_name} not found")
    
