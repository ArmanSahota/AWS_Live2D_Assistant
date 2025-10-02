#!/usr/bin/env python3
"""
AWS Lambda Function for Claude Vision API

This is the AWS Lambda function code that needs to be deployed to handle
vision requests from the VTuber system.
"""

import json
import base64
import os
import boto3
from anthropic import Anthropic

def lambda_handler(event, context):
    """
    AWS Lambda handler for Claude Vision API requests
    
    Expected event format:
    {
        "body": {
            "text": "User prompt",
            "image": "base64_image_data",
            "has_vision": true,
            "system": "System prompt"
        }
    }
    """
    
    try:
        # Parse the request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        text = body.get('text', '')
        system = body.get('system', '')
        image_data = body.get('image')
        has_vision = body.get('has_vision', False)
        
        print(f"[LAMBDA] Processing request - Vision: {has_vision}, Text length: {len(text)}")
        if image_data:
            print(f"[LAMBDA] Image data length: {len(image_data)}")
        
        # Initialize Anthropic client
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        client = Anthropic(api_key=api_key)
        
        # Prepare messages
        messages = []
        
        if has_vision and image_data:
            print("[LAMBDA] Processing vision request")
            
            # Vision request with image
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_data
                        }
                    }
                ]
            })
            
            # Use Claude 3.7 Vision model
            model = "claude-3-7-sonnet-20250219"
            max_tokens = 1500  # More tokens for detailed vision analysis
            
        else:
            print("[LAMBDA] Processing text-only request")
            
            # Text-only request
            messages.append({
                "role": "user",
                "content": text
            })
            
            # Use Claude 3.7 model
            model = "claude-3-7-sonnet-20250219"
            max_tokens = 1000
        
        print(f"[LAMBDA] Using model: {model}")
        
        # Make API call to Claude
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system if system else "You are a helpful AI assistant with vision capabilities.",
            messages=messages
        )
        
        reply_text = response.content[0].text
        print(f"[LAMBDA] Claude response length: {len(reply_text)}")
        
        # Return successful response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'reply': reply_text,
                'model_used': model,
                'vision_processed': has_vision and bool(image_data),
                'tokens_used': response.usage.output_tokens if hasattr(response, 'usage') else None
            })
        }
        
    except Exception as e:
        print(f"[LAMBDA] Error: {str(e)}")
        
        # Return error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'error_type': type(e).__name__
            })
        }

# For local testing
if __name__ == "__main__":
    # Test the lambda function locally
    test_event = {
        'body': {
            'text': 'Hello, can you see this image?',
            'system': 'You are a helpful vision assistant.',
            'has_vision': False  # Set to True and add image data for vision testing
        }
    }
    
    result = lambda_handler(test_event, None)
    print("Test result:", json.dumps(result, indent=2))