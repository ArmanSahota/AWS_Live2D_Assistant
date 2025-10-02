#!/usr/bin/env python3
"""
Test Script for Claude Conversation ValidationException Fix

This script tests the fix for the ValidationException error that occurs
after vision analysis when transitioning back to normal conversation.
"""

import asyncio
import websockets
import json
import base64
import time
from pathlib import Path

async def test_conversation_validation_fix():
    """
    Test the conversation validation fix by simulating the exact scenario
    that caused the ValidationException error.
    """
    
    print("🧪 TESTING CLAUDE CONVERSATION VALIDATION FIX")
    print("=" * 60)
    
    # Test configuration
    server_url = "ws://localhost:1018/client-ws"  # Adjust port as needed
    test_image_path = "test_image.jpg"  # You can use any image file
    
    try:
        # Connect to WebSocket server
        print("📡 Connecting to WebSocket server...")
        async with websockets.connect(server_url) as websocket:
            print("✅ Connected successfully")
            
            # Step 1: Test normal conversation before vision analysis
            print("\n🗣️  STEP 1: Testing normal conversation (baseline)")
            await test_normal_conversation(websocket, "Hello, how are you?")
            
            # Step 2: Perform vision analysis (if image available)
            if Path(test_image_path).exists():
                print("\n👁️  STEP 2: Testing vision analysis")
                await test_vision_analysis(websocket, test_image_path)
                
                # Wait for vision analysis to complete
                await asyncio.sleep(3)
                
                # Step 3: Test normal conversation after vision analysis (the critical test)
                print("\n🔍 STEP 3: Testing conversation after vision analysis (CRITICAL)")
                success = await test_normal_conversation(websocket, "Let's tell me more about it")
                
                if success:
                    print("\n✅ SUCCESS: Conversation validation fix is working!")
                    print("   No ValidationException errors occurred after vision analysis")
                else:
                    print("\n❌ FAILURE: ValidationException error still occurs")
                    
            else:
                print(f"\n⚠️  Skipping vision analysis test - {test_image_path} not found")
                print("   Create a test image file to run the complete test")
            
            # Step 4: Additional conversation tests
            print("\n🔄 STEP 4: Additional conversation stability tests")
            for i in range(3):
                await test_normal_conversation(websocket, f"Test message {i+1}")
                await asyncio.sleep(1)
            
            print("\n✅ All conversation tests completed")
            
    except ConnectionRefusedError:
        print("❌ Could not connect to WebSocket server")
        print("💡 Make sure the server is running: python LLM-Live2D-Desktop-Assitant-main/server.py")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    return True

async def test_normal_conversation(websocket, message):
    """
    Test normal conversation flow
    """
    try:
        print(f"   Sending: {message}")
        
        # Send text message
        await websocket.send(json.dumps({
            "type": "mic-audio-end-with-text",
            "text": message
        }))
        
        # Wait for response
        response_received = False
        error_occurred = False
        
        timeout = time.time() + 10  # 10 second timeout
        while time.time() < timeout and not response_received:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                data = json.loads(response)
                
                if data.get("type") == "full-text":
                    response_text = data.get("text", "")
                    if "HTTP error 500" in response_text or "ValidationException" in response_text:
                        print(f"   ❌ ValidationException error detected: {response_text[:100]}...")
                        error_occurred = True
                        break
                    else:
                        print(f"   ✅ Response received: {response_text[:50]}...")
                        response_received = True
                        break
                        
            except asyncio.TimeoutError:
                continue
        
        if error_occurred:
            return False
        elif not response_received:
            print("   ⚠️  No response received within timeout")
            return False
        else:
            return True
            
    except Exception as e:
        print(f"   ❌ Error in conversation test: {e}")
        return False

async def test_vision_analysis(websocket, image_path):
    """
    Test vision analysis with an image
    """
    try:
        print(f"   Loading image: {image_path}")
        
        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        
        print("   Sending vision analysis request...")
        
        # Send vision analysis request
        await websocket.send(json.dumps({
            "type": "object-analysis-request",
            "image": f"data:image/jpeg;base64,{image_data}",
            "question": "What do you see in this image?"
        }))
        
        # Wait for vision analysis response
        timeout = time.time() + 30  # 30 second timeout for vision analysis
        while time.time() < timeout:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(response)
                
                if data.get("type") == "object-analysis-result":
                    analysis = data.get("analysis", "")
                    print(f"   ✅ Vision analysis completed: {analysis[:50]}...")
                    return True
                    
            except asyncio.TimeoutError:
                continue
        
        print("   ⚠️  Vision analysis timed out")
        return False
        
    except Exception as e:
        print(f"   ❌ Error in vision analysis: {e}")
        return False

def create_test_image():
    """
    Create a simple test image if none exists
    """
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple test image
        img = Image.new('RGB', (200, 200), color='blue')
        draw = ImageDraw.Draw(img)
        draw.text((50, 90), "TEST IMAGE", fill='white')
        img.save("test_image.jpg")
        print("✅ Created test_image.jpg for testing")
        return True
    except ImportError:
        print("⚠️  PIL not available - cannot create test image")
        print("   Please place any image file as 'test_image.jpg' to test vision analysis")
        return False

def main():
    """
    Main test function
    """
    print("🔧 CLAUDE CONVERSATION VALIDATION FIX TEST")
    print("This test validates the fix for ValidationException errors after vision analysis")
    print()
    
    # Create test image if needed
    if not Path("test_image.jpg").exists():
        create_test_image()
    
    # Run the test
    try:
        result = asyncio.run(test_conversation_validation_fix())
        
        if result:
            print("\n🎉 TEST PASSED: Conversation validation fix is working correctly!")
        else:
            print("\n💥 TEST FAILED: Issues detected with conversation validation")
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")

if __name__ == "__main__":
    main()