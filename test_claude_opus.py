"""
Test Claude Opus Model via AWS Bedrock
Usage: python test_claude_opus.py
"""
import requests
import json
import os
from datetime import datetime

# Configuration
# Replace with your actual AWS endpoint after deployment
HTTP_BASE = os.getenv('HTTP_BASE', 'https://your-api-endpoint.execute-api.us-west-2.amazonaws.com/dev')

def test_claude_opus():
    """Test Claude Opus model through AWS endpoint"""
    
    print("=" * 60)
    print("CLAUDE OPUS MODEL TEST")
    print("=" * 60)
    print(f"Endpoint: {HTTP_BASE}/claude")
    print(f"Model: anthropic.claude-3-5-sonnet-20241022-v2:0")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Test cases with increasing complexity
    test_cases = [
        {
            "name": "Simple Greeting",
            "text": "Hello! Please introduce yourself.",
            "system": "You are a helpful AI assistant."
        },
        {
            "name": "Complex Reasoning",
            "text": "Explain quantum computing in simple terms, then provide a Python code example of a quantum circuit simulation.",
            "system": "You are an expert in quantum computing who explains complex topics clearly."
        },
        {
            "name": "Creative Writing",
            "text": "Write a short haiku about artificial intelligence, then explain its meaning.",
            "system": "You are a creative poet and literary analyst."
        },
        {
            "name": "VTuber Persona",
            "text": "Hello! I'm setting up my desktop and need your help. Can you tell me about yourself?",
            "system": "You are a friendly Live2D VTuber assistant who helps users with their desktop tasks. You have a cheerful personality and use casual, friendly language."
        }
    ]
    
    success_count = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print("-" * 40)
        print(f"Input: {test['text'][:100]}...")
        print(f"System: {test['system'][:100]}...")
        
        try:
            # Make request to Claude Opus
            response = requests.post(
                f"{HTTP_BASE}/claude",
                json={
                    "text": test['text'],
                    "system": test['system']
                },
                headers={
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get('reply', 'No reply received')
                
                # Display response (truncated for readability)
                print(f"✅ Success!")
                print(f"Response: {reply[:200]}...")
                print(f"Full length: {len(reply)} characters")
                success_count += 1
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(f"Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - Is your AWS endpoint deployed?")
            print("\nTo deploy:")
            print("1. cd LLM-Live2D-Desktop-Assitant-main/backend")
            print("2. sam build")
            print("3. sam deploy --guided")
            print("4. Update HTTP_BASE with the endpoint URL from outputs")
            
        except requests.exceptions.Timeout:
            print("❌ Request timed out (30s) - Model might be cold starting")
            print("Try again in a moment")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {success_count}/{len(test_cases)}")
    
    if success_count == len(test_cases):
        print("✅ ALL TESTS PASSED - Claude Opus is working!")
    elif success_count > 0:
        print("⚠️ PARTIAL SUCCESS - Some tests passed")
    else:
        print("❌ ALL TESTS FAILED - Check your configuration")
    
    print("\nNext steps:")
    if success_count == 0:
        print("1. Deploy the AWS backend: sam deploy")
        print("2. Set HTTP_BASE environment variable")
        print("3. Check AWS Bedrock access for Opus model")
    else:
        print("1. Update conf.yaml with your endpoint")
        print("2. Start the app: python server.py")
        print("3. Test with TTS/STT integration")
    
    return success_count > 0

def test_model_availability():
    """Quick test to check if the model is available"""
    print("\nChecking model availability...")
    print("Model ID: anthropic.claude-opus-4-1-20250805-v1:0")
    print("Region: us-west-2")
    print("\nNote: You need to request access to Claude Opus in AWS Bedrock")
    print("Go to: AWS Console > Bedrock > Model access")
    print("Request access to: Anthropic Claude Opus")

if __name__ == "__main__":
    # Check if endpoint is configured
    if HTTP_BASE.startswith("https://your-"):
        print("⚠️ WARNING: Using placeholder endpoint")
        print("Please set the HTTP_BASE environment variable:")
        print("  export HTTP_BASE=https://your-actual-endpoint.execute-api.us-west-2.amazonaws.com/dev")
        print()
        test_model_availability()
    else:
        # Run tests
        success = test_claude_opus()
        
        if not success:
            test_model_availability()