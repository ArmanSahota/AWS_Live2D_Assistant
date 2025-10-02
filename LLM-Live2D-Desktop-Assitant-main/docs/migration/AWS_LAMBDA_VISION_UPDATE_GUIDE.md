# AWS Lambda Vision Support Update Guide

## Problem Identified

Your AWS Lambda function at `https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev/claude` currently only supports text-based requests, but Claude 3.5 Sonnet has vision capabilities that require a different message format.

## Current Error
```
ValidationException: messages.0.content.0.text.text: Input should be a valid string
```

This happens because the Lambda function expects simple text but receives the Anthropic Messages API format with image content blocks.

## Solution: Update AWS Lambda Function

Your AWS Lambda function needs to be updated to handle both text and vision requests. Here's the updated Lambda function code:

### Updated Lambda Function (Python)

```python
import json
import boto3
import base64
from typing import Dict, Any, List

def lambda_handler(event, context):
    """
    Updated Lambda function to handle both text and vision requests for Claude.
    """
    
    try:
        # Parse the request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)
        
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        # Determine if this is a vision request or text request
        if 'messages' in body and isinstance(body['messages'], list):
            # New Anthropic Messages API format (vision support)
            response = handle_vision_request(bedrock, body)
        else:
            # Legacy text format (backward compatibility)
            response = handle_text_request(bedrock, body)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(response)
        }
        
    except Exception as e:
        print(f"Lambda error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f'Lambda function error: {str(e)}'
            })
        }

def handle_vision_request(bedrock, body: Dict[str, Any]) -> Dict[str, Any]:
    """Handle vision requests with the Anthropic Messages API format."""
    
    # Extract parameters
    model_id = body.get('model', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
    max_tokens = body.get('max_tokens', 1000)
    system_prompt = body.get('system', '')
    messages = body.get('messages', [])
    
    # Prepare the request for Bedrock
    bedrock_body = {
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': max_tokens,
        'messages': messages
    }
    
    # Add system prompt if provided
    if system_prompt:
        bedrock_body['system'] = system_prompt
    
    # Call Bedrock
    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(bedrock_body),
        contentType='application/json'
    )
    
    # Parse response
    response_body = json.loads(response['body'].read())
    
    # Extract the text content
    if 'content' in response_body and len(response_body['content']) > 0:
        reply_text = response_body['content'][0].get('text', '')
    else:
        reply_text = 'No response generated'
    
    return {
        'reply': reply_text,
        'content': response_body.get('content', []),
        'usage': response_body.get('usage', {}),
        'model': model_id,
        'type': 'vision'
    }

def handle_text_request(bedrock, body: Dict[str, Any]) -> Dict[str, Any]:
    """Handle legacy text requests for backward compatibility."""
    
    # Extract parameters (legacy format)
    text = body.get('text', '')
    system_prompt = body.get('system', '')
    model_id = body.get('model', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
    max_tokens = body.get('max_tokens', 1000)
    
    # Convert to Messages API format
    messages = [
        {
            'role': 'user',
            'content': text
        }
    ]
    
    # Prepare the request for Bedrock
    bedrock_body = {
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': max_tokens,
        'messages': messages
    }
    
    # Add system prompt if provided
    if system_prompt:
        bedrock_body['system'] = system_prompt
    
    # Call Bedrock
    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(bedrock_body),
        contentType='application/json'
    )
    
    # Parse response
    response_body = json.loads(response['body'].read())
    
    # Extract the text content
    if 'content' in response_body and len(response_body['content']) > 0:
        reply_text = response_body['content'][0].get('text', '')
    else:
        reply_text = 'No response generated'
    
    return {
        'reply': reply_text,
        'usage': response_body.get('usage', {}),
        'model': model_id,
        'type': 'text'
    }
```

### Required IAM Permissions

Make sure your Lambda function has these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
                "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-*"
            ]
        }
    ]
}
```

## Deployment Steps

1. **Update Lambda Function Code**:
   - Replace your current Lambda function code with the updated version above
   - Make sure to install any required dependencies

2. **Test the Update**:
   - Deploy the updated function
   - Test with a simple text request first
   - Then test with a vision request

3. **Verify Vision Support**:
   - The function should now handle both formats:
     - Legacy: `{"text": "Hello", "system": "..."}`
     - Vision: `{"messages": [{"role": "user", "content": [...]}]}`

## Alternative: Quick Fix Without Lambda Update

If you can't update the Lambda function immediately, I can implement a local workaround that processes images locally and sends enhanced text prompts to your current endpoint.

Would you like me to:
1. **Help you update the AWS Lambda function** (recommended for full vision support)
2. **Implement the local workaround** (works with current setup)

Let me know which approach you prefer!