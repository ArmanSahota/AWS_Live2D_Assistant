#!/usr/bin/env python3
"""
Claude Conversation Diagnostic Tool

This tool adds comprehensive logging to diagnose the ValidationException error
that occurs after vision analysis when transitioning back to normal conversation.

The error: messages.2.content.0.text.text: Input should be a valid string
"""

def create_conversation_diagnostic_patch():
    """
    Creates diagnostic patches to identify the ValidationException source
    """
    
    # Patch 1: Enhanced conversation history logging in claude.py
    claude_diagnostic_patch = '''
# ADD TO claude.py after line 196 (after self.messages.append(user_message))

        # DIAGNOSTIC: Log conversation history state after adding user message
        print(f"[CLAUDE CONVERSATION DEBUG] ===== CONVERSATION HISTORY STATE =====")
        print(f"[CLAUDE CONVERSATION DEBUG] Total messages in history: {len(self.messages)}")
        for i, msg in enumerate(self.messages):
            print(f"[CLAUDE CONVERSATION DEBUG] Message {i}:")
            print(f"[CLAUDE CONVERSATION DEBUG]   Role: {msg.get('role', 'UNKNOWN')}")
            print(f"[CLAUDE CONVERSATION DEBUG]   Content type: {type(msg.get('content', 'NONE'))}")
            
            content = msg.get('content')
            if isinstance(content, list):
                print(f"[CLAUDE CONVERSATION DEBUG]   Content array length: {len(content)}")
                for j, item in enumerate(content):
                    print(f"[CLAUDE CONVERSATION DEBUG]   Content[{j}]: {type(item)}")
                    if isinstance(item, dict):
                        print(f"[CLAUDE CONVERSATION DEBUG]   Content[{j}] keys: {list(item.keys())}")
                        if item.get('type') == 'text' and 'text' in item:
                            text_value = item['text']
                            print(f"[CLAUDE CONVERSATION DEBUG]   Content[{j}] text type: {type(text_value)}")
                            if isinstance(text_value, dict):
                                print(f"[CLAUDE CONVERSATION DEBUG]   ❌ NESTED TEXT DETECTED: {list(text_value.keys())}")
                            else:
                                print(f"[CLAUDE CONVERSATION DEBUG]   ✅ Text is string: {len(str(text_value))} chars")
            elif isinstance(content, str):
                print(f"[CLAUDE CONVERSATION DEBUG]   Content string length: {len(content)}")
            else:
                print(f"[CLAUDE CONVERSATION DEBUG]   Content: {content}")
        
        print(f"[CLAUDE CONVERSATION DEBUG] ===== END CONVERSATION HISTORY =====")
'''

    # Patch 2: Enhanced normalization logging
    normalization_diagnostic_patch = '''
# ADD TO claude.py at the beginning of _normalize_messages_for_aws method (after line 118)

        print(f"[CLAUDE NORMALIZATION DEBUG] ===== STARTING MESSAGE NORMALIZATION =====")
        print(f"[CLAUDE NORMALIZATION DEBUG] Input messages count: {len(messages)}")
        print(f"[CLAUDE NORMALIZATION DEBUG] Image base64 provided: {image_base64 is not None}")
        
        # Log each input message structure
        for i, msg in enumerate(messages):
            print(f"[CLAUDE NORMALIZATION DEBUG] Input Message {i}:")
            print(f"[CLAUDE NORMALIZATION DEBUG]   Role: {msg.get('role')}")
            print(f"[CLAUDE NORMALIZATION DEBUG]   Content type: {type(msg.get('content'))}")
            
            content = msg.get('content')
            if isinstance(content, list):
                for j, item in enumerate(content):
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_val = item.get('text')
                        print(f"[CLAUDE NORMALIZATION DEBUG]   Content[{j}] text type: {type(text_val)}")
                        if isinstance(text_val, dict):
                            print(f"[CLAUDE NORMALIZATION DEBUG]   ❌ PROBLEM: Nested text structure detected!")
                            print(f"[CLAUDE NORMALIZATION DEBUG]   Nested keys: {list(text_val.keys())}")
'''

    # Patch 3: Post-normalization validation
    post_normalization_patch = '''
# ADD TO claude.py at the end of _normalize_messages_for_aws method (before return statement)

        # VALIDATION: Check normalized messages for remaining issues
        print(f"[CLAUDE NORMALIZATION DEBUG] ===== POST-NORMALIZATION VALIDATION =====")
        for i, msg in enumerate(normalized_messages):
            content = msg.get('content')
            if isinstance(content, list):
                for j, item in enumerate(content):
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_val = item.get('text')
                        if isinstance(text_val, dict):
                            print(f"[CLAUDE NORMALIZATION DEBUG] ❌ NORMALIZATION FAILED!")
                            print(f"[CLAUDE NORMALIZATION DEBUG] Message {i}, Content {j} still has nested text!")
                            print(f"[CLAUDE NORMALIZATION DEBUG] Nested structure: {text_val}")
                        else:
                            print(f"[CLAUDE NORMALIZATION DEBUG] ✅ Message {i}, Content {j} normalized correctly")
        
        print(f"[CLAUDE NORMALIZATION DEBUG] ===== END VALIDATION =====")
'''

    return {
        'conversation_history': claude_diagnostic_patch,
        'normalization_start': normalization_diagnostic_patch,
        'normalization_end': post_normalization_patch
    }

def create_conversation_reset_fix():
    """
    Creates a fix to properly reset conversation history after vision analysis
    """
    
    conversation_reset_fix = '''
# ADD TO claude.py after line 325 (after adding assistant response to history)

            # CRITICAL FIX: Clean conversation history after vision analysis
            if image_base64:
                print(f"[CLAUDE VISION FIX] Cleaning conversation history after vision analysis")
                
                # Remove vision messages that could cause structure issues
                cleaned_messages = []
                for msg in self.messages:
                    content = msg.get('content')
                    
                    # Skip messages with complex vision content structures
                    if isinstance(content, list):
                        has_image = any(item.get('type') == 'image' for item in content if isinstance(item, dict))
                        if has_image:
                            print(f"[CLAUDE VISION FIX] Removing vision message from history")
                            continue
                    
                    cleaned_messages.append(msg)
                
                self.messages = cleaned_messages
                print(f"[CLAUDE VISION FIX] Conversation history cleaned: {len(self.messages)} messages remaining")
'''
    
    return conversation_reset_fix

def main():
    """
    Main function to display diagnostic patches and fixes
    """
    print("🔍 CLAUDE CONVERSATION VALIDATION ERROR DIAGNOSTIC")
    print("=" * 60)
    
    print("\n📋 PROBLEM SUMMARY:")
    print("After vision analysis, normal conversation fails with:")
    print("ValidationException: messages.2.content.0.text.text: Input should be a valid string")
    print("\nThis suggests nested text structures in conversation history (index 2 = 3rd message)")
    
    print("\n🎯 MOST LIKELY CAUSES:")
    print("1. Vision messages with complex content structures persist in conversation history")
    print("2. Message normalization doesn't handle all nested structure patterns")
    
    print("\n🔧 DIAGNOSTIC PATCHES:")
    print("Apply these patches to claude.py to identify the exact issue:")
    
    patches = create_conversation_diagnostic_patch()
    
    print("\n📝 PATCH 1 - Conversation History Logging:")
    print("Add to claude.py after line 196:")
    print(patches['conversation_history'])
    
    print("\n📝 PATCH 2 - Normalization Start Logging:")
    print("Add to claude.py at beginning of _normalize_messages_for_aws method:")
    print(patches['normalization_start'])
    
    print("\n📝 PATCH 3 - Post-Normalization Validation:")
    print("Add to claude.py at end of _normalize_messages_for_aws method:")
    print(patches['normalization_end'])
    
    print("\n🛠️ POTENTIAL FIX:")
    print("Add to claude.py after vision analysis completion:")
    fix = create_conversation_reset_fix()
    print(fix)
    
    print("\n🧪 TESTING PROCEDURE:")
    print("1. Apply diagnostic patches to claude.py")
    print("2. Restart server: python LLM-Live2D-Desktop-Assitant-main/server.py")
    print("3. Perform vision analysis with an image")
    print("4. Try normal conversation after vision analysis")
    print("5. Check logs for nested text structure issues")
    print("6. Apply the conversation reset fix if nested structures are found")
    
    print("\n⚠️  IMPORTANT:")
    print("The error occurs at messages.2 (3rd message), suggesting the issue is in")
    print("conversation history management, not the current message being sent.")

if __name__ == "__main__":
    main()