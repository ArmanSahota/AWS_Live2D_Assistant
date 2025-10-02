import os
import sys
import requests
import json

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

def test_claude(base_url, prompt="Hello, Claude! This is a test."):
    """Test the Claude endpoint of the AWS API."""
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
                print("\nClaude response:")
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

def test_claude_with_system(base_url, prompt="Tell me about yourself.", system="You are a helpful assistant."):
    """Test the Claude endpoint with a system prompt."""
    try:
        print(f"Sending request to {base_url}/claude with system prompt")
        print(f"System: {system}")
        print(f"Prompt: {prompt}")
        
        # Note: This assumes the AWS Lambda function has been updated to support system prompts
        response = requests.post(
            f"{base_url}/claude",
            json={
                "text": prompt,
                "system": system
            },
            timeout=60
        )
        
        print(f"Claude API status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "reply" in data:
                print("\nClaude response with system prompt:")
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
    
    # Test the Claude endpoint with a simple prompt
    print("\n=== Testing Claude Endpoint ===")
    claude_ok = test_claude(base_url)
    
    if not claude_ok:
        print("Claude API test failed. Exiting.")
        sys.exit(1)
    
    # Test the Claude endpoint with a system prompt
    # Note: This may fail if the AWS Lambda function doesn't support system prompts yet
    print("\n=== Testing Claude Endpoint with System Prompt ===")
    claude_system_ok = test_claude_with_system(base_url)
    
    if not claude_system_ok:
        print("Claude API test with system prompt failed. This is expected if the AWS Lambda function doesn't support system prompts yet.")
    
    print("\nAll tests completed.")

if __name__ == "__main__":
    main()
