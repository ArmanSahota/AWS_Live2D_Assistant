#!/usr/bin/env python3
"""
WebSocket Transmission Diagnostic Tool
Tests the WebSocket transmission fix for vision analysis timeout issues
"""

import asyncio
import websockets
import json
import base64
import time
from pathlib import Path

class WebSocketTransmissionDiagnostic:
    def __init__(self):
        self.analysis_id = None
        self.start_time = None
        self.received_response = False
        
    async def test_websocket_transmission(self):
        """Test WebSocket transmission with comprehensive logging"""
        
        # Load test image
        test_image_path = Path("Test_Photos/SwitchController.jpg")
        if not test_image_path.exists():
            print(f"❌ Test image not found: {test_image_path}")
            return False
            
        with open(test_image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        print("🔍 WEBSOCKET TRANSMISSION DIAGNOSTIC STARTING...")
        print(f"📸 Test image loaded: {len(image_data)} chars")
        
        try:
            # Connect to WebSocket
            uri = "ws://localhost:8000/client-ws"
            print(f"🔌 Connecting to {uri}...")
            
            async with websockets.connect(uri) as websocket:
                print("✅ WebSocket connected successfully")
                print(f"📊 WebSocket state: {websocket.state}")
                
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
                
                # Monitor WebSocket for response with detailed logging
                timeout_seconds = 90  # Extended timeout for debugging
                print(f"⏰ Monitoring WebSocket for response (timeout: {timeout_seconds}s)...")
                
                try:
                    while True:
                        response = await asyncio.wait_for(
                            websocket.recv(), 
                            timeout=timeout_seconds
                        )
                        
                        elapsed = time.time() - self.start_time
                        print(f"\n📥 WEBSOCKET MESSAGE RECEIVED after {elapsed:.2f}s")
                        
                        # Parse response
                        try:
                            data = json.loads(response)
                            message_type = data.get('type', 'UNKNOWN')
                            message_id = data.get('analysisId', 'NO_ID')
                            
                            print(f"📋 MESSAGE ANALYSIS:")
                            print(f"   Type: {message_type}")
                            print(f"   Analysis ID: {message_id}")
                            print(f"   Expected ID: {self.analysis_id}")
                            print(f"   ID Match: {message_id == self.analysis_id}")
                            print(f"   Message size: {len(response)} chars")
                            
                            # Check if this is our vision analysis response
                            if message_type in ['object-analysis-result', 'object-analysis-response']:
                                if message_id == self.analysis_id:
                                    print("🎯 VISION ANALYSIS RESPONSE MATCHED!")
                                    self.received_response = True
                                    
                                    if 'result' in data:
                                        result = data['result']
                                        print(f"📊 RESULT ANALYSIS:")
                                        print(f"   Category: {result.get('category', 'MISSING')}")
                                        print(f"   Confidence: {result.get('confidence', 'MISSING')}")
                                        print(f"   Analysis length: {len(result.get('analysis', ''))}")
                                        print(f"   Description: {result.get('description', 'MISSING')}")
                                        
                                        # Show first 200 chars of analysis
                                        analysis_text = result.get('analysis', '')
                                        if analysis_text:
                                            preview = analysis_text[:200] + "..." if len(analysis_text) > 200 else analysis_text
                                            print(f"   Analysis preview: {preview}")
                                    
                                    if 'error' in data:
                                        print(f"❌ ERROR IN RESPONSE: {data['error']}")
                                    
                                    print("✅ WEBSOCKET TRANSMISSION TEST SUCCESSFUL!")
                                    return True
                                else:
                                    print(f"⚠️  Vision response for different analysis ID: {message_id}")
                            else:
                                print(f"📨 Other message type: {message_type}")
                                
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON DECODE ERROR: {e}")
                            print(f"   Raw response (first 500 chars): {response[:500]}...")
                            
                except asyncio.TimeoutError:
                    elapsed = time.time() - self.start_time
                    print(f"\n⏰ TIMEOUT OCCURRED after {elapsed:.2f}s")
                    print("❌ No vision analysis response received within timeout period")
                    
                    print("\n🔍 TRANSMISSION FAILURE ANALYSIS:")
                    print("   1. ✅ WebSocket connection established successfully")
                    print("   2. ✅ Analysis request sent successfully")
                    print("   3. ❌ Vision analysis response not received")
                    print("   4. 🔍 Check server logs for WebSocket transmission errors")
                    print("   5. 🔍 Look for '[VISION ERROR]' messages in server output")
                    
                    return False
                    
        except Exception as e:
            print(f"❌ CONNECTION ERROR: {e}")
            print("   Check if server is running on port 8000")
            return False

async def main():
    diagnostic = WebSocketTransmissionDiagnostic()
    success = await diagnostic.test_websocket_transmission()
    
    print("\n" + "="*70)
    print("WEBSOCKET TRANSMISSION DIAGNOSTIC COMPLETE")
    print("="*70)
    
    if success:
        print("✅ RESULT: WebSocket transmission is working correctly!")
        print("   The timeout issue has been resolved.")
    else:
        print("❌ RESULT: WebSocket transmission is still failing.")
        print("   Check server logs for detailed error information.")
        
    print("\nNext steps:")
    print("1. Check server console for '[VISION DEBUG]' and '[VISION ERROR]' messages")
    print("2. Look for WebSocket state and message size information")
    print("3. Verify if message truncation occurred due to size limits")
    print("4. Check for retry attempts and their success/failure")

if __name__ == "__main__":
    asyncio.run(main())