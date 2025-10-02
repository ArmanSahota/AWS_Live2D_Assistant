#!/usr/bin/env python3
"""
Test script to trigger Claude Vision diagnostic logging
"""

import asyncio
import websockets
import json
import base64
from pathlib import Path

async def test_vision_diagnostic():
    """Test vision request to trigger diagnostic logging"""
    
    print("🧪 TESTING CLAUDE VISION DIAGNOSTIC")
    print("=" * 40)
    
    # Create a small test image (1x1 pixel PNG)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    try:
        async with websockets.connect("ws://localhost:8000/ws") as websocket:
            print("✅ Connected to WebSocket server")
            
            # Send vision analysis request
            vision_request = {
                "type": "object-analysis-request",
                "analysisId": "diagnostic_test_12345",
                "imageData": f"data:image/png;base64,{test_image_b64}",
                "userQuestion": "What is this?",
                "timestamp": 1234567890
            }
            
            print("📤 Sending vision analysis request...")
            await websocket.send(json.dumps(vision_request))
            
            # Wait for response
            print("⏳ Waiting for response (check server logs for diagnostic output)...")
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                print(f"📥 Received response: {len(response)} chars")
                
                # Check if we got the expected error
                if "ValidationException" in response:
                    print("✅ DIAGNOSTIC TRIGGERED: ValidationException error reproduced")
                    print("🔍 Check server logs for [CLAUDE DIAGNOSTIC] messages")
                else:
                    print("ℹ️  Response received without error - check logs anyway")
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout waiting for response")
                
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("💡 Make sure the server is running: python server.py")

if __name__ == "__main__":
    asyncio.run(test_vision_diagnostic())