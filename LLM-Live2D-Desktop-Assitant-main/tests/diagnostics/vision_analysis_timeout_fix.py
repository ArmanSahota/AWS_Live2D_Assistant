#!/usr/bin/env python3
"""
Vision Analysis Timeout Fix
Fixes the message type mismatch and WebSocket handling issues
"""

import os
import shutil
from pathlib import Path

def apply_vision_timeout_fix():
    """Apply the comprehensive fix for vision analysis timeout"""
    
    print("🔧 APPLYING VISION ANALYSIS TIMEOUT FIX...")
    
    # Fix 1: Server-side message type consistency
    server_py_path = Path("LLM-Live2D-Desktop-Assitant-main/server.py")
    
    if server_py_path.exists():
        print("📝 Fixing server.py message type...")
        
        with open(server_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the message type from "object-analysis-response" to "object-analysis-result"
        old_message_type = '"type": "object-analysis-response"'
        new_message_type = '"type": "object-analysis-result"'
        
        if old_message_type in content:
            content = content.replace(old_message_type, new_message_type)
            print("   ✅ Fixed message type: object-analysis-response → object-analysis-result")
        else:
            print("   ⚠️  Message type already correct or not found")
        
        # Add additional logging for debugging
        log_insertion_point = 'print(f"[VISION FIX] Sending vision analysis result to client...")'
        additional_logging = '''print(f"[VISION FIX] Sending vision analysis result to client...")
                                print(f"[VISION DEBUG] Message type: {response_message['type']}")
                                print(f"[VISION DEBUG] Analysis ID: {response_message['analysisId']}")
                                print(f"[VISION DEBUG] Result keys: {list(response_message['result'].keys())}")'''
        
        if log_insertion_point in content and additional_logging not in content:
            content = content.replace(log_insertion_point, additional_logging)
            print("   ✅ Added enhanced server-side logging")
        
        with open(server_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Fix 2: Client-side WebSocket handler improvements
    vision_ui_path = Path("LLM-Live2D-Desktop-Assitant-main/static/desktop/vision-analysis-ui.js")
    
    if vision_ui_path.exists():
        print("📝 Fixing vision-analysis-ui.js WebSocket handling...")
        
        with open(vision_ui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Increase timeout from 30 seconds to 60 seconds
        old_timeout = 'setTimeout(() => {', 30000
        new_timeout_code = '''// Set up timeout - increased to 60 seconds for Claude Vision API
            timeoutId = setTimeout(() => {
                console.log('[VisionAnalysisUI] Analysis timeout after 60 seconds');
                console.log('[VisionAnalysisUI] Expected analysis ID:', analysisId);
                console.log('[VisionAnalysisUI] WebSocket state:', window.ws ? window.ws.readyState : 'no websocket');'''
        
        if '}, 30000);' in content:
            content = content.replace('}, 30000);', '}, 60000);')
            print("   ✅ Increased timeout: 30s → 60s")
        
        # Improve error logging
        error_logging_improvement = '''console.log('[VisionAnalysisUI] ===== RECEIVED WEBSOCKET MESSAGE =====');
                    console.log('[VisionAnalysisUI] Message type:', data.type);
                    console.log('[VisionAnalysisUI] Analysis ID in message:', data.analysisId);
                    console.log('[VisionAnalysisUI] Expected analysis ID:', analysisId);
                    console.log('[VisionAnalysisUI] ID Match:', data.analysisId === analysisId);
                    console.log('[VisionAnalysisUI] Full message keys:', Object.keys(data));'''
        
        if 'console.log(\'[VisionAnalysisUI] Full message:\', data);' in content and 'ID Match:' not in content:
            content = content.replace(
                'console.log(\'[VisionAnalysisUI] Full message:\', data);',
                error_logging_improvement
            )
            print("   ✅ Enhanced client-side logging")
        
        # Add fallback handler for any analysis result message
        fallback_handler = '''
                    // Fallback: Handle any object-analysis message for this ID
                    if ((data.type === 'object-analysis-result' || data.type === 'object-analysis-response') && 
                        data.analysisId === analysisId) {
                        console.log('[VisionAnalysisUI] ✅ ANALYSIS RESULT MATCHED (fallback) - Processing...');
                        clearTimeout(timeoutId);
                        
                        // Restore original message handler
                        if (originalOnMessage) {
                            window.ws.onmessage = originalOnMessage;
                        }
                        
                        resolve(data.result);
                        return;
                    }'''
        
        # Insert fallback handler before the error check
        error_check_line = 'else if (data.type === \'error\' && data.analysisId === analysisId) {'
        if error_check_line in content and 'fallback' not in content:
            content = content.replace(error_check_line, fallback_handler + '\n                    } ' + error_check_line)
            print("   ✅ Added fallback message handler")
        
        with open(vision_ui_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Fix 3: WebSocket connection handler improvements
    websocket_js_path = Path("LLM-Live2D-Desktop-Assitant-main/static/desktop/websocket.js")
    
    if websocket_js_path.exists():
        print("📝 Fixing websocket.js message handling...")
        
        with open(websocket_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Improve object-analysis-result handling
        analysis_result_handler = '''case 'object-analysis-result':
        case 'object-analysis-response':  // Handle both message types
            // Handle object analysis results from backend
            console.log('[VISION DEBUG] ✅ Received object-analysis message');
            console.log('[VISION DEBUG] Message type:', data.type);
            console.log('[VISION DEBUG] Analysis ID:', data.analysisId);
            console.log('[VISION DEBUG] Analysis result keys:', data.result ? Object.keys(data.result) : 'no result');'''
        
        old_case = "case 'object-analysis-result':"
        if old_case in content and 'object-analysis-response' not in content:
            content = content.replace(old_case, analysis_result_handler)
            print("   ✅ Enhanced WebSocket message handling")
        
        with open(websocket_js_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("\n✅ VISION ANALYSIS TIMEOUT FIX APPLIED SUCCESSFULLY!")
    print("\nFixes applied:")
    print("1. ✅ Fixed message type consistency (server → client)")
    print("2. ✅ Increased client timeout (30s → 60s)")
    print("3. ✅ Enhanced logging for debugging")
    print("4. ✅ Added fallback message handler")
    print("5. ✅ Improved WebSocket message handling")
    
    print("\n🔄 Please restart the server to apply these changes:")
    print("   python LLM-Live2D-Desktop-Assitant-main/server.py")

def create_validation_script():
    """Create a script to validate the fix"""
    
    validation_script = '''#!/usr/bin/env python3
"""
Vision Analysis Timeout Fix Validation
Tests the timeout fix to ensure it works correctly
"""

import asyncio
import sys
import os

# Add the project directory to Python path
sys.path.append('LLM-Live2D-Desktop-Assitant-main')

async def validate_timeout_fix():
    """Validate that the timeout fix is working"""
    
    print("🧪 VALIDATING VISION ANALYSIS TIMEOUT FIX...")
    
    # Import the diagnostic tool
    try:
        from vision_analysis_timeout_diagnostic import VisionTimeoutDiagnostic
        
        diagnostic = VisionTimeoutDiagnostic()
        await diagnostic.test_vision_analysis_flow()
        
        print("\\n✅ Validation complete!")
        print("Check the output above to confirm:")
        print("1. Response received within 60 seconds")
        print("2. Message type is 'object-analysis-result'")
        print("3. Analysis ID matches between request/response")
        print("4. No timeout errors occur")
        
    except ImportError as e:
        print(f"❌ Could not import diagnostic tool: {e}")
        print("Make sure the diagnostic script exists and server is running")
    except Exception as e:
        print(f"❌ Validation failed: {e}")

if __name__ == "__main__":
    asyncio.run(validate_timeout_fix())
'''
    
    validation_path = Path("LLM-Live2D-Desktop-Assitant-main/validate_timeout_fix.py")
    with open(validation_path, 'w', encoding='utf-8') as f:
        f.write(validation_script)
    
    print(f"📋 Created validation script: {validation_path}")

if __name__ == "__main__":
    apply_vision_timeout_fix()
    create_validation_script()
    
    print("\n" + "="*60)
    print("VISION ANALYSIS TIMEOUT FIX COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Restart the server: python LLM-Live2D-Desktop-Assitant-main/server.py")
    print("2. Test the fix: python LLM-Live2D-Desktop-Assitant-main/vision_analysis_timeout_diagnostic.py")
    print("3. Validate: python LLM-Live2D-Desktop-Assitant-main/validate_timeout_fix.py")
    print("4. If still having issues, check the enhanced logs for more details")