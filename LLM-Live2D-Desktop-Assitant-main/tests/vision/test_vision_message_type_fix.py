#!/usr/bin/env python3
"""
Vision Message Type Fix Test
Tests that the backend now sends the correct message type that the frontend expects.
"""

import asyncio
import websockets
import json
import base64
import sys
import os
from pathlib import Path

# Test configuration
WEBSOCKET_URL = "ws://localhost:8000/client-ws"
TEST_IMAGE_PATH = "Test_Photos/SwitchController.jpg"

def create_test_image_data():
    """Create base64 encoded test image data"""
    try:
        # Try to load a test image
        image_path = Path(TEST_IMAGE_PATH)
        if image_path.exists():
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
                return f"data:image/jpeg;base64,{image_data}"
        else:
            print(f"[TEST] Test image not found at {image_path}")
            # Create a minimal test image data (1x1 pixel PNG)
            minimal_png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            return f"data:image/png;base64,{minimal_png}"
    except Exception as e:
        print(f"[TEST] Error creating test image: {e}")
        # Fallback to minimal PNG
        minimal_png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        return f"data:image/png;base64,{minimal_png}"

async def test_vision_message_type():
    """Test that vision analysis returns the correct message type"""
    
    print("[TEST] 🧪 Testing Vision Message Type Fix...")
    print("[TEST] Connecting to WebSocket...")
    
    try:
        # Connect to WebSocket
        websocket = await websockets.connect(WEBSOCKET_URL)
        print("[TEST] ✅ WebSocket connected successfully")
        
        # Wait for initial messages
        await asyncio.sleep(1)
        
        # Drain any initial messages
        try:
            while True:
                message = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                data = json.loads(message)
                print(f"[TEST] Initial message: {data.get('type', 'unknown')}")
        except asyncio.TimeoutError:
            pass  # No more initial messages
        
        # Create test vision analysis request
        test_analysis_id = "test_message_type_fix_12345"
        test_image_data = create_test_image_data()
        
        vision_request = {
            "type": "object-analysis-request",
            "analysisId": test_analysis_id,
            "imageData": test_image_data,
            "userQuestion": "What is this object? (Message type test)",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        print(f"[TEST] 📤 Sending vision analysis request with ID: {test_analysis_id}")
        await websocket.send(json.dumps(vision_request))
        
        # Wait for response and check message type
        print("[TEST] 📥 Waiting for response...")
        
        response_received = False
        correct_message_type = False
        response_data = None
        
        # Wait up to 30 seconds for response
        try:
            timeout_seconds = 30
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < timeout_seconds:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    message_type = data.get('type', 'unknown')
                    
                    print(f"[TEST] 📨 Received message type: '{message_type}'")
                    
                    # Check if this is our vision analysis response
                    if data.get('analysisId') == test_analysis_id:
                        response_received = True
                        response_data = data
                        
                        # Check if message type is correct
                        if message_type == "object-analysis-result":
                            correct_message_type = True
                            print(f"[TEST] ✅ CORRECT MESSAGE TYPE: '{message_type}'")
                            break
                        elif message_type == "object-analysis-response":
                            print(f"[TEST] ❌ OLD MESSAGE TYPE: '{message_type}' (fix not applied)")
                            break
                        else:
                            print(f"[TEST] ❓ UNEXPECTED MESSAGE TYPE: '{message_type}'")
                            break
                    else:
                        # Other message, continue waiting
                        if message_type not in ['control', 'full-text', 'audio-payload']:
                            print(f"[TEST] 📋 Other message: {message_type}")
                        
                except asyncio.TimeoutError:
                    continue  # Keep waiting
                    
        except Exception as e:
            print(f"[TEST] ❌ Error waiting for response: {e}")
        
        # Close WebSocket
        await websocket.close()
        
        # Report results
        print("\n" + "="*60)
        print("[TEST] 📊 TEST RESULTS")
        print("="*60)
        
        if response_received:
            print(f"[TEST] ✅ Response received for analysis ID: {test_analysis_id}")
            
            if correct_message_type:
                print("[TEST] ✅ MESSAGE TYPE FIX SUCCESSFUL!")
                print("[TEST] ✅ Backend now sends 'object-analysis-result'")
                print("[TEST] ✅ Frontend will receive vision analysis responses")
                
                # Show response details
                if response_data and 'result' in response_data:
                    result = response_data['result']
                    print(f"[TEST] 📋 Analysis confidence: {result.get('confidence', 'N/A')}")
                    print(f"[TEST] 📋 Analysis category: {result.get('category', 'N/A')}")
                    analysis_text = result.get('analysis', '')
                    if analysis_text:
                        preview = analysis_text[:100] + "..." if len(analysis_text) > 100 else analysis_text
                        print(f"[TEST] 📋 Analysis preview: {preview}")
                
                return True
            else:
                print("[TEST] ❌ MESSAGE TYPE FIX FAILED!")
                print("[TEST] ❌ Backend still sends wrong message type")
                print("[TEST] ❌ Frontend will not receive vision analysis responses")
                return False
        else:
            print("[TEST] ❌ NO RESPONSE RECEIVED!")
            print("[TEST] ❌ Vision analysis may have failed or timed out")
            print("[TEST] ❌ Check server logs for errors")
            return False
            
    except websockets.exceptions.ConnectionRefused:
        print("[TEST] ❌ Could not connect to WebSocket server")
        print("[TEST] ❌ Make sure the server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"[TEST] ❌ Test failed with error: {e}")
        return False

async def main():
    """Main test function"""
    print("Vision Message Type Fix Test")
    print("="*40)
    print("This test verifies that the backend sends 'object-analysis-result'")
    print("instead of 'object-analysis-response' to match frontend expectations.")
    print()
    
    success = await test_vision_message_type()
    
    print("\n" + "="*60)
    if success:
        print("[TEST] 🎉 VISION MESSAGE TYPE FIX VERIFIED!")
        print("[TEST] 🎉 Vision analysis communication should now work!")
    else:
        print("[TEST] 💥 VISION MESSAGE TYPE FIX FAILED!")
        print("[TEST] 💥 Vision analysis communication will not work!")
    print("="*60)
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[TEST] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[TEST] Test failed with error: {e}")
        sys.exit(1)