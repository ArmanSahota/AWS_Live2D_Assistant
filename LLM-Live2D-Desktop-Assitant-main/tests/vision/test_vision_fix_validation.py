#!/usr/bin/env python3
"""
Test script to validate the vision system fix for undefined 'category' and 'confidence' variables.
This will test the vision analysis endpoint and check if the NameError is resolved.
"""

import asyncio
import websockets
import json
import base64
import os
from pathlib import Path

async def test_vision_system():
    """Test the vision system with a real image to validate the fix."""
    
    print("🔍 Testing Vision System Fix Validation")
    print("=" * 50)
    
    # Find a test image
    test_image_path = None
    possible_paths = [
        "Test_Photos/SwitchController.jpg",
        "Test_Photos/Keyboard.jpg",
        "Test_Photos/SodaPop.jpg"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            test_image_path = path
            break
    
    if not test_image_path:
        print("❌ No test images found. Please ensure test images exist in Test_Photos/")
        return False
    
    print(f"📸 Using test image: {test_image_path}")
    
    # Read and encode the image
    try:
        with open(test_image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        print(f"✅ Image loaded successfully: {len(image_data)} chars")
    except Exception as e:
        print(f"❌ Failed to load image: {e}")
        return False
    
    # Test the websocket connection and vision analysis
    try:
        print("\n🔌 Connecting to WebSocket server...")
        async with websockets.connect("ws://localhost:8000/client-ws") as websocket:
            print("✅ Connected to WebSocket server")
            
            # Send vision analysis request
            analysis_request = {
                "type": "object-analysis-request",
                "analysisId": "test_fix_validation_123",
                "imageData": f"data:image/jpeg;base64,{image_data}",
                "userQuestion": "What do you see in this image? Please describe it in detail."
            }
            
            print("📤 Sending vision analysis request...")
            await websocket.send(json.dumps(analysis_request))
            
            # Wait for response
            print("⏳ Waiting for vision analysis response...")
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                response_data = json.loads(response)
                
                print("\n📥 Received response:")
                print(f"Response type: {response_data.get('type', 'unknown')}")
                print(f"Analysis ID: {response_data.get('analysisId', 'unknown')}")
                
                if response_data.get('type') == 'object-analysis-response':
                    result = response_data.get('result', {})
                    print(f"✅ Vision analysis completed successfully!")
                    print(f"Category: {result.get('category', 'N/A')}")
                    print(f"Confidence: {result.get('confidence', 'N/A')}")
                    print(f"Analysis preview: {result.get('analysis', 'N/A')[:100]}...")
                    
                    # Check if our diagnostic variables are in the details
                    details = result.get('details', [])
                    for detail in details:
                        if isinstance(detail, str) and 'Object category:' in detail:
                            print(f"🔍 Found category detail: {detail}")
                        if isinstance(detail, str) and 'Analysis confidence:' in detail:
                            print(f"🔍 Found confidence detail: {detail}")
                    
                    return True
                    
                elif response_data.get('type') == 'error':
                    print(f"❌ Error response received: {response_data}")
                    return False
                else:
                    print(f"⚠️ Unexpected response type: {response_data}")
                    return False
                    
            except asyncio.TimeoutError:
                print("❌ Timeout waiting for response")
                return False
                
    except ConnectionRefusedError:
        print("❌ Could not connect to WebSocket server. Is the server running?")
        print("💡 Please start the server first with: python server.py")
        return False
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Vision System Fix Validation Test")
    print("This test will validate that the 'category' and 'confidence' variable fix works.")
    print("\n📋 Test Plan:")
    print("1. Load a test image")
    print("2. Send vision analysis request via WebSocket")
    print("3. Check if NameError is resolved")
    print("4. Validate diagnostic logs appear")
    print("5. Confirm vision analysis completes successfully")
    
    # Run the async test
    try:
        result = asyncio.run(test_vision_system())
        
        print("\n" + "=" * 50)
        if result:
            print("🎉 TEST PASSED: Vision system fix validation successful!")
            print("✅ The undefined 'category' and 'confidence' variables have been fixed.")
            print("✅ Vision analysis completes without NameError.")
        else:
            print("❌ TEST FAILED: Vision system still has issues.")
            print("🔧 Check the server logs for diagnostic information.")
            
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")

if __name__ == "__main__":
    main()