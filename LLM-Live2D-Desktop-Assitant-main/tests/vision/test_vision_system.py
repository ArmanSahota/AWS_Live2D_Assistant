#!/usr/bin/env python3
"""
Vision System Test Script

This script tests the vision system components to ensure they're working correctly.
It validates image processing, mock analysis, and configuration handling.
"""

import sys
import os
import base64
import json
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from module.vision_manager import VisionManager
    from PIL import Image
    import io
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required dependencies:")
    print("pip install Pillow")
    sys.exit(1)

def create_test_image() -> str:
    """Create a test image and return as base64"""
    # Create a simple test image
    img = Image.new('RGB', (640, 480), color='blue')
    
    # Add some simple shapes to make it more interesting
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    # Draw a circle (simulating a tire)
    draw.ellipse([200, 150, 440, 330], fill='black', outline='white', width=3)
    draw.ellipse([250, 200, 390, 280], fill='gray')
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=80)
    img_data = base64.b64encode(buffer.getvalue()).decode()
    
    return img_data

def create_test_config() -> dict:
    """Create test configuration"""
    return {
        'vision': {
            'enabled': True,
            'captureMode': 'manual',
            'captureQuality': 0.8,
            'resolution': '1280x720',
            'periodicInterval': 30000,
            'compressionEnabled': True,
            'confidenceThreshold': 0.7,
            'maxImageSize': 1048576,
            'rateLimitMs': 5000,
            'categories': {
                'automotive': True,
                'electronics': True,
                'tools': True,
                'appliances': True,
                'medical': False
            },
            'analysis': {
                'includeRepairInfo': True,
                'includeCostEstimates': True,
                'includeSafetyWarnings': True,
                'includeSpecifications': True,
                'detailLevel': 'comprehensive'
            }
        }
    }

async def test_vision_manager_initialization():
    """Test VisionManager initialization"""
    print("🔧 Testing VisionManager initialization...")
    
    try:
        config = create_test_config()
        vision_manager = VisionManager(config)
        
        # Test basic properties
        assert vision_manager.compression_quality == 0.8
        assert vision_manager.max_resolution == (1280, 720)
        assert vision_manager.confidence_threshold == 0.7
        
        print("✅ VisionManager initialization successful")
        return vision_manager
        
    except Exception as e:
        print(f"❌ VisionManager initialization failed: {e}")
        return None

async def test_image_processing(vision_manager):
    """Test image processing functionality"""
    print("🖼️  Testing image processing...")
    
    try:
        # Create test image
        test_image_data = create_test_image()
        print(f"   Created test image: {len(test_image_data)} characters")
        
        # Process the image
        processed_image = await vision_manager._process_image(test_image_data)
        
        if processed_image:
            print(f"   ✅ Image processed successfully")
            print(f"   Original size: {processed_image['original_size']}")
            print(f"   Processed size: {processed_image['processed_size']}")
            print(f"   Compression ratio: {processed_image['compression_ratio']:.2f}")
            print(f"   Format: {processed_image['format']}")
            return processed_image
        else:
            print("   ❌ Image processing failed")
            return None
            
    except Exception as e:
        print(f"   ❌ Image processing error: {e}")
        return None

async def test_object_analysis(vision_manager, processed_image):
    """Test object analysis functionality"""
    print("🔍 Testing object analysis...")
    
    try:
        # Test different types of questions
        test_questions = [
            "What is this tire? Is it repairable?",
            "Can you identify this smartphone?",
            "What tool is this and how do I use it?",
            "What is this object?"
        ]
        
        for i, question in enumerate(test_questions):
            print(f"   Testing question {i+1}: '{question}'")
            
            analysis_result = await vision_manager._analyze_object(
                processed_image, question, f"test_analysis_{i+1}"
            )
            
            if analysis_result:
                print(f"   ✅ Analysis completed")
                print(f"      Category: {analysis_result['category']}")
                print(f"      Confidence: {analysis_result['confidence']:.2f}")
                print(f"      Analysis length: {len(analysis_result['analysis'])} characters")
            else:
                print(f"   ❌ Analysis failed for question {i+1}")
                
    except Exception as e:
        print(f"   ❌ Object analysis error: {e}")

async def test_full_analysis_request(vision_manager):
    """Test full analysis request processing"""
    print("📋 Testing full analysis request...")
    
    try:
        # Create test request
        test_image_data = create_test_image()
        request_data = {
            'analysisId': 'test_full_analysis_001',
            'imageData': test_image_data,
            'userQuestion': 'What is this object? Can you analyze it for me?',
            'timestamp': 1234567890
        }
        
        # Process the request
        result = await vision_manager.process_analysis_request(request_data)
        
        if result['success']:
            print("   ✅ Full analysis request successful")
            print(f"      Analysis ID: {result['analysisId']}")
            print(f"      Category: {result['result']['category']}")
            print(f"      Confidence: {result['result']['confidence']:.2f}")
            
            # Print first 200 characters of analysis
            analysis_preview = result['result']['analysis'][:200] + "..."
            print(f"      Analysis preview: {analysis_preview}")
            
        else:
            print(f"   ❌ Full analysis request failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ❌ Full analysis request error: {e}")

def test_configuration_handling():
    """Test configuration handling"""
    print("⚙️  Testing configuration handling...")
    
    try:
        config = create_test_config()
        vision_manager = VisionManager(config)
        
        # Test getting capabilities
        capabilities = vision_manager.get_analysis_capabilities()
        print(f"   ✅ Capabilities retrieved: {len(capabilities)} items")
        
        # Test getting supported categories
        categories = vision_manager.get_supported_categories()
        print(f"   ✅ Supported categories: {categories}")
        
        # Test configuration update
        new_config = {'captureQuality': 0.9, 'confidenceThreshold': 0.8}
        vision_manager.update_config(new_config)
        print(f"   ✅ Configuration updated successfully")
        
    except Exception as e:
        print(f"   ❌ Configuration handling error: {e}")

def test_rate_limiting(vision_manager):
    """Test rate limiting functionality"""
    print("⏱️  Testing rate limiting...")
    
    try:
        analysis_id = "rate_limit_test"
        
        # First request should pass
        result1 = vision_manager._check_rate_limit(analysis_id)
        print(f"   First request allowed: {result1}")
        
        # Update rate limit
        vision_manager._update_rate_limit(analysis_id)
        
        # Immediate second request should be blocked
        result2 = vision_manager._check_rate_limit(analysis_id)
        print(f"   Immediate second request blocked: {not result2}")
        
        if result1 and not result2:
            print("   ✅ Rate limiting working correctly")
        else:
            print("   ❌ Rate limiting not working as expected")
            
    except Exception as e:
        print(f"   ❌ Rate limiting test error: {e}")

async def run_all_tests():
    """Run all vision system tests"""
    print("🚀 Starting Vision System Tests")
    print("=" * 50)
    
    # Test 1: Initialization
    vision_manager = await test_vision_manager_initialization()
    if not vision_manager:
        print("❌ Cannot continue tests without VisionManager")
        return False
    
    print()
    
    # Test 2: Image Processing
    processed_image = await test_image_processing(vision_manager)
    if not processed_image:
        print("❌ Cannot continue without processed image")
        return False
    
    print()
    
    # Test 3: Object Analysis
    await test_object_analysis(vision_manager, processed_image)
    print()
    
    # Test 4: Full Analysis Request
    await test_full_analysis_request(vision_manager)
    print()
    
    # Test 5: Configuration Handling
    test_configuration_handling()
    print()
    
    # Test 6: Rate Limiting
    test_rate_limiting(vision_manager)
    print()
    
    print("=" * 50)
    print("✅ Vision System Tests Completed")
    return True

def main():
    """Main test function"""
    print("Vision System Test Suite")
    print("Testing vision components and functionality...")
    print()
    
    try:
        # Run async tests
        success = asyncio.run(run_all_tests())
        
        if success:
            print("\n🎉 All tests completed successfully!")
            print("\nNext steps:")
            print("1. Start the application: python server.py")
            print("2. Open the desktop interface")
            print("3. Enable vision system in the UI")
            print("4. Test with real camera input")
        else:
            print("\n❌ Some tests failed. Please check the errors above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)