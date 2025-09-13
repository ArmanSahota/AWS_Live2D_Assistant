import os
import sys
import requests
import json
import time

def test_health(base_url):
    """Test the health endpoint of the AWS API."""
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check status code: {response.status_code}")
        if response.status_code == 200:
            print(f"Health check response: {response.json()}")
            return True
        else:
            print(f"Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"Health check error: {str(e)}")
        return False

def test_claude_streaming(base_url, prompt="Tell me a short story about a robot learning to paint."):
    """
    Test the Claude endpoint with simulated streaming.
    
    This function demonstrates how the claude.py implementation simulates streaming
    by yielding characters one by one from the response.
    """
    try:
        print(f"Sending request to {base_url}/claude")
        print(f"Prompt: {prompt}")
        
        response = requests.post(
            f"{base_url}/claude",
            json={"text": prompt},
            timeout=60
        )
        
        print(f"Claude API status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "reply" in data:
                print("\nClaude response (simulated streaming):")
                print("-" * 50)
                
                # Simulate streaming by printing characters one by one
                for char in data["reply"]:
                    print(char, end="", flush=True)
                    time.sleep(0.01)  # Small delay to simulate streaming
                
                print("\n" + "-" * 50)
                return True
            else:
                print(f"Invalid response format: {data}")
                return False
        else:
            print(f"Claude API request failed: {response.text}")
            return False
    except Exception as e:
        print(f"Claude API error: {str(e)}")
        return False

def test_claude_with_conversation(base_url):
    """
    Test the Claude endpoint with a conversation history.
    
    This function demonstrates how to send a conversation history to the Claude endpoint.
    """
    try:
        print(f"Sending conversation to {base_url}/claude")
        
        # Create a conversation history
        messages = [
            {"role": "user", "content": "Hello, my name is Alex."},
            {"role": "assistant", "content": "Hello Alex! It's nice to meet you. How can I help you today?"},
            {"role": "user", "content": "What was my name again?"}
        ]
        
        print("Conversation history:")
        for msg in messages:
            print(f"{msg['role']}: {msg['content']}")
        
        # Send the conversation history
        response = requests.post(
            f"{base_url}/claude",
            json={"messages": messages},
            timeout=60
        )
        
        print(f"Claude API status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "reply" in data:
                print("\nClaude response with conversation history:")
                print("-" * 50)
                print(data["reply"])
                print("-" * 50)
                return True
            else:
                print(f"Invalid response format: {data}")
                return False
        else:
            print(f"Claude API request failed: {response.text}")
            return False
    except Exception as e:
        print(f"Claude API error: {str(e)}")
        return False

def main():
    # Get the base URL from environment variable or use the one from conf.yaml
    base_url = os.environ.get("VITE_HTTP_BASE", "https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev")
    
    print(f"Using AWS HTTP endpoint: {base_url}")
    
    # Test the health endpoint
    print("\n=== Testing Health Endpoint ===")
    health_ok = test_health(base_url)
    
    if not health_ok:
        print("Health check failed. Exiting.")
        sys.exit(1)
    
    # Test the Claude endpoint with simulated streaming
    print("\n=== Testing Claude Endpoint with Simulated Streaming ===")
    streaming_ok = test_claude_streaming(base_url)
    
    if not streaming_ok:
        print("Claude API streaming test failed. Exiting.")
        sys.exit(1)
    
    # Test the Claude endpoint with a conversation history
    print("\n=== Testing Claude Endpoint with Conversation History ===")
    conversation_ok = test_claude_with_conversation(base_url)
    
    if not conversation_ok:
        print("Claude API conversation test failed. This is expected if the AWS Lambda function doesn't support conversation history yet.")
    
    print("\nAll tests completed.")

if __name__ == "__main__":
    main()
