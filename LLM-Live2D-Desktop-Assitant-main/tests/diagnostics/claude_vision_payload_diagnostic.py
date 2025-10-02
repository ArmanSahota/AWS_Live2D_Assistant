#!/usr/bin/env python3
"""
Claude Vision Payload Diagnostic Tool

This script adds enhanced logging to the Claude client to capture the exact
payload structure being sent to AWS Bedrock for vision requests, helping
diagnose the ValidationException error.
"""

import json
from pathlib import Path

def create_diagnostic_patch():
    """Create diagnostic patch for Claude client"""
    
    print("🔍 CLAUDE VISION PAYLOAD DIAGNOSTIC")
    print("=" * 50)
    
    # Enhanced logging patch for claude.py
    claude_diagnostic_patch = '''
    # ADD AFTER LINE 182 in claude.py (after print(f"[CLAUDE VISION] Payload keys: {list(payload.keys())}"))
    
            # DIAGNOSTIC: Log the complete payload structure for vision requests
            if image_base64:
                print(f"[CLAUDE DIAGNOSTIC] ===== COMPLETE PAYLOAD STRUCTURE =====")
                print(f"[CLAUDE DIAGNOSTIC] Payload type: {type(payload)}")
                print(f"[CLAUDE DIAGNOSTIC] Payload keys: {list(payload.keys())}")
                
                # Log each payload field in detail
                for key, value in payload.items():
                    print(f"[CLAUDE DIAGNOSTIC] {key}: {type(value)}")
                    if key == "messages" and isinstance(value, list):
                        print(f"[CLAUDE DIAGNOSTIC] Messages array length: {len(value)}")
                        for i, msg in enumerate(value):
                            print(f"[CLAUDE DIAGNOSTIC] Message {i}: {type(msg)}")
                            if isinstance(msg, dict):
                                print(f"[CLAUDE DIAGNOSTIC] Message {i} keys: {list(msg.keys())}")
                                if "content" in msg:
                                    content = msg["content"]
                                    print(f"[CLAUDE DIAGNOSTIC] Message {i} content type: {type(content)}")
                                    if isinstance(content, list):
                                        print(f"[CLAUDE DIAGNOSTIC] Message {i} content length: {len(content)}")
                                        for j, item in enumerate(content):
                                            print(f"[CLAUDE DIAGNOSTIC] Content {j}: {type(item)}")
                                            if isinstance(item, dict):
                                                print(f"[CLAUDE DIAGNOSTIC] Content {j} keys: {list(item.keys())}")
                                                if "text" in item:
                                                    text_value = item["text"]
                                                    print(f"[CLAUDE DIAGNOSTIC] Content {j} text type: {type(text_value)}")
                                                    if isinstance(text_value, dict):
                                                        print(f"[CLAUDE DIAGNOSTIC] ❌ PROBLEM FOUND: text is dict, not string!")
                                                        print(f"[CLAUDE DIAGNOSTIC] text dict keys: {list(text_value.keys())}")
                                                    else:
                                                        print(f"[CLAUDE DIAGNOSTIC] ✅ text is string: {len(str(text_value))} chars")
                
                # Log the JSON structure (truncated for readability)
                try:
                    payload_json = json.dumps(payload, indent=2, default=str)
                    print(f"[CLAUDE DIAGNOSTIC] JSON payload preview (first 1000 chars):")
                    print(payload_json[:1000])
                    if len(payload_json) > 1000:
                        print("... (truncated)")
                except Exception as e:
                    print(f"[CLAUDE DIAGNOSTIC] Error serializing payload: {e}")
                
                print(f"[CLAUDE DIAGNOSTIC] ===== END PAYLOAD STRUCTURE =====")
    '''
    
    # Message normalization diagnostic patch
    normalization_diagnostic_patch = '''
    # ADD AFTER LINE 106 in claude.py (after the print statement in _normalize_messages_for_aws)
    
            # DIAGNOSTIC: Enhanced logging for message normalization
            if self.verbose:
                print(f"[CLAUDE DIAGNOSTIC] ===== MESSAGE NORMALIZATION DETAILS =====")
                for i, (original, normalized) in enumerate(zip(messages, normalized_messages)):
                    print(f"[CLAUDE DIAGNOSTIC] Message {i} normalization:")
                    print(f"[CLAUDE DIAGNOSTIC]   Original content type: {type(original.get('content'))}")
                    print(f"[CLAUDE DIAGNOSTIC]   Normalized content type: {type(normalized['content'])}")
                    
                    if isinstance(original.get('content'), list):
                        print(f"[CLAUDE DIAGNOSTIC]   Original content length: {len(original['content'])}")
                        for j, item in enumerate(original['content']):
                            if isinstance(item, dict) and item.get('type') == 'text':
                                print(f"[CLAUDE DIAGNOSTIC]   Original text item {j}: {type(item.get('text'))}")
                    
                    if isinstance(normalized['content'], list):
                        print(f"[CLAUDE DIAGNOSTIC]   Normalized content length: {len(normalized['content'])}")
                        for j, item in enumerate(normalized['content']):
                            if isinstance(item, dict) and item.get('type') == 'text':
                                print(f"[CLAUDE DIAGNOSTIC]   Normalized text item {j}: {type(item.get('text'))}")
                                if isinstance(item.get('text'), dict):
                                    print(f"[CLAUDE DIAGNOSTIC]   ❌ NORMALIZATION FAILED: text is still dict!")
                
                print(f"[CLAUDE DIAGNOSTIC] ===== END NORMALIZATION DETAILS =====")
    '''
    
    print("1️⃣ CLAUDE.PY PAYLOAD DIAGNOSTIC PATCH:")
    print("Add this after line 182 in claude.py:")
    print(claude_diagnostic_patch)
    
    print("\n2️⃣ CLAUDE.PY NORMALIZATION DIAGNOSTIC PATCH:")
    print("Add this after line 106 in claude.py:")
    print(normalization_diagnostic_patch)
    
    # Create a test script to trigger the diagnostic
    test_script = '''#!/usr/bin/env python3
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
'''
    
    # Write the test script
    with open("LLM-Live2D-Desktop-Assitant-main/test_claude_vision_diagnostic.py", "w") as f:
        f.write(test_script)
    
    print("\n3️⃣ DIAGNOSTIC TEST SCRIPT CREATED:")
    print("File: test_claude_vision_diagnostic.py")
    
    print("\n📋 NEXT STEPS:")
    print("1. Apply the diagnostic patches to claude.py")
    print("2. Restart the server: python server.py")
    print("3. Run diagnostic test: python test_claude_vision_diagnostic.py")
    print("4. Check server logs for [CLAUDE DIAGNOSTIC] messages")
    print("5. Look for '❌ PROBLEM FOUND: text is dict, not string!' messages")

if __name__ == "__main__":
    create_diagnostic_patch()