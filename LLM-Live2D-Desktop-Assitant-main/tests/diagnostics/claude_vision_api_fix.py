#!/usr/bin/env python3
"""
Claude Vision API Integration Fix

This script provides the complete fix to enable actual Claude Vision API
integration instead of the current text-only simulation approach.
"""

def create_claude_vision_fix():
    """
    Creates the complete fix for Claude Vision API integration
    """
    
    # Fix 1: Update claude.py to handle image data properly
    claude_py_fix = '''
# REPLACE the chat_iter method in claude.py with this implementation:

def chat_iter(self, prompt: str, image_base64=None) -> Iterator[str]:
    """
    Send message to Claude via AWS HTTP endpoint and yield response tokens.
    
    Args:
        prompt (str): User message
        image_base64 (str, optional): Base64 encoded image for vision analysis
        
    Yields:
        str: Response tokens
    """
    # Add user message to history
    user_message = {"role": "user", "content": prompt}
    
    # If image is provided, format as vision message
    if image_base64:
        # Remove data URL prefix if present
        if image_base64.startswith('data:image'):
            image_base64 = image_base64.split(',')[1]
        
        user_message["content"] = [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_base64
                }
            }
        ]
    
    self.messages.append(user_message)
    
    try:
        if self.verbose:
            print(f"Sending request to AWS HTTP endpoint: {self.base_url}/claude")
            if image_base64:
                print(f"[VISION] Including image data ({len(image_base64)} chars)")
        
        # Prepare the payload with system prompt and conversation history
        payload = {
            "text": prompt,
            "system": self.system if self.system else ""
        }
        
        # Include image data if provided
        if image_base64:
            payload["image"] = image_base64
            payload["has_vision"] = True
        
        # Include conversation history if available
        if len(self.messages) > 1:  # More than just the current user message
            payload["messages"] = self.messages
        
        # Send request to AWS HTTP endpoint
        response = requests.post(
            f"{self.base_url}/claude",
            json=payload,
            timeout=60  # 60 second timeout
        )
        
        # Check for errors
        if response.status_code != 200:
            error_msg = f"HTTP error {response.status_code}: {response.text}"
            if self.verbose:
                print(error_msg)
            yield error_msg
            return
        
        # Parse the response
        data = response.json()
        if "reply" not in data:
            error_msg = "Invalid response format: missing 'reply' field"
            if self.verbose:
                print(error_msg)
            yield error_msg
            return
        
        # Get the response text
        response_text = data["reply"]
        
        # Simulate streaming by yielding characters one by one
        for char in response_text:
            yield char
        
        # Add assistant response to history
        self.messages.append({
            "role": "assistant", 
            "content": response_text
        })
            
    except Exception as e:
        if self.verbose:
            print(f"Error in Claude chat via AWS HTTP: {str(e)}")
        yield f"Error occurred: {str(e)}"
'''

    # Fix 2: Update server.py to use actual vision API
    server_py_fix = '''
# REPLACE the object-analysis-request handler in server.py (around line 635) with:

elif data.get("type") == "object-analysis-request":
    analysis_id = data.get("analysisId")
    image_data = data.get("imageData")
    user_question = data.get("userQuestion", "What is this object?")
    
    print(f"\\n[VISION DEBUG] ===== OBJECT ANALYSIS REQUEST RECEIVED =====")
    print(f"[VISION DEBUG] Analysis ID: {analysis_id}")
    print(f"[VISION DEBUG] Image data length: {len(image_data) if image_data else 0}")
    print(f"[VISION DEBUG] User question: {user_question}")
    print(f"[VISION DEBUG] Using REAL Claude Vision API")
    
    logger.info(f"[VISION] Received object analysis request: {analysis_id}")
    
    try:
        # Process the image analysis using REAL Claude Vision API
        if image_data and open_llm_vtuber:
            print(f"[VISION DEBUG] Processing with Claude Vision API...")
            
            # Clean up image data (remove data URL prefix if present)
            clean_image_data = image_data
            if image_data.startswith('data:image'):
                clean_image_data = image_data.split(',')[1]
            
            # Create vision-specific prompt
            vision_prompt = f"""Please analyze this image and answer the user's question: "{user_question}"

Provide a detailed analysis including:
1. What objects you can see in the image
2. Their characteristics, colors, and features
3. Any text or labels visible
4. The context or setting
5. Answer to the specific question asked

Be specific and detailed in your response."""
            
            print(f"[VISION DEBUG] Sending image to Claude Vision API...")
            
            # Use Claude Vision API with actual image data
            response_text = ""
            for chunk in open_llm_vtuber.llm.chat_iter(vision_prompt, clean_image_data):
                response_text += chunk
            
            print(f"[VISION DEBUG] Claude Vision API response received")
            print(f"[VISION DEBUG] Response length: {len(response_text)} characters")
            
            # Create analysis result
            analysis_result = {
                "category": "vision_analysis",
                "confidence": 0.9,  # High confidence since using real vision API
                "analysis": response_text,
                "description": "Analysis performed using Claude Vision API",
                "details": {
                    "method": "claude_vision_api",
                    "image_processed": True,
                    "api_used": "anthropic_claude_vision"
                }
            }
            
            # Send response back to client
            response_message = {
                "type": "object-analysis-result",
                "analysisId": analysis_id,
                "result": analysis_result
            }
            
            print(f"[VISION DEBUG] Sending response to client...")
            await websocket.send_text(json.dumps(response_message))
            
        else:
            # Handle missing data
            error_result = {
                "category": "error",
                "confidence": 0.0,
                "analysis": "Unable to process image: missing image data or LLM not available",
                "description": "Vision analysis failed",
                "details": {
                    "error": "Missing required components",
                    "has_image": bool(image_data),
                    "has_llm": bool(open_llm_vtuber)
                }
            }
            
            response_message = {
                "type": "object-analysis-result",
                "analysisId": analysis_id,
                "result": error_result
            }
            
            await websocket.send_text(json.dumps(response_message))
            
    except Exception as e:
        logger.error(f"[VISION] Error processing analysis request: {str(e)}")
        
        # Send error response
        error_result = {
            "category": "error",
            "confidence": 0.0,
            "analysis": f"Vision analysis failed: {str(e)}",
            "description": "Error during vision processing",
            "details": {
                "error": str(e),
                "error_type": type(e).__name__
            }
        }
        
        response_message = {
            "type": "object-analysis-result",
            "analysisId": analysis_id,
            "result": error_result
        }
        
        await websocket.send_text(json.dumps(response_message))
'''

    # Fix 3: AWS Lambda function update (if using AWS)
    aws_lambda_fix = '''
# UPDATE your AWS Lambda function to handle vision requests:

import json
import base64
import boto3
from anthropic import Anthropic

def lambda_handler(event, context):
    try:
        # Parse the request
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        
        text = body.get('text', '')
        system = body.get('system', '')
        image_data = body.get('image')
        has_vision = body.get('has_vision', False)
        
        # Initialize Anthropic client
        client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
        
        # Prepare messages
        messages = []
        
        if has_vision and image_data:
            # Vision request
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
            
            # Use Claude 3 Vision model
            model = "claude-3-sonnet-20240229"
        else:
            # Text-only request
            messages.append({
                "role": "user", 
                "content": text
            })
            
            # Use regular Claude model
            model = "claude-3-haiku-20240307"
        
        # Make API call
        response = client.messages.create(
            model=model,
            max_tokens=1000,
            system=system,
            messages=messages
        )
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'reply': response.content[0].text
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
'''

    return {
        'claude_py': claude_py_fix,
        'server_py': server_py_fix,
        'aws_lambda': aws_lambda_fix
    }

def main():
    """Main function to display the complete fix"""
    
    print("🔧 Claude Vision API Integration Fix")
    print("=" * 60)
    
    print("\n🎯 PROBLEM IDENTIFIED:")
    print("The system is using LOCAL image analysis + text simulation")
    print("instead of sending actual images to Claude Vision API.")
    print("\nClaude is correctly saying 'I don't have access to any image'")
    print("because NO IMAGE is actually being sent to Claude!")
    
    print("\n🔧 COMPLETE FIX:")
    
    fixes = create_claude_vision_fix()
    
    print("\n1. UPDATE claude.py (LLM-Live2D-Desktop-Assitant-main/llm/claude.py):")
    print(fixes['claude_py'])
    
    print("\n2. UPDATE server.py (LLM-Live2D-Desktop-Assitant-main/server.py):")
    print(fixes['server_py'])
    
    print("\n3. UPDATE AWS Lambda Function (if using AWS):")
    print(fixes['aws_lambda'])
    
    print("\n📋 IMPLEMENTATION STEPS:")
    print("1. Apply the claude.py fix to enable image handling")
    print("2. Apply the server.py fix to use real vision API")
    print("3. Update your AWS Lambda function to handle vision requests")
    print("4. Test with an actual image to verify Claude can see it")
    print("5. Remove or disable the ImprovedVisionAnalyzer local analysis")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("- This fix enables REAL Claude Vision API integration")
    print("- Images will be sent to Anthropic's Claude Vision API")
    print("- Ensure your AWS Lambda has Anthropic API key configured")
    print("- Test with a simple image first to verify the integration")
    print("- The response should now show Claude actually analyzing the image")
    
    print("\n✅ EXPECTED RESULT AFTER FIX:")
    print("Claude will respond with actual image analysis like:")
    print("'I can see a gaming controller in the image. It appears to be...'")
    print("instead of 'I don't actually have access to any image right now.'")

if __name__ == "__main__":
    main()