#!/usr/bin/env python3
"""
Vision Analysis Timeout Diagnostic Tool
Adds comprehensive logging to identify the exact cause of analysis timeouts
"""

import json
import asyncio
import websockets
import base64
import time
from pathlib import Path

class VisionTimeoutDiagnostic:
    def __init__(self):
        self.analysis_id = None
        self.start_time = None
        
    async def test_vision_analysis_flow(self):
        """Test the complete vision analysis flow with detailed logging"""
        
        # Load test image
        test_image_path = Path("Test_Photos/SwitchController.jpg")
        if not test_image_path.exists():
            print(f"❌ Test image not found: {test_image_path}")
            return
            
        with open(test_image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        print("🔍 VISION TIMEOUT DIAGNOSTIC STARTING...")
        print(f"📸 Test image loaded: {len(image_data)} chars")
        
        try:
            # Connect to WebSocket
            uri = "ws://localhost:8000/client-ws"
            print(f"🔌 Connecting to {uri}...")
            
            async with websockets.connect(uri) as websocket:
                print("✅ WebSocket connected successfully")
                
                # Generate analysis ID
                self.analysis_id = str(int(time.time() * 1000))
                self.start_time = time.time()
                
                print(f"🆔 Generated analysis ID: {self.analysis_id}")
                
                # Send analysis request
                request_message = {
                    "type": "object-analysis-request",
                    "analysisId": self.analysis_id,
                    "imageData": f"data:image/jpeg;base64,{image_data}",
                    "userQuestion": "What gaming controller is this?"
                }
                
                print("📤 SENDING ANALYSIS REQUEST...")
                print(f"   Type: {request_message['type']}")
                print(f"   Analysis ID: {request_message['analysisId']}")
                print(f"   Image data length: {len(request_message['imageData'])}")
                print(f"   Question: {request_message['userQuestion']}")
                
                await websocket.send(json.dumps(request_message))
                print("✅ Analysis request sent successfully")
                
                # Wait for response with detailed logging
                timeout_seconds = 45
                print(f"⏰ Waiting for response (timeout: {timeout_seconds}s)...")
                
                try:
                    response = await asyncio.wait_for(
                        websocket.recv(), 
                        timeout=timeout_seconds
                    )
                    
                    elapsed = time.time() - self.start_time
                    print(f"📥 RESPONSE RECEIVED after {elapsed:.2f}s")
                    
                    # Parse response
                    try:
                        data = json.loads(response)
                        print("📋 RESPONSE ANALYSIS:")
                        print(f"   Type: {data.get('type', 'MISSING')}")
                        print(f"   Analysis ID: {data.get('analysisId', 'MISSING')}")
                        print(f"   Expected ID: {self.analysis_id}")
                        print(f"   ID Match: {data.get('analysisId') == self.analysis_id}")
                        
                        if 'result' in data:
                            result = data['result']
                            print(f"   Result keys: {list(result.keys())}")
                            print(f"   Category: {result.get('category', 'MISSING')}")
                            print(f"   Confidence: {result.get('confidence', 'MISSING')}")
                            print(f"   Analysis length: {len(result.get('analysis', ''))}")
                        
                        if 'error' in data:
                            print(f"   Error: {data['error']}")
                            
                        print(f"📄 Full response: {json.dumps(data, indent=2)}")
                        
                        # Check for expected response type
                        expected_types = ["object-analysis-result", "object-analysis-response"]
                        actual_type = data.get('type')
                        
                        if actual_type in expected_types:
                            print("✅ RESPONSE TYPE VALID")
                        else:
                            print(f"❌ UNEXPECTED RESPONSE TYPE: {actual_type}")
                            print(f"   Expected one of: {expected_types}")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON DECODE ERROR: {e}")
                        print(f"   Raw response: {response[:500]}...")
                        
                except asyncio.TimeoutError:
                    elapsed = time.time() - self.start_time
                    print(f"⏰ TIMEOUT OCCURRED after {elapsed:.2f}s")
                    print("❌ No response received within timeout period")
                    
                    # This indicates the server is not sending a response
                    print("\n🔍 TIMEOUT ANALYSIS:")
                    print("   1. Server may be processing but not sending response")
                    print("   2. Response may have wrong message type")
                    print("   3. Analysis ID mismatch preventing client recognition")
                    print("   4. WebSocket connection issue during transmission")
                    
        except Exception as e:
            print(f"❌ CONNECTION ERROR: {e}")
            print("   Check if server is running on port 8000")

async def main():
    diagnostic = VisionTimeoutDiagnostic()
    await diagnostic.test_vision_analysis_flow()
    
    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)
    print("Next steps:")
    print("1. Check server logs for 'Sending vision analysis result to client'")
    print("2. Verify message type consistency (result vs response)")
    print("3. Confirm analysis ID matching between request/response")
    print("4. Test WebSocket message handler restoration")

if __name__ == "__main__":
    asyncio.run(main())