#!/usr/bin/env python3
"""
Standalone Vision Analysis Test

This script tests the vision analysis system directly using the test photos
without requiring the WebSocket server to be running. It will help validate
whether the vision system components are working correctly.
"""

import base64
import json
import os
import sys
from PIL import Image
import io
from datetime import datetime

# Add the current directory to Python path to import modules
sys.path.append('.')

class StandaloneVisionTester:
    def __init__(self):
        self.test_photos_dir = "Test_Photos"
        self.test_results = []
        
        # Test cases
        self.test_cases = [
            {
                "filename": "SwitchController.jpg",
                "description": "Nintendo Switch Joy-Con controller",
                "expected_keywords": ["controller", "nintendo", "switch", "joy-con", "gaming", "buttons"],
                "question": "What gaming controller is this?"
            },
            {
                "filename": "Keyboard.jpg", 
                "description": "Computer keyboard",
                "expected_keywords": ["keyboard", "keys", "computer", "typing", "qwerty"],
                "question": "What type of input device is this?"
            },
            {
                "filename": "SodaPop.jpg",
                "description": "Can of Sprite soda",
                "expected_keywords": ["sprite", "soda", "can", "drink", "beverage", "green"],
                "question": "What beverage is this?"
            }
        ]
    
    def load_image_as_base64(self, filename):
        """Load image file and convert to base64"""
        try:
            filepath = os.path.join(self.test_photos_dir, filename)
            
            if not os.path.exists(filepath):
                print(f"❌ Image file not found: {filepath}")
                return None
            
            # Open and process image
            with Image.open(filepath) as img:
                print(f"📷 Original image: {img.size[0]}x{img.size[1]}, mode: {img.mode}")
                
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                    print(f"🔄 Converted to RGB mode")
                
                # Resize if too large (max 1024x1024 for testing)
                if img.size[0] > 1024 or img.size[1] > 1024:
                    original_size = img.size
                    img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                    print(f"📏 Resized from {original_size} to {img.size}")
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                image_bytes = buffer.getvalue()
                
                base64_string = base64.b64encode(image_bytes).decode('utf-8')
                
                print(f"✅ Processed {filename}: {img.size[0]}x{img.size[1]}, {len(image_bytes)} bytes, {len(base64_string)} base64 chars")
                return base64_string
                
        except Exception as e:
            print(f"❌ Error loading {filename}: {str(e)}")
            return None
    
    def test_local_vision_analyzer(self, test_case):
        """Test the local vision analyzer component"""
        print(f"\n🔍 Testing Local Vision Analyzer: {test_case['filename']}")
        
        # Load image
        image_data = self.load_image_as_base64(test_case['filename'])
        if not image_data:
            return {"success": False, "error": "Failed to load image"}
        
        try:
            # Try to import and use the improved vision analyzer
            from module.improved_vision_analyzer import ImprovedVisionAnalyzer
            
            print("📦 Imported ImprovedVisionAnalyzer")
            analyzer = ImprovedVisionAnalyzer()
            
            # Perform local analysis
            print("🔬 Performing local image analysis...")
            local_analysis = analyzer.analyze_image_locally(image_data)
            
            print(f"📊 Local analysis results:")
            print(f"   Object type: {local_analysis.get('object_type', 'unknown')}")
            print(f"   Dimensions: {local_analysis.get('dimensions', {})}")
            print(f"   Colors: {local_analysis.get('colors', {})}")
            print(f"   Visual description: {local_analysis.get('visual_description', 'N/A')}")
            
            return {
                "success": True,
                "method": "local_analysis",
                "analysis": local_analysis,
                "analyzer_type": "ImprovedVisionAnalyzer"
            }
            
        except ImportError as e:
            print(f"❌ Could not import ImprovedVisionAnalyzer: {e}")
            return {"success": False, "error": f"Import error: {e}"}
        except Exception as e:
            print(f"❌ Error in local analysis: {e}")
            return {"success": False, "error": f"Analysis error: {e}"}
    
    def test_claude_integration(self, test_case):
        """Test Claude LLM integration (without image for now)"""
        print(f"\n🤖 Testing Claude Integration: {test_case['filename']}")
        
        try:
            # Try to import and test Claude LLM
            from llm.claude import LLM
            
            print("📦 Imported Claude LLM")
            
            # Create a test prompt (text-only for now)
            test_prompt = f"""I'm testing the vision analysis system. Please respond with a detailed analysis of what you would expect to see in an image of: {test_case['description']}.

Question: {test_case['question']}

Please provide a detailed response as if you were analyzing the actual image."""
            
            # Initialize Claude (this will test the basic setup)
            claude = LLM(
                system="You are a helpful vision analysis assistant.",
                verbose=True
            )
            
            print("🔗 Testing Claude connection...")
            
            # Test basic chat functionality
            response_text = ""
            try:
                for chunk in claude.chat_iter(test_prompt):
                    response_text += chunk
                
                print(f"✅ Claude responded with {len(response_text)} characters")
                print(f"📝 Response preview: {response_text[:200]}...")
                
                return {
                    "success": True,
                    "method": "claude_text_only",
                    "response": response_text,
                    "response_length": len(response_text)
                }
                
            except Exception as e:
                print(f"❌ Claude chat error: {e}")
                return {"success": False, "error": f"Claude chat error: {e}"}
            
        except ImportError as e:
            print(f"❌ Could not import Claude LLM: {e}")
            return {"success": False, "error": f"Import error: {e}"}
        except Exception as e:
            print(f"❌ Error testing Claude: {e}")
            return {"success": False, "error": f"Claude error: {e}"}
    
    def test_vision_with_image(self, test_case):
        """Test vision analysis with actual image data"""
        print(f"\n👁️ Testing Vision with Image: {test_case['filename']}")
        
        # Load image
        image_data = self.load_image_as_base64(test_case['filename'])
        if not image_data:
            return {"success": False, "error": "Failed to load image"}
        
        try:
            # Try to use Claude with image data
            from llm.claude import LLM
            
            # Get the base URL from environment variable
            import os
            base_url = os.environ.get("HTTP_BASE", "https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev")
            
            claude = LLM(
                system="You are a helpful vision analysis assistant. Analyze images in detail.",
                base_url=base_url,
                verbose=True
            )
            
            vision_prompt = f"""Please analyze this image and answer: {test_case['question']}

Provide a detailed analysis including:
1. What objects you can see
2. Their characteristics and features
3. Colors and visual details
4. Answer to the specific question"""
            
            print("🖼️ Sending image to Claude...")
            print(f"   Image data length: {len(image_data)} chars")
            print(f"   Question: {test_case['question']}")
            
            # Test Claude with image data
            response_text = ""
            for chunk in claude.chat_iter(vision_prompt, image_data):
                response_text += chunk
            
            print(f"📥 Claude vision response: {len(response_text)} chars")
            print(f"📝 Response preview: {response_text[:200]}...")
            
            # Check if this looks like real vision analysis
            is_real_vision = self.validate_vision_response(response_text, test_case)
            
            return {
                "success": True,
                "method": "claude_vision",
                "response": response_text,
                "is_real_vision": is_real_vision,
                "image_sent": True
            }
            
        except Exception as e:
            print(f"❌ Error in vision test: {e}")
            return {"success": False, "error": f"Vision error: {e}"}
    
    def validate_vision_response(self, response_text, test_case):
        """Validate if response looks like real vision analysis"""
        
        # Check for "no image" indicators
        no_image_indicators = [
            "don't have access to any image",
            "can't see the image", 
            "no image provided",
            "unable to see",
            "cannot see the image",
            "I don't actually have access",
            "misunderstanding"
        ]
        
        response_lower = response_text.lower()
        
        for indicator in no_image_indicators:
            if indicator in response_lower:
                print(f"❌ DETECTED: '{indicator}' - This is NOT real vision analysis")
                return False
        
        # Check for expected keywords
        keyword_matches = 0
        for keyword in test_case['expected_keywords']:
            if keyword.lower() in response_lower:
                keyword_matches += 1
                print(f"✅ Found keyword: '{keyword}'")
        
        is_detailed = len(response_text) > 100
        has_keywords = keyword_matches > 0
        
        print(f"📊 Vision validation:")
        print(f"   Length: {len(response_text)} chars")
        print(f"   Keywords found: {keyword_matches}/{len(test_case['expected_keywords'])}")
        print(f"   Appears to be real vision: {is_detailed and has_keywords}")
        
        return is_detailed and has_keywords
    
    def run_all_tests(self):
        """Run all vision tests"""
        print("🚀 Starting Standalone Vision Analysis Tests")
        print("=" * 60)
        
        # Check if test photos exist
        if not os.path.exists(self.test_photos_dir):
            print(f"❌ Test photos directory not found: {self.test_photos_dir}")
            return
        
        print(f"📁 Test photos directory: {os.path.abspath(self.test_photos_dir)}")
        
        # List available photos
        photos = [f for f in os.listdir(self.test_photos_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"📷 Available photos: {photos}")
        
        # Run tests for each image
        for test_case in self.test_cases:
            print(f"\n{'='*60}")
            print(f"🖼️ TESTING: {test_case['filename']}")
            print(f"📝 Expected: {test_case['description']}")
            print(f"❓ Question: {test_case['question']}")
            print(f"{'='*60}")
            
            # Test 1: Local Vision Analyzer
            local_result = self.test_local_vision_analyzer(test_case)
            
            # Test 2: Claude Integration (text-only)
            claude_result = self.test_claude_integration(test_case)
            
            # Test 3: Vision with Image
            vision_result = self.test_vision_with_image(test_case)
            
            # Store results
            self.test_results.append({
                "filename": test_case['filename'],
                "local_analysis": local_result,
                "claude_text": claude_result,
                "claude_vision": vision_result
            })
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 STANDALONE VISION TEST REPORT")
        print("=" * 60)
        
        local_success = sum(1 for r in self.test_results if r['local_analysis']['success'])
        claude_success = sum(1 for r in self.test_results if r['claude_text']['success'])
        vision_success = sum(1 for r in self.test_results if r['claude_vision']['success'])
        real_vision = sum(1 for r in self.test_results if r['claude_vision'].get('is_real_vision', False))
        
        print(f"📈 COMPONENT TEST RESULTS:")
        print(f"   Local Analysis: {local_success}/{len(self.test_results)} successful")
        print(f"   Claude Text: {claude_success}/{len(self.test_results)} successful")
        print(f"   Claude Vision: {vision_success}/{len(self.test_results)} successful")
        print(f"   Real Vision Analysis: {real_vision}/{len(self.test_results)} detected")
        
        print(f"\n🎯 DIAGNOSIS:")
        
        if real_vision == len(self.test_results):
            print("   ✅ VISION SYSTEM IS WORKING!")
            print("   ✅ Claude Vision API is properly integrated")
            print("   ✅ Images are being sent to Claude successfully")
        elif vision_success == len(self.test_results) and real_vision == 0:
            print("   ❌ VISION SYSTEM IS BROKEN!")
            print("   ❌ Claude is NOT receiving image data")
            print("   ❌ System is using text-only simulation")
            print("   🔧 APPLY FIXES FROM IMMEDIATE_VISION_FIX_REQUIRED.md")
        elif local_success == len(self.test_results):
            print("   ⚠️ LOCAL ANALYSIS WORKING, CLAUDE VISION BROKEN")
            print("   ✅ Image processing components work")
            print("   ❌ Claude Vision API integration broken")
        else:
            print("   ❌ MULTIPLE COMPONENT FAILURES")
            print("   🔧 Check system setup and dependencies")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"\n🖼️ {result['filename']}:")
            
            # Local analysis
            if result['local_analysis']['success']:
                print(f"   ✅ Local Analysis: SUCCESS")
                obj_type = result['local_analysis']['analysis'].get('object_type', 'unknown')
                print(f"      Detected: {obj_type}")
            else:
                print(f"   ❌ Local Analysis: FAILED")
            
            # Claude text
            if result['claude_text']['success']:
                print(f"   ✅ Claude Text: SUCCESS")
            else:
                print(f"   ❌ Claude Text: FAILED")
            
            # Claude vision
            if result['claude_vision']['success']:
                if result['claude_vision'].get('is_real_vision'):
                    print(f"   ✅ Claude Vision: REAL ANALYSIS ✅")
                else:
                    print(f"   ⚠️ Claude Vision: FAKE RESPONSE ❌")
            else:
                print(f"   ❌ Claude Vision: FAILED")

def main():
    """Main test function"""
    tester = StandaloneVisionTester()
    tester.run_all_tests()

if __name__ == "__main__":
    print("🔍 Standalone Vision Analysis Test")
    print("Testing vision components with Switch Controller, Keyboard, and Sprite")
    print("=" * 60)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()