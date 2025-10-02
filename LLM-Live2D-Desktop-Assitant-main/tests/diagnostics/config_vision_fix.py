#!/usr/bin/env python3
"""
Vision Configuration Fix

This script creates the necessary configuration to enable Claude Vision API.
Run this script to set up the AWS endpoint configuration.
"""

import json
import os

def create_config_file():
    """Create configuration file with AWS endpoint"""
    
    config = {
        "httpBase": "https://your-aws-api-gateway-url.amazonaws.com/prod",
        "vision_enabled": True,
        "claude_model": "claude-3-sonnet-20240229",
        "vision_settings": {
            "max_image_size": 5242880,  # 5MB
            "supported_formats": ["jpeg", "jpg", "png", "webp"],
            "timeout": 30
        }
    }
    
    # Write to config file
    config_path = "config/vision_config.json"
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created vision configuration: {config_path}")
    print("⚠️  IMPORTANT: Update the httpBase URL with your actual AWS endpoint!")
    
    return config_path

def update_app_config():
    """Update main app configuration to include vision settings"""
    
    # Check if there's an existing config file to update
    config_files = [
        "config.json",
        "config/config.json", 
        "config/app_config.json"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Add vision settings
                config["vision_enabled"] = True
                config["httpBase"] = config.get("httpBase", "https://your-aws-api-gateway-url.amazonaws.com/prod")
                
                # Write back
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print(f"✅ Updated existing config: {config_file}")
                return config_file
                
            except Exception as e:
                print(f"⚠️  Could not update {config_file}: {e}")
    
    print("ℹ️  No existing config file found to update")
    return None

def main():
    """Main configuration setup"""
    print("🔧 Vision Configuration Fix")
    print("=" * 40)
    
    # Create vision config
    vision_config = create_config_file()
    
    # Update app config if exists
    app_config = update_app_config()
    
    print("\n📋 NEXT STEPS:")
    print("1. Update the httpBase URL in the config file with your actual AWS endpoint")
    print("2. Ensure your AWS Lambda function supports vision requests")
    print("3. Test the vision system with: python test_vision_standalone.py")
    
    print("\n🔗 AWS Endpoint Examples:")
    print("- API Gateway: https://abc123.execute-api.us-east-1.amazonaws.com/prod")
    print("- Lambda Function URL: https://abc123.lambda-url.us-east-1.on.aws/")
    print("- Custom Domain: https://api.yourdomain.com")
    
    print(f"\n✅ Configuration setup complete!")

if __name__ == "__main__":
    main()