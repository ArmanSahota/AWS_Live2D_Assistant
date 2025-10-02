#!/usr/bin/env python3
"""
Vision Analysis Test using HTTP API
Tests the vision analysis system using HTTP requests instead of WebSocket
"""

import base64
import json
import requests
import os
from PIL import Image
import io
from datetime import datetime

class VisionHTTPTestRunner:
    def __init__(self):
        self.test_photos_dir = "Test_Photos"
        self.http_base = "https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev"
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
                
                # Resize for reasonable file size (max 800x800)
                if img.size[0] > 800 or img.size[1] > 800:
                    img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                image_bytes = buffer.getvalue()
                
                base64_string = base64.b64encode(image_bytes).decode('utf-8')
                
                print(f"✅ Loaded {filename}: {img.size[0]}x{img.size[1]}, {len(base64_string)} chars")
                return base64_string
                
        except Exception as e:
            print(f"❌ Error loading {filename}: {str(e)}")
            return None
    
    def test_vision_analysis_http(self, test_case):
        """Test vision analysis using HTTP API"""
        print(f"\n🔍 Testing: {test_case['filename']}")
        print(f"📝 Description: {test_case['description']}")
        print(f"❓ Question: {test_case['question']}")
        
        # Load image
        image_base64 = self.load_image_as_base64(test_case['filename'])
        if not image_base64:
            return {
                "filename": test_case['filename'],
                "success": False,
                "error": "Failed to load image",
                "analysis": None
            }
        
        try:
            # Try different HTTP endpoints for vision analysis
            endpoints_to_try = [
                "/vision-analysis",
                "/analyze-image", 
                "/object-analysis",
                "/vision",
                "/claude-vision"
            ]
            
            for endpoint in endpoints_to_try:
                url = f"{self.http_base}{endpoint}"
                print(f"🔌 Trying endpoint: {url}")
                
                # Prepare request payload
                payload = {
                    "image": image_base64,
                    "question": test_case['question'],
                    "filename": test_case['filename']
                }
                
                headers = {
                    "Content-Type": "application/json"
                }
                
                try:
                    print(f"📤 Sending HTTP request...")
                    response = requests.post(url, json=payload, headers=headers, timeout=30)
                    
                    print(f"📥 Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        print(f"✅ Success! Response received from {endpoint}")
                        
                        # Extract analysis from response
                        analysis_text = ""
                        if "analysis" in response_data:
                            analysis_text = response_data["analysis"]
                        elif "result" in response_data:
                            if isinstance(response_data["result"], dict):
                                analysis_text = response_data["result"].get("analysis", str(response_data["result"]))
                            else:
                                analysis_text = str(response_data["result"])
                        elif "message" in response_data:
                            analysis_text = response_data["message"]
                        else:
                            analysis_text = str(response_data)
                        
                        print(f"📝 Analysis length: {len(analysis_text)} chars")
                        print(f"📝 Analysis preview: {analysis_text[:200]}...")
                        
                        # Validate analysis
                        is_real_analysis = self.validate_analysis(analysis_text, test_case)
                        
                        return {
                            "filename": test_case['filename'],
                            "success": True,
                            "analysis": analysis_text,
                            "endpoint": endpoint,
                            "is_real_analysis": is_real_analysis,
                            "response_data": response_data
                        }
                    
                    elif response.status_code == 404:
                        print(f"❌ Endpoint not found: {endpoint}")
                        continue
                    else:
                        print(f"❌ HTTP Error {response.status_code}: {response.text[:200]}")
                        continue
                        
                except requests.exceptions.Timeout:
                    print(f"⏰ Timeout for endpoint: {endpoint}")
                    continue
                except requests.exceptions.RequestException as e:
                    print(f"❌ Request error for {endpoint}: {str(e)}")
                    continue
            
            # If we get here, none of the endpoints worked
            return {
                "filename": test_case['filename'],
                "success": False,
                "error": "No working HTTP endpoints found",
                "analysis": None
            }
                        
        except Exception as e:
            print(f"❌ Error during HTTP vision test: {str(e)}")
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
            "misunderstanding",
            "error",
            "not found"
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
        is_detailed = len(analysis_text) > 50
        has_keywords = keyword_matches > 0
        
        print(f"📊 Analysis validation:")
        print(f"   Length: {len(analysis_text)} chars (detailed: {is_detailed})")
        print(f"   Keyword matches: {keyword_matches}/{len(test_case['expected_keywords'])}")
        print(f"   Real analysis: {is_detailed and has_keywords}")
        
        return is_detailed and has_keywords
    
    def run_all_tests(self):
        """Run vision analysis tests for all test images"""
        print("🚀 Starting HTTP Vision Analysis Tests")
        print("=" * 60)
        
        # Check if test photos exist
        if not os.path.exists(self.test_photos_dir):
            print(f"❌ Test photos directory not found: {self.test_photos_dir}")
            return
        
        print(f"📁 Test photos directory: {os.path.abspath(self.test_photos_dir)}")
        print(f"🌐 HTTP Base URL: {self.http_base}")
        
        # Run tests for each image
        for test_case in self.test_cases:
            result = self.test_vision_analysis_http(test_case)
            self.test_results.append(result)
        
        # Generate summary report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 HTTP VISION ANALYSIS TEST REPORT")
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
                print(f"   🌐 Endpoint: {result.get('endpoint', 'N/A')}")
                
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
        elif successful_tests < len(self.test_results):
            print("   ⚠️  VISION SYSTEM HAS CONNECTION ISSUES!")
            print("   ⚠️  Some tests failed to get responses")
            print("   🔧 Check HTTP API endpoints and server status")
        else:
            print("   ⚠️  MIXED RESULTS - PARTIAL FUNCTIONALITY")
            print("   🔧 Some images analyzed correctly, others failed")
        
        print(f"\n📁 Test completed at: {datetime.now().isoformat()}")

def main():
    """Main test function"""
    tester = VisionHTTPTestRunner()
    tester.run_all_tests()

if __name__ == "__main__":
    print("🔍 HTTP Vision Analysis Test with Test Photos")
    print("Testing Switch Controller, Keyboard, and Sprite Can via HTTP API")
    print("=" * 60)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")