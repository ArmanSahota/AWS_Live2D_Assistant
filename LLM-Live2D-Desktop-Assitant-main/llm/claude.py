import requests
import json
from typing import Iterator, Dict, List, Any, Union
from .llm_interface import LLMInterface

class LLM(LLMInterface):
    def __init__(
        self,
        system: str = None,
        base_url: str = None,
        model: str = "claude-3-haiku-20240307",
        llm_api_key: str = None,  # Not needed for AWS endpoint but kept for compatibility
        verbose: bool = False,
    ):
        """
        Initialize Claude LLM using AWS HTTP endpoint.
        
        Args:
            system (str): System prompt
            base_url (str): Base URL for AWS HTTP endpoint
            model (str): Model name (for reference only, actual model is set in AWS)
            llm_api_key (str): Not used with AWS endpoint, kept for compatibility
            verbose (bool): Whether to print debug info
        """
        self.system = self._enhance_system_prompt(system) if system else None
        self.model = model
        self.verbose = verbose
        self.base_url = base_url
        
        if self.verbose:
            print(f"Initialized Claude LLM with AWS HTTP endpoint: {base_url}")
        
        # Store conversation history (excluding system prompt)
        self.messages = []
    
    def _enhance_system_prompt(self, original_system: str) -> str:
        """Enhance the system prompt to be more intelligent about responses"""
        enhancement = """

IMPORTANT RESPONSE GUIDELINES:
- When you don't know something specific, say so clearly and suggest alternatives
- Don't provide generic lists of information unless specifically asked
- Be contextual and relevant to the user's actual question
- If asked about unknown error codes or specific issues, acknowledge the limitation and provide helpful next steps
- Keep responses focused and conversational, not like reading from a manual
- Only provide detailed technical information when specifically requested
"""
        return original_system + enhancement

    def _normalize_message_content(self, content: Union[str, List[Dict], Dict]) -> Union[str, List[Dict]]:
        """
        Normalize message content to ensure AWS Claude API compatibility.
        
        Args:
            content: Message content that may be nested or malformed
            
        Returns:
            Normalized content structure
        """
        if isinstance(content, str):
            return content
            
        if isinstance(content, list):
            normalized_content = []
            for item in content:
                if isinstance(item, dict):
                    normalized_item = item.copy()
                    
                    # Fix nested text structures - ENHANCED FIX WITH DEEP RECURSION
                    if item.get("type") == "text" and "text" in item:
                        text_value = item["text"]
                        
                        # Recursively handle deeply nested text structures
                        def extract_text_recursively(value, depth=0):
                            if depth > 5:  # Prevent infinite recursion
                                return str(value)
                            
                            if isinstance(value, str):
                                return value
                            elif isinstance(value, dict):
                                # Handle nested text.text structure (multiple levels)
                                if "text" in value:
                                    return extract_text_recursively(value["text"], depth + 1)
                                elif "content" in value:
                                    return extract_text_recursively(value["content"], depth + 1)
                                elif "value" in value:
                                    return extract_text_recursively(value["value"], depth + 1)
                                else:
                                    # Fallback: use first string value found or convert entire dict
                                    string_values = [v for v in value.values() if isinstance(v, str)]
                                    if string_values:
                                        return string_values[0]
                                    else:
                                        return str(value)
                            else:
                                return str(value)
                        
                        normalized_text = extract_text_recursively(text_value)
                        normalized_item["text"] = normalized_text
                        
                        if self.verbose and text_value != normalized_text:
                            print(f"[CLAUDE FIX] Recursively normalized text structure: {type(text_value)} -> string")
                    
                    # Handle image content - ensure proper structure
                    elif item.get("type") == "image" and "source" in item:
                        # Image content is fine as-is, just copy
                        pass
                    
                    normalized_content.append(normalized_item)
                else:
                    normalized_content.append(item)
            
            return normalized_content
            
        if isinstance(content, dict):
            # Handle case where content is a single dict that should be a string
            if "text" in content:
                return content["text"]
            else:
                return str(content)
                
        # Fallback: convert to string
        return str(content)

    def _normalize_messages_for_aws(self, messages: List[Dict]) -> List[Dict]:
        """
        Normalize all messages in the conversation history for AWS Claude API.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            List of normalized messages
        """
        normalized_messages = []
        
        for message in messages:
            normalized_message = {
                "role": message.get("role", "user"),
                "content": self._normalize_message_content(message.get("content", ""))
            }
            
            if self.verbose:
                print(f"[CLAUDE FIX] Normalized message - Role: {normalized_message['role']}, Content type: {type(normalized_message['content'])}")
            
            normalized_messages.append(normalized_message)
        
        # DIAGNOSTIC: Enhanced logging for message normalization
        if self.verbose:
            print(f"[CLAUDE DIAGNOSTIC] ===== MESSAGE NORMALIZATION DETAILS =====")
            for i, (original, normalized) in enumerate(zip(messages, normalized_messages)):
                print(f"[CLAUDE DIAGNOSTIC] Message {i} normalization:")
                print(f"[CLAUDE DIAGNOSTIC]   Original content type: {type(original.get('content'))}")
                print(f"[CLAUDE DIAGNOSTIC]   Normalized content type: {type(normalized['content'])}")
                
                if isinstance(original.get('content'), list):
                    print(f"[CLAUDE DIAGNOSTIC]   Original content length: {len(original['content'])}")
                    for j, item in enumerate(original['content']):
                        if isinstance(item, dict) and item.get('type') == 'text':
                            print(f"[CLAUDE DIAGNOSTIC]   Original text item {j}: {type(item.get('text'))}")
                
                if isinstance(normalized['content'], list):
                    print(f"[CLAUDE DIAGNOSTIC]   Normalized content length: {len(normalized['content'])}")
                    for j, item in enumerate(normalized['content']):
                        if isinstance(item, dict) and item.get('type') == 'text':
                            print(f"[CLAUDE DIAGNOSTIC]   Normalized text item {j}: {type(item.get('text'))}")
                            if isinstance(item.get('text'), dict):
                                print(f"[CLAUDE DIAGNOSTIC]   ❌ NORMALIZATION FAILED: text is still dict!")
            
            print(f"[CLAUDE DIAGNOSTIC] ===== END NORMALIZATION DETAILS =====")
        
        return normalized_messages

    def chat_iter(self, prompt: str, image_base64=None) -> Iterator[str]:
        """
        Send message to Claude via AWS HTTP endpoint and yield response tokens.
        
        Args:
            prompt (str): User message
            image_base64 (str, optional): Base64 encoded image for vision analysis
            
        Yields:
            str: Response tokens
        """
        # Add user message to history
        user_message = {"role": "user", "content": prompt}
        
        # If image is provided, format as vision message
        if image_base64:
            print(f"[CLAUDE VISION] Processing image data: {len(image_base64)} chars")
            
            # Remove data URL prefix if present
            if image_base64.startswith('data:image'):
                image_base64 = image_base64.split(',')[1]
                print(f"[CLAUDE VISION] Cleaned image data: {len(image_base64)} chars")
            
            user_message["content"] = [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_base64
                    }
                }
            ]
            print(f"[CLAUDE VISION] Formatted vision message with image")
        
        self.messages.append(user_message)
        
        try:
            if self.verbose:
                print(f"Sending request to AWS HTTP endpoint: {self.base_url}/claude")
                if image_base64:
                    print(f"[VISION] Including image data ({len(image_base64)} chars)")
            
            # Prepare the payload with system prompt and conversation history
            payload = {
                "text": prompt,
                "system": self.system if self.system else ""
            }
            
            # Include image data if provided - THIS IS THE CRITICAL FIX
            if image_base64:
                payload["image"] = image_base64
                payload["has_vision"] = True
                print(f"[CLAUDE VISION] Added image to payload")
            
            # Include normalized conversation history if available - ENHANCED CRITICAL FIX
            if len(self.messages) > 1:
                # For vision requests, exclude the current vision message from history to avoid conflicts
                messages_to_normalize = self.messages[:-1] if image_base64 else self.messages
                
                if messages_to_normalize:
                    normalized_messages = self._normalize_messages_for_aws(messages_to_normalize)
                    payload["messages"] = normalized_messages
                    
                    if self.verbose:
                        print(f"[CLAUDE FIX] Normalized {len(normalized_messages)} messages for AWS API")
                        if image_base64:
                            print(f"[CLAUDE FIX] Excluded current vision message from history to prevent conflicts")
                        for i, msg in enumerate(normalized_messages):
                            content_preview = str(msg["content"])[:100] if msg["content"] else ""
                            print(f"[CLAUDE FIX] Message {i}: {msg['role']} - {content_preview}...")
            
            print(f"[CLAUDE VISION] Payload keys: {list(payload.keys())}")
            
            # DIAGNOSTIC: Log the complete payload structure for vision requests
            if image_base64:
                print(f"[CLAUDE DIAGNOSTIC] ===== COMPLETE PAYLOAD STRUCTURE =====")
                print(f"[CLAUDE DIAGNOSTIC] Payload type: {type(payload)}")
                print(f"[CLAUDE DIAGNOSTIC] Payload keys: {list(payload.keys())}")
                
                # Log each payload field in detail
                for key, value in payload.items():
                    print(f"[CLAUDE DIAGNOSTIC] {key}: {type(value)}")
                    if key == "messages" and isinstance(value, list):
                        print(f"[CLAUDE DIAGNOSTIC] Messages array length: {len(value)}")
                        for i, msg in enumerate(value):
                            print(f"[CLAUDE DIAGNOSTIC] Message {i}: {type(msg)}")
                            if isinstance(msg, dict):
                                print(f"[CLAUDE DIAGNOSTIC] Message {i} keys: {list(msg.keys())}")
                                if "content" in msg:
                                    content = msg["content"]
                                    print(f"[CLAUDE DIAGNOSTIC] Message {i} content type: {type(content)}")
                                    if isinstance(content, list):
                                        print(f"[CLAUDE DIAGNOSTIC] Message {i} content length: {len(content)}")
                                        for j, item in enumerate(content):
                                            print(f"[CLAUDE DIAGNOSTIC] Content {j}: {type(item)}")
                                            if isinstance(item, dict):
                                                print(f"[CLAUDE DIAGNOSTIC] Content {j} keys: {list(item.keys())}")
                                                if "text" in item:
                                                    text_value = item["text"]
                                                    print(f"[CLAUDE DIAGNOSTIC] Content {j} text type: {type(text_value)}")
                                                    if isinstance(text_value, dict):
                                                        print(f"[CLAUDE DIAGNOSTIC] ❌ PROBLEM FOUND: text is dict, not string!")
                                                        print(f"[CLAUDE DIAGNOSTIC] text dict keys: {list(text_value.keys())}")
                                                    else:
                                                        print(f"[CLAUDE DIAGNOSTIC] ✅ text is string: {len(str(text_value))} chars")
                
                # Log the JSON structure (truncated for readability)
                try:
                    payload_json = json.dumps(payload, indent=2, default=str)
                    print(f"[CLAUDE DIAGNOSTIC] JSON payload preview (first 1000 chars):")
                    print(payload_json[:1000])
                    if len(payload_json) > 1000:
                        print("... (truncated)")
                except Exception as e:
                    print(f"[CLAUDE DIAGNOSTIC] Error serializing payload: {e}")
                
                print(f"[CLAUDE DIAGNOSTIC] ===== END PAYLOAD STRUCTURE =====")
            
            # Check if base_url is configured
            if not self.base_url or self.base_url == "None":
                error_msg = "AWS base URL not configured. Please set base_url in configuration."
                if self.verbose:
                    print(error_msg)
                yield error_msg
                return
            
            # Send request to AWS HTTP endpoint
            response = requests.post(
                f"{self.base_url}/claude",
                json=payload,
                timeout=60
            )
            
            # Check for errors
            if response.status_code != 200:
                error_msg = f"HTTP error {response.status_code}: {response.text}"
                if self.verbose:
                    print(error_msg)
                yield error_msg
                return
            
            # Parse the response
            data = response.json()
            if "reply" not in data:
                error_msg = "Invalid response format: missing 'reply' field"
                if self.verbose:
                    print(error_msg)
                yield error_msg
                return
            
            # Get the response text
            response_text = data["reply"]
            
            print(f"[CLAUDE VISION] Received response: {len(response_text)} chars")
            
            # Simulate streaming by yielding characters one by one
            for char in response_text:
                yield char
            
            # Add assistant response to history
            self.messages.append({
                "role": "assistant",
                "content": response_text
            })
            
            # CRITICAL FIX: Clean conversation history after vision analysis to prevent ValidationException
            if image_base64:
                print(f"[CLAUDE VISION FIX] Cleaning conversation history after vision analysis")
                
                # Remove vision messages that could cause structure issues in future conversations
                cleaned_messages = []
                for msg in self.messages:
                    content = msg.get('content')
                    
                    # Skip messages with complex vision content structures
                    if isinstance(content, list):
                        has_image = any(item.get('type') == 'image' for item in content if isinstance(item, dict))
                        has_complex_text = any(
                            isinstance(item.get('text'), dict)
                            for item in content
                            if isinstance(item, dict) and item.get('type') == 'text'
                        )
                        
                        if has_image or has_complex_text:
                            print(f"[CLAUDE VISION FIX] Removing problematic vision message from history")
                            continue
                    
                    cleaned_messages.append(msg)
                
                # Keep only the last few messages to maintain context but avoid structure issues
                if len(cleaned_messages) > 4:
                    cleaned_messages = cleaned_messages[-4:]
                
                self.messages = cleaned_messages
                print(f"[CLAUDE VISION FIX] Conversation history cleaned: {len(self.messages)} messages remaining")
                
        except Exception as e:
            if self.verbose:
                print(f"Error in Claude chat via AWS HTTP: {str(e)}")
            yield f"Error occurred: {str(e)}"

    def handle_interrupt(self, heard_response: str) -> None:
        """
        Handle interruption by updating the last assistant message.
        
        Args:
            heard_response (str): The heard portion of the response
        """
        if self.messages and self.messages[-1]["role"] == "assistant":
            # Update last assistant message with only heard portion
            self.messages[-1]["content"] = heard_response
