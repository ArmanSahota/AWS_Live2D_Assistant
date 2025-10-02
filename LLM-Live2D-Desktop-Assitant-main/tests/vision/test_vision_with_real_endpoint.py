#!/usr/bin/env python3
"""
Test Vision System with Real AWS Endpoints

This script tests the vision system using the actual AWS endpoints
and Claude 3.7 Sonnet model to validate the fixes are working.
"""

import sys
import os
import json
sys.path.append('.')

# Import the configuration
def load_config():
    """Load configuration from app_config.json"""
    config_path = "config/app_config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return None

def test_vision_with_real_aws():
    """Test the vision system with real AWS endpoints"""
    
    print("🔧 Testing Vision System with Real AWS Endpoints")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Could not load configuration from config/app_config.json")
        return
    
    print(f"📡 HTTP Base: {config.get('httpBase')}")
    print(f"🔗 WebSocket URL: {config.get('wsUrl')}")
    print(f"🤖 Model ID: {config.get('modelId')}")
    print(f"👁️ Vision Enabled: {config.get('vision_enabled')}")
    
    # Patch the system to use the real configuration
    import unittest.mock
    
    # Mock the LLM initialization to use the real base_url
    def mock_llm_init(self, **kwargs):
        self.base_url = config.get('httpBase')
        self.system = kwargs.get('system', '')
        self.verbose = kwargs.get('verbose', False)
        self.messages = []
        print(f"[MOCK LLM] Initialized with base_url: {self.base_url}")
    
    with unittest.mock.patch.object(sys.modules['llm.claude'].LLM, '__init__', mock_llm_init):
        # Import and run the vision test
        from test_vision_standalone import StandaloneVisionTester
        
        print("\n🧪 Running vision tests with real AWS endpoints...")
        print(f"🎯 Expected: Real Claude 3.7 Sonnet vision analysis")
        
        # Run the test
        tester = StandaloneVisionTester()
        tester.run_all_tests()

def main():
    """Main test function"""
    try:
        test_vision_with_real_aws()
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 Vision System Test with Real AWS Endpoints")
    print("Testing with Claude 3.7 Sonnet and actual AWS infrastructure")
    print("=" * 60)
    
    main()