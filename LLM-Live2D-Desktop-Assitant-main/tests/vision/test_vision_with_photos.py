#!/usr/bin/env python3
"""
Vision Analysis Test with Test Photos

This script tests the vision analysis system using the provided test photos:
- SwitchController.jpg (Joy-Con Switch controller)
- Keyboard.jpg (Computer keyboard)
- SodaPop.jpg (Can of Sprite)

It will validate whether the vision system can properly analyze these images
and determine if the Claude Vision API integration is working correctly.
"""

import base64
import json
import asyncio
import websockets
import os
from PIL import Image
import io
from datetime import datetime

class VisionTestRunner:
    def __init__(self):
        self.test_photos_dir = "Test_Photos"
        self.websocket_url = "wss://sz0alheq5d.execute-api.us-west-2.amazonaws.com/dev"
        self.test_results = []
        
        # Test cases with expected analysis keywords
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
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize to much smaller size for WebSocket limits (max 32KB message)
                # Target around 300x300 to keep base64 under 30KB
                if img.size[0] > 300 or img.size[1] > 300:
                    img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=60)
                image_bytes = buffer.getvalue()
                
                base64_string = base64.b64encode(image_bytes).decode('utf-8')
                data_url = f"data:image/jpeg;base64,{base64_string}"
                
                print(f"✅ Loaded {filename}: {img.size[0]}x{img.size[1]}, {len(base64_string)} chars")
                return data_url
                
        except Exception as e:
            print(f"❌ Error loading {filename}: {str(e)}")
            return None
    
    async def test_vision_analysis(self, test_case):
        """Test vision analysis for a single image"""
        print(f"\n🔍 Testing: {test_case['filename']}")
        print(f"📝 Description: {test_case['description']}")
        print(f"❓ Question: {test_case['question']}")
        
        # Load image
        image_data = self.load_image_as_base64(test_case['filename'])
        if not image_data:
            return {
                "filename": test_case['filename'],
                "success": False,
                "error": "Failed to load image",
                "analysis": None
            }
        
        try:
            # Connect to WebSocket
            print(f"🔌 Connecting to {self.websocket_url}...")
            async with websockets.connect(self.websocket_url) as websocket:
                print("✅ Connected to WebSocket")
                
                # Create analysis request
                analysis_id = f"test_{test_case['filename']}_{int(datetime.now().timestamp())}"
                request_message = {
                    "type": "object-analysis-request",
                    "analysisId": analysis_id,
                    "imageData": image_data,
                    "userQuestion": test_case['question']
                }
                
                print(f"📤 Sending vision analysis request...")
                print(f"   Analysis ID: {analysis_id}")
                print(f"   Image data length: {len(image_data)}")
                print(f"   Question: {test_case['question']}")
                
                # Send request
                await websocket.send(json.dumps(request_message))
                
                # Wait for response (with timeout)
                print("⏳ Waiting for analysis response...")
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    response_data = json.loads(response)
                    
                    print(f"📥 Received response:")
                    print(f"   Type: {response_data.get('type')}")
                    print(f"   Analysis ID: {response_data.get('analysisId')}")
                    
                    if response_data.get('type') == 'object-analysis-response':
                        result = response_data.get('result', {})
                        analysis_text = result.get('analysis', '')
                        confidence = result.get('confidence', 0.0)
                        category = result.get('category', '')
                        
                        print(f"   Category: {category}")
                        print(f"   Confidence: {confidence}")
                        print(f"   Analysis length: {len(analysis_text)} chars")
                        print(f"   Analysis preview: {analysis_text[:200]}...")
                        
                        # Check if this looks like a real vision analysis
                        is_real_analysis = self.validate_analysis(analysis_text, test_case)
                        
                        return {
                            "filename": test_case['filename'],
                            "success": True,
                            "analysis": analysis_text,
                            "confidence": confidence,
                            "category": category,
                            "is_real_analysis": is_real_analysis,
                            "response_data": response_data
                        }
                    else:
                        print(f"❌ Unexpected response type: {response_data.get('type')}")
                        return {
                            "filename": test_case['filename'],
                            "success": False,
                            "error": f"Unexpected response type: {response_data.get('type')}",
                            "response_data": response_data
                        }
                        
                except asyncio.TimeoutError:
                    print("❌ Timeout waiting for response")
                    return {
                        "filename": test_case['filename'],
                        "success": False,
                        "error": "Timeout waiting for response",
                        "analysis": None
                    }
                    
        except Exception as e:
            print(f"❌ Error during vision test: {str(e)}")
            return {
                "filename": test_case['filename'],
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    def validate_analysis(self, analysis_text, test_case):
        """Validate if the analysis looks like real vision analysis"""
        
        # Check for common "no image" responses
        no_image_indicators = [
            "don't have access to any image",
            "can't see the image",
            "no image provided",
            "unable to see",
            "cannot see the image",
            "I don't actually have access",
            "misunderstanding"
        ]
        
        analysis_lower = analysis_text.lower()
        
        # If it contains "no image" indicators, it's not real analysis
        for indicator in no_image_indicators:
            if indicator in analysis_lower:
                print(f"❌ FAKE ANALYSIS DETECTED: Contains '{indicator}'")
                return False
        
        # Check for expected keywords
        keyword_matches = 0
        for keyword in test_case['expected_keywords']:
            if keyword.lower() in analysis_lower:
                keyword_matches += 1
                print(f"✅ Found expected keyword: '{keyword}'")
        
        # Check if analysis is detailed enough (real vision analysis should be detailed)
        is_detailed = len(analysis_text) > 100
        has_keywords = keyword_matches > 0
        
        print(f"📊 Analysis validation:")
        print(f"   Length: {len(analysis_text)} chars (detailed: {is_detailed})")
        print(f"   Keyword matches: {keyword_matches}/{len(test_case['expected_keywords'])}")
        print(f"   Real analysis: {is_detailed and has_keywords}")
        
        return is_detailed and has_keywords
    
    async def run_all_tests(self):
        """Run vision analysis tests for all test images"""
        print("🚀 Starting Vision Analysis Tests")
        print("=" * 60)
        
        # Check if test photos exist
        if not os.path.exists(self.test_photos_dir):
            print(f"❌ Test photos directory not found: {self.test_photos_dir}")
            return
        
        print(f"📁 Test photos directory: {os.path.abspath(self.test_photos_dir)}")
        
        # Run tests for each image
        for test_case in self.test_cases:
            result = await self.test_vision_analysis(test_case)
            self.test_results.append(result)
            
            # Brief pause between tests
            await asyncio.sleep(2)
        
        # Generate summary report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 VISION ANALYSIS TEST REPORT")
        print("=" * 60)
        
        successful_tests = sum(1 for r in self.test_results if r['success'])
        real_analyses = sum(1 for r in self.test_results if r.get('is_real_analysis', False))
        
        print(f"📈 SUMMARY:")
        print(f"   Total tests: {len(self.test_results)}")
        print(f"   Successful responses: {successful_tests}")
        print(f"   Real vision analyses: {real_analyses}")
        print(f"   Success rate: {successful_tests/len(self.test_results)*100:.1f}%")
        print(f"   Real analysis rate: {real_analyses/len(self.test_results)*100:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        
        for result in self.test_results:
            print(f"\n🖼️  {result['filename']}:")
            
            if result['success']:
                print(f"   ✅ Status: SUCCESS")
                print(f"   📊 Confidence: {result.get('confidence', 'N/A')}")
                print(f"   🏷️  Category: {result.get('category', 'N/A')}")
                
                if result.get('is_real_analysis'):
                    print(f"   🎯 Analysis: REAL VISION ANALYSIS ✅")
                else:
                    print(f"   ⚠️  Analysis: FAKE/PLACEHOLDER RESPONSE ❌")
                
                if result.get('analysis'):
                    print(f"   📝 Preview: {result['analysis'][:150]}...")
            else:
                print(f"   ❌ Status: FAILED")
                print(f"   🚫 Error: {result.get('error', 'Unknown error')}")
        
        # Diagnosis
        print(f"\n🎯 DIAGNOSIS:")
        
        if real_analyses == len(self.test_results):
            print("   ✅ VISION SYSTEM IS WORKING CORRECTLY!")
            print("   ✅ Claude Vision API is properly integrated")
            print("   ✅ All images were successfully analyzed")
        elif successful_tests == len(self.test_results) and real_analyses == 0:
            print("   ❌ VISION SYSTEM IS USING FAKE RESPONSES!")
            print("   ❌ Claude Vision API is NOT integrated")
            print("   ❌ System is using text-only simulation")
            print("   🔧 APPLY THE FIXES FROM IMMEDIATE_VISION_FIX_REQUIRED.md")
        elif successful_tests < len(self.test_results):
            print("   ⚠️  VISION SYSTEM HAS CONNECTION ISSUES!")
            print("   ⚠️  Some tests failed to get responses")
            print("   🔧 Check WebSocket connection and server status")
        else:
            print("   ⚠️  MIXED RESULTS - PARTIAL FUNCTIONALITY")
            print("   🔧 Some images analyzed correctly, others failed")
        
        print(f"\n📁 Test completed at: {datetime.now().isoformat()}")

async def main():
    """Main test function"""
    tester = VisionTestRunner()
    await tester.run_all_tests()

if __name__ == "__main__":
    print("🔍 Vision Analysis Test with Test Photos")
    print("Testing Switch Controller, Keyboard, and Sprite Can")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")