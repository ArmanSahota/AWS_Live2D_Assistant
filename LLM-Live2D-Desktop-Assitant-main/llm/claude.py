import requests
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

    def chat_iter(self, prompt: str, image_base64=None) -> Iterator[str]:
        """
        Send message to Claude via AWS HTTP endpoint and yield response tokens.
        
        Args:
            prompt (str): User message
            image_base64 (str, optional): Base64 encoded image (not used in this implementation)
            
        Yields:
            str: Response tokens
        """
        # Add user message to history
        self.messages.append({"role": "user", "content": prompt})
        
        try:
            if self.verbose:
                print(f"Sending request to AWS HTTP endpoint: {self.base_url}/claude")
            
            # Prepare the payload with system prompt and conversation history
            payload = {
                "text": prompt,
                "system": self.system if self.system else ""
            }
            
            # Include conversation history if available
            if len(self.messages) > 1:  # More than just the current user message
                # Convert our message format to the format expected by the Lambda function
                payload["messages"] = self.messages
            
            # Send request to AWS HTTP endpoint
            response = requests.post(
                f"{self.base_url}/claude",
                json=payload,
                timeout=60  # 60 second timeout
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
            
            # Simulate streaming by yielding characters one by one
            # This maintains compatibility with the existing code that expects streaming
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
            self.messages[-1]["content"] = heard_response
