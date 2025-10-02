#!/usr/bin/env python3
"""
Test script for vision analysis timeout fix
This script tests the WebSocket message handling for object analysis requests
"""

import asyncio
import json
import websockets
import base64
import sys
from pathlib import Path

async def test_vision_analysis():
    """Test the vision analysis WebSocket endpoint"""
    
    # Create a simple test image (1x1 pixel PNG in base64)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77yQAAAABJRU5ErkJggg=="
    
    try:
        # Connect to the WebSocket server
        uri = "ws://localhost:12393/client-ws"  # Default port
        print(f"Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket server")
            
            # Wait for initial messages
            await asyncio.sleep(2)
            
            # Send object analysis request
            analysis_request = {
                "type": "object-analysis-request",
                "analysisId": "test-123",
                "imageData": test_image_b64,
                "userQuestion": "What is this test image?",
                "timestamp": 1234567890
            }
            
            print("📤 Sending vision analysis request...")
            await websocket.send(json.dumps(analysis_request))
            
            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=35.0)
                data = json.loads(response)
                
                if data.get("type") == "object-analysis-result":
                    print("✅ Received analysis result:")
                    print(f"   Analysis ID: {data.get('analysisId')}")
                    print(f"   Result: {data.get('result')}")
                    return True
                elif data.get("type") == "error":
                    print(f"❌ Received error response: {data.get('error')}")
                    return False
                else:
                    print(f"📨 Received other message: {data.get('type')}")
                    
            except asyncio.TimeoutError:
                print("❌ Timeout waiting for analysis response (35 seconds)")
                return False
                
    except ConnectionRefusedError:
        print("❌ Could not connect to WebSocket server")
        print("   Make sure the server is running on localhost:12393")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

async def main():
    """Main test function"""
    print("🔍 Testing Vision Analysis Timeout Fix")
    print("=" * 50)
    
    success = await test_vision_analysis()
    
    print("=" * 50)
    if success:
        print("✅ Vision analysis test PASSED")
        sys.exit(0)
    else:
        print("❌ Vision analysis test FAILED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())