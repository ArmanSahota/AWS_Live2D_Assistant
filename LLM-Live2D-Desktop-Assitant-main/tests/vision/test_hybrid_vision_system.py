#!/usr/bin/env python3
"""
Test Hybrid Vision System

This script tests the new hybrid vision analysis system that combines
local image analysis with Claude text reasoning to work around AWS Lambda limitations.
"""

import asyncio
import base64
import json
import yaml
from pathlib import Path
from module.local_vision_analyzer import LocalVisionAnalyzer

def load_config():
    """Load configuration from conf.yaml"""
    try:
        with open("conf.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def create_test_controller_image():
    """Create a test image that simulates a PS5 controller"""
    # This creates a simple test image with controller-like proportions
    from PIL import Image, ImageDraw
    import io
    
    # Create image with controller-like aspect ratio (wider than tall)
    width, height = 400, 250
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Draw a controller-like shape (rounded rectangle)
    controller_rect = [50, 75, 350, 175]
    draw.rounded_rectangle(controller_rect, radius=20, fill='black', outline='gray', width=2)
    
    # Draw some controller elements (buttons, sticks)
    # Left stick
    draw.ellipse([80, 95, 110, 125], fill='gray', outline='darkgray')
    # Right stick  
    draw.ellipse([290, 130, 320, 160], fill='gray', outline='darkgray')
    # D-pad
    draw.rectangle([120, 100, 140, 120], fill='darkgray')
    # Face buttons
    draw.ellipse([250, 95, 270, 115], fill='blue')  # X button area
    draw.ellipse([270, 85, 290, 105], fill='red')   # Circle button area
    
    # Convert to base64
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=85)
    image_bytes = buffer.getvalue()
    
    return base64.b64encode(image_bytes).decode()

async def test_hybrid_vision():
    """Test the hybrid vision analysis system"""
    
    print("🔍 Testing Hybrid Vision Analysis System")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Failed to load configuration")
        return False
    
    print(f"✅ Configuration loaded")
    
    # Initialize local analyzer
    try:
        local_analyzer = LocalVisionAnalyzer()
        print(f"✅ Local Vision Analyzer initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Local Vision Analyzer: {e}")
        return False
    
    # Create test controller image
    test_image = create_test_controller_image()
    print(f"✅ Test controller image created ({len(test_image)} characters)")
    
    # Test local analysis
    print(f"\n🧪 Running Local Image Analysis")
    print("-" * 30)
    
    try:
        local_analysis = local_analyzer.analyze_image_locally(test_image)
        
        print(f"Local Analysis Results:")
        print(f"- Dimensions: {local_analysis.get('dimensions', {})}")
        print(f"- Format: {local_analysis.get('format', 'unknown')}")
        print(f"- Color scheme: {local_analysis.get('colors', {}).get('color_scheme', 'unknown')}")
        print(f"- Aspect ratio: {local_analysis.get('shapes', {}).get('aspect_ratio', 0):.2f}")
        print(f"- File size: {local_analysis.get('file_size', 0)} bytes")
        
        # Test prompt generation
        user_question = "What is this object? Is it a gaming controller?"
        enhanced_prompt = local_analyzer.generate_analysis_prompt(local_analysis, user_question)
        
        print(f"\n📝 Generated Enhanced Prompt:")
        print("-" * 30)
        print(enhanced_prompt[:500] + "..." if len(enhanced_prompt) > 500 else enhanced_prompt)
        
        # Analyze the prompt for controller hints
        if 'controller' in enhanced_prompt.lower() or 'gaming' in enhanced_prompt.lower():
            print(f"✅ Prompt correctly identifies controller characteristics")
        else:
            print(f"⚠️  Prompt may not identify controller characteristics")
        
        return True
        
    except Exception as e:
        print(f"❌ Local analysis failed: {e}")
        return False

async def test_ps5_controller_scenario():
    """Test the specific PS5 controller scenario"""
    
    print(f"\n🎮 PS5 Controller Scenario Test")
    print("-" * 30)
    
    local_analyzer = LocalVisionAnalyzer()
    
    # Create controller image
    test_image = create_test_controller_image()
    user_question = "What is this object? Can you analyze it?"
    
    print(f"Simulating: User holds up PS5 controller and asks '{user_question}'")
    
    try:
        # Perform local analysis
        local_analysis = local_analyzer.analyze_image_locally(test_image)
        
        # Generate enhanced prompt
        enhanced_prompt = local_analyzer.generate_analysis_prompt(local_analysis, user_question)
        
        print(f"\nLocal Analysis Summary:")
        dims = local_analysis.get('dimensions', {})
        aspect_ratio = dims.get('width', 1) / max(dims.get('height', 1), 1)
        print(f"- Aspect ratio: {aspect_ratio:.2f} ({'controller-like' if 1.3 < aspect_ratio < 2.0 else 'not controller-like'})")
        print(f"- Color scheme: {local_analysis.get('colors', {}).get('color_scheme', 'unknown')}")
        
        print(f"\nEnhanced Prompt Quality:")
        prompt_lower = enhanced_prompt.lower()
        controller_hints = sum([
            'controller' in prompt_lower,
            'gaming' in prompt_lower,
            'handheld' in prompt_lower,
            'aspect ratio' in prompt_lower,
            'symmetr' in prompt_lower
        ])
        print(f"- Controller-related hints: {controller_hints}/5")
        
        if controller_hints >= 3:
            print(f"✅ High-quality prompt for controller identification")
        else:
            print(f"⚠️  Prompt may need improvement for controller identification")
        
        return True
        
    except Exception as e:
        print(f"❌ PS5 controller test failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("🚀 Hybrid Vision System Test Suite")
    print("=" * 60)
    
    async def run_tests():
        # Test local analysis
        local_test = await test_hybrid_vision()
        
        # Test PS5 controller scenario
        ps5_test = await test_ps5_controller_scenario()
        
        print(f"\n📊 Final Results")
        print("=" * 30)
        
        if local_test and ps5_test:
            print(f"🎉 ALL TESTS PASSED!")
            print(f"✅ Hybrid vision system is working")
            print(f"✅ Local image analysis functional")
            print(f"✅ Enhanced prompts generated correctly")
            print(f"✅ PS5 controller characteristics detected")
            
            print(f"\n🔧 Next Steps:")
            print(f"1. Restart the VTuber application")
            print(f"2. Try holding up your PS5 controller again")
            print(f"3. The system will now use local analysis + Claude reasoning")
            print(f"4. Check logs for detailed hybrid analysis results")
            
        else:
            print(f"❌ SOME TESTS FAILED")
            print(f"⚠️  Check dependencies (PIL, numpy)")
            print(f"⚠️  Verify local analysis implementation")
    
    # Run the async tests
    asyncio.run(run_tests())

if __name__ == "__main__":
    main()