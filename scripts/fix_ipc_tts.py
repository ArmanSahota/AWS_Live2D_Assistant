#!/usr/bin/env python3
"""
Fix the TTS issue in ipc.js by removing JavaScript code from Python string
"""

import os

ipc_file = "LLM-Live2D-Desktop-Assitant-main/src/main/ipc.js"

# Read the file
with open(ipc_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and remove the problematic lines (299-300, 0-indexed so 298-299)
# These lines contain JavaScript inside a Python string which causes the error
if len(lines) > 299:
    # Check if these are the problematic lines
    if '// FIX: Escape text to prevent Python code injection' in lines[298]:
        # Remove lines 299-300 (index 298-299)
        del lines[298:300]
        print(f"✓ Removed problematic JavaScript lines from Python string")
        
        # Write the fixed file
        with open(ipc_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✓ Fixed {ipc_file}")
        print("✓ TTS should now work properly!")
    else:
        print("Lines don't match expected pattern. File may already be fixed.")
else:
    print("File structure unexpected")

print("\nNow restart the application to test TTS.")