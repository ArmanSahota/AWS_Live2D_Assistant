#!/usr/bin/env python3
"""
Vision Bias Diagnostic Tool
Adds detailed logging to identify gaming controller bias issues
"""

def create_diagnostic_patches():
    """Create diagnostic patches to validate the gaming controller bias hypothesis"""
    
    # Patch 1: Enhanced local analysis logging
    local_analysis_patch = '''
# ADD TO improved_vision_analyzer.py after line 173 in _predict_object_type():

print(f"\\n[LOCAL ANALYSIS DEBUG] ===== OBJECT TYPE PREDICTION =====")
print(f"[LOCAL ANALYSIS DEBUG] Image dimensions: {width}x{height}")
print(f"[LOCAL ANALYSIS DEBUG] Aspect ratio: {aspect_ratio:.2f}")
print(f"[LOCAL ANALYSIS DEBUG] Gaming controller criteria check:")
print(f"[LOCAL ANALYSIS DEBUG] - Aspect ratio 1.3-2.0: {1.3 < aspect_ratio < 2.0}")
print(f"[LOCAL ANALYSIS DEBUG] - Width 200-1200: {200 < width < 1200}")
print(f"[LOCAL ANALYSIS DEBUG] - Height 150-800: {150 < height < 800}")
print(f"[LOCAL ANALYSIS DEBUG] - Vertical symmetry > 0.5: {symmetry['vertical'] > 0.5}")
print(f"[LOCAL ANALYSIS DEBUG] PREDICTED TYPE: {object_type}")
print(f"[LOCAL ANALYSIS DEBUG] =======================================\\n")
'''

    # Patch 2: Category override logging  
    category_override_patch = '''
# ADD TO server.py after line 691 (after category assignment):

print(f"\\n[CATEGORY OVERRIDE DEBUG] ===== CATEGORY DECISION =====")
print(f"[CATEGORY OVERRIDE DEBUG] Local object type: {local_object_type}")
print(f"[CATEGORY OVERRIDE DEBUG] Claude category (from text): {claude_category}")
print(f"[CATEGORY OVERRIDE DEBUG] FINAL CATEGORY (after override): {category}")
print(f"[CATEGORY OVERRIDE DEBUG] Override applied: {local_object_type == 'gaming_controller'}")
print(f"[CATEGORY OVERRIDE DEBUG] =======================================\\n")
'''

    # Patch 3: Claude response logging
    claude_response_patch = '''
# ADD TO server.py after line 680 (after Claude analysis):

print(f"\\n[CLAUDE ANALYSIS DEBUG] ===== CLAUDE'S ACTUAL RESPONSE =====")
print(f"[CLAUDE ANALYSIS DEBUG] Response length: {len(response_text)} chars")
print(f"[CLAUDE ANALYSIS DEBUG] Claude's response: {response_text[:200]}...")
print(f"[CLAUDE ANALYSIS DEBUG] Category from Claude text: {_determine_object_category(response_text)}")
print(f"[CLAUDE ANALYSIS DEBUG] =======================================\\n")
'''

    return {
        'local_analysis': local_analysis_patch,
        'category_override': category_override_patch, 
        'claude_response': claude_response_patch
    }

def main():
    print("🔍 Vision Bias Diagnostic Tool")
    print("=" * 60)
    
    print("\n📋 HYPOTHESIS:")
    print("The system is hardcoded to detect gaming controllers due to:")
    print("1. Overly broad gaming controller detection criteria")
    print("2. Forced category override that ignores Claude's analysis")
    print("3. Keyboards match gaming controller criteria (aspect ratio, size, symmetry)")
    
    print("\n🧪 VALIDATION NEEDED:")
    print("Add the following diagnostic patches to confirm the hypothesis:")
    
    patches = create_diagnostic_patches()
    
    print("\n📝 PATCH 1 - Local Analysis Logging:")
    print("Add to improved_vision_analyzer.py in _predict_object_type():")
    print(patches['local_analysis'])
    
    print("\n📝 PATCH 2 - Category Override Logging:")
    print("Add to server.py after category assignment:")
    print(patches['category_override'])
    
    print("\n📝 PATCH 3 - Claude Response Logging:")
    print("Add to server.py after Claude analysis:")
    print(patches['claude_response'])
    
    print("\n🎯 EXPECTED RESULTS:")
    print("When you test with a keyboard, you should see:")
    print("- Local analysis incorrectly predicts 'gaming_controller'")
    print("- Claude's response mentions 'keyboard' or similar")
    print("- Category override forces 'gaming_controller' anyway")
    print("- Final response talks about PS5 controller despite Claude seeing keyboard")
    
    print("\n⚠️  CONFIRMATION NEEDED:")
    print("Please apply these patches and test with your keyboard.")
    print("Share the debug output to confirm this diagnosis before I implement fixes.")

if __name__ == "__main__":
    main()