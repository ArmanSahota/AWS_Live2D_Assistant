#!/usr/bin/env python3
"""
Vision Image Data Flow Diagnostic Tool

This diagnostic tool adds comprehensive logging to trace image data flow
from frontend capture through backend processing to Claude API calls.
"""

import json
import base64
from datetime import datetime

def create_image_flow_diagnostic_patch():
    """
    Creates diagnostic patches to trace image data flow through the system
    """
    
    # Patch 1: Frontend webcam capture logging
    frontend_patch = '''
// ADD TO webcam-manager.js in captureForAnalysis() method after line 299:

console.log('[WEBCAM DEBUG] ===== IMAGE CAPTURE DIAGNOSTIC =====');
console.log('[WEBCAM DEBUG] Raw image captured:', rawImage ? 'YES' : 'NO');
console.log('[WEBCAM DEBUG] Raw image length:', rawImage ? rawImage.length : 0);
console.log('[WEBCAM DEBUG] Raw image starts with data:image:', rawImage ? rawImage.startsWith('data:image') : false);
console.log('[WEBCAM DEBUG] Processed image:', processedImage ? 'YES' : 'NO');
console.log('[WEBCAM DEBUG] Processed image length:', processedImage ? processedImage.length : 0);
console.log('[WEBCAM DEBUG] =======================================');
'''

    # Patch 2: Frontend WebSocket transmission logging  
    websocket_patch = '''
// ADD TO vision-analysis-ui.js in sendForAnalysis() method after line 787:

console.log('[WEBSOCKET DEBUG] ===== IMAGE TRANSMISSION DIAGNOSTIC =====');
console.log('[WEBSOCKET DEBUG] Image data being sent:', imageData ? 'YES' : 'NO');
console.log('[WEBSOCKET DEBUG] Image data length:', imageData ? imageData.length : 0);
console.log('[WEBSOCKET DEBUG] Image data type:', typeof imageData);
console.log('[WEBSOCKET DEBUG] Image starts with data:image:', imageData ? imageData.startsWith('data:image') : false);
console.log('[WEBSOCKET DEBUG] Request message:', JSON.stringify(requestMessage, null, 2));
console.log('[WEBSOCKET DEBUG] =======================================');
'''

    # Patch 3: Backend WebSocket reception logging
    backend_patch = '''
# ADD TO server.py after line 642 in the object-analysis-request handler:

print(f"\\n[BACKEND DEBUG] ===== IMAGE RECEPTION DIAGNOSTIC =====")
print(f"[BACKEND DEBUG] Image data received: {'YES' if image_data else 'NO'}")
print(f"[BACKEND DEBUG] Image data type: {type(image_data)}")
print(f"[BACKEND DEBUG] Image data length: {len(image_data) if image_data else 0}")
if image_data:
    print(f"[BACKEND DEBUG] Image starts with data:image: {image_data.startswith('data:image') if isinstance(image_data, str) else 'N/A'}")
    # Extract base64 part if it's a data URL
    if isinstance(image_data, str) and image_data.startswith('data:image'):
        base64_part = image_data.split(',')[1] if ',' in image_data else image_data
        print(f"[BACKEND DEBUG] Base64 part length: {len(base64_part)}")
        try:
            decoded = base64.b64decode(base64_part)
            print(f"[BACKEND DEBUG] Successfully decoded base64, bytes length: {len(decoded)}")
        except Exception as e:
            print(f"[BACKEND DEBUG] Failed to decode base64: {e}")
print(f"[BACKEND DEBUG] =======================================\\n")
'''

    # Patch 4: Claude API call logging
    claude_patch = '''
# ADD TO claude.py in chat_iter() method after line 54:

print(f"\\n[CLAUDE API DEBUG] ===== CLAUDE REQUEST DIAGNOSTIC =====")
print(f"[CLAUDE API DEBUG] Prompt length: {len(prompt)} characters")
print(f"[CLAUDE API DEBUG] Image data provided: {'YES' if image_base64 else 'NO'}")
print(f"[CLAUDE API DEBUG] Image data length: {len(image_base64) if image_base64 else 0}")
print(f"[CLAUDE API DEBUG] Prompt preview: {prompt[:200]}...")
print(f"[CLAUDE API DEBUG] System prompt: {self.system[:100] if self.system else 'None'}...")
print(f"[CLAUDE API DEBUG] Payload keys: {list(payload.keys())}")
print(f"[CLAUDE API DEBUG] =======================================\\n")
'''

    return {
        'frontend_webcam': frontend_patch,
        'frontend_websocket': websocket_patch, 
        'backend_reception': backend_patch,
        'claude_api': claude_patch
    }

def analyze_current_implementation():
    """
    Analyze the current vision implementation to identify the root cause
    """
    
    analysis = {
        'diagnosis': 'IMAGE DATA NOT REACHING CLAUDE VISION API',
        'root_cause': 'Text-only simulation instead of actual vision processing',
        'evidence': [
            '1. claude.py chat_iter() method has image_base64 parameter but marks it as "not used"',
            '2. server.py uses ImprovedVisionAnalyzer which does LOCAL analysis only',
            '3. System generates "realistic prompt" to make Claude think it can see the image',
            '4. No actual image data is sent to Claude Vision API',
            '5. Claude responds with "I don\'t actually have access to any image" because it\'s true!'
        ],
        'current_flow': [
            '1. Frontend captures image correctly',
            '2. WebSocket sends image data to backend',
            '3. Backend receives image data',
            '4. ImprovedVisionAnalyzer analyzes image LOCALLY',
            '5. System generates text prompt describing what it "sees"',
            '6. Text-only prompt sent to Claude (NO IMAGE)',
            '7. Claude correctly responds that it cannot see any image'
        ],
        'required_fixes': [
            '1. Implement actual Claude Vision API integration',
            '2. Modify claude.py to handle image_base64 parameter properly',
            '3. Update payload to include image data in correct format',
            '4. Replace text simulation with real vision API calls',
            '5. Add proper error handling for vision API failures'
        ]
    }
    
    return analysis

def main():
    """Main diagnostic function"""
    
    print("🔍 Vision Image Data Flow Diagnostic")
    print("=" * 60)
    
    # Analyze current implementation
    analysis = analyze_current_implementation()
    
    print(f"\n🎯 DIAGNOSIS: {analysis['diagnosis']}")
    print(f"🔍 ROOT CAUSE: {analysis['root_cause']}")
    
    print(f"\n📋 EVIDENCE:")
    for evidence in analysis['evidence']:
        print(f"   {evidence}")
    
    print(f"\n🔄 CURRENT FLOW:")
    for step in analysis['current_flow']:
        print(f"   {step}")
    
    print(f"\n🔧 REQUIRED FIXES:")
    for fix in analysis['required_fixes']:
        print(f"   {fix}")
    
    # Generate diagnostic patches
    patches = create_image_flow_diagnostic_patch()
    
    print(f"\n📝 DIAGNOSTIC PATCHES:")
    print(f"\n1. Frontend Webcam Capture Logging:")
    print(patches['frontend_webcam'])
    
    print(f"\n2. Frontend WebSocket Transmission Logging:")
    print(patches['frontend_websocket'])
    
    print(f"\n3. Backend Image Reception Logging:")
    print(patches['backend_reception'])
    
    print(f"\n4. Claude API Call Logging:")
    print(patches['claude_api'])
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Apply the diagnostic patches above to confirm image data flow")
    print("2. Implement actual Claude Vision API integration in claude.py")
    print("3. Update server.py to use real vision API instead of text simulation")
    print("4. Test with actual image data being sent to Claude Vision API")
    
    print(f"\n⚠️  CRITICAL FINDING:")
    print("The system is working as designed - it's using LOCAL image analysis")
    print("combined with text prompts. Claude is correctly saying it can't see")
    print("the image because NO IMAGE is actually being sent to Claude!")

if __name__ == "__main__":
    main()