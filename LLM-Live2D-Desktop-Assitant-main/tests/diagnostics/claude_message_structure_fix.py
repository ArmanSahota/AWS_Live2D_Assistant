#!/usr/bin/env python3
"""
Claude Message Structure Fix
============================

This script fixes the AWS Claude API validation error:
"messages.0.content.0.text.text: Input should be a valid string"

The issue occurs when vision functionality creates nested message structures
that are incompatible with AWS Claude API expectations.

PROBLEM:
- Vision messages create nested content: {"type": "text", "text": {"text": "..."}}
- AWS Claude expects: {"type": "text", "text": "..."}
- This causes "messages.0.content.0.text.text" validation error

SOLUTION:
- Normalize message structures before sending to AWS Claude API
- Flatten nested text content while preserving vision capabilities
- Add validation logging for debugging
"""

import json
import logging
from typing import Dict, List, Any, Union

def create_claude_message_fix():
    """
    Create the fix for Claude message structure formatting.
    
    Returns:
        dict: Contains the fixed code for claude.py
    """
    
    fixed_claude_py = '''import requests
from typing import Iterator
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
        self.system = system
        self.model = model
        self.verbose = verbose
        self.base_url = base_url
        
        if self.verbose:
            print(f"Initialized Claude LLM with AWS HTTP endpoint: {base_url}")
        
        # Store conversation history (excluding system prompt)
        self.messages = []

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
                    
                    # Fix nested text structures
                    if item.get("type") == "text" and "text" in item:
                        text_value = item["text"]
                        
                        # Handle nested text.text structure
                        if isinstance(text_value, dict) and "text" in text_value:
                            normalized_item["text"] = text_value["text"]
                            if self.verbose:
                                print(f"[CLAUDE FIX] Normalized nested text structure")
                        elif isinstance(text_value, str):
                            normalized_item["text"] = text_value
                        else:
                            # Fallback: convert to string
                            normalized_item["text"] = str(text_value)
                            if self.verbose:
                                print(f"[CLAUDE FIX] Converted non-string text to string: {type(text_value)}")
                    
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
            
            # Include image data if provided
            if image_base64:
                payload["image"] = image_base64
                payload["has_vision"] = True
                print(f"[CLAUDE VISION] Added image to payload")
            
            # Include normalized conversation history if available - THIS IS THE CRITICAL FIX
            if len(self.messages) > 1:
                normalized_messages = self._normalize_messages_for_aws(self.messages)
                payload["messages"] = normalized_messages
                
                if self.verbose:
                    print(f"[CLAUDE FIX] Normalized {len(normalized_messages)} messages for AWS API")
                    for i, msg in enumerate(normalized_messages):
                        content_preview = str(msg["content"])[:100] if msg["content"] else ""
                        print(f"[CLAUDE FIX] Message {i}: {msg['role']} - {content_preview}...")
            
            print(f"[CLAUDE VISION] Payload keys: {list(payload.keys())}")
            
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
            self.messages[-1]["content"] = heard_response'''

    return {
        "claude_py_fix": fixed_claude_py
    }

def apply_claude_message_fix():
    """
    Apply the Claude message structure fix.
    """
    print("=" * 60)
    print("CLAUDE MESSAGE STRUCTURE FIX")
    print("=" * 60)
    print()
    print("ISSUE DIAGNOSED:")
    print("- AWS Claude API validation error: 'messages.0.content.0.text.text: Input should be a valid string'")
    print("- Caused by nested message structures from vision functionality")
    print("- Vision messages create double-nested text content incompatible with AWS API")
    print()
    
    fixes = create_claude_message_fix()
    
    print("SOLUTION IMPLEMENTED:")
    print("1. Added message content normalization functions")
    print("2. Fixed nested text.text structures before sending to AWS")
    print("3. Added validation logging for debugging")
    print("4. Preserved vision functionality while ensuring AWS compatibility")
    print()
    
    print("APPLY THIS FIX:")
    print("Replace the content of LLM-Live2D-Desktop-Assitant-main/llm/claude.py with:")
    print()
    print("```python")
    print(fixes["claude_py_fix"])
    print("```")
    print()
    
    print("VERIFICATION:")
    print("1. Restart the application")
    print("2. Test normal conversation (should work without validation errors)")
    print("3. Test vision functionality (should work with normalized message structures)")
    print("4. Check logs for '[CLAUDE FIX]' messages to confirm normalization is working")
    print()
    
    print("This fix resolves the AWS Claude API validation error while maintaining")
    print("full compatibility with both text and vision conversations.")

if __name__ == "__main__":
    apply_claude_message_fix()