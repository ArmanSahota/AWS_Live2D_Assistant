"""
Claude Vision Analysis Module

This module integrates with Claude's vision capabilities to provide real object analysis
instead of placeholder responses. It uses the existing Claude configuration from conf.yaml.
"""

import base64
import json
import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ClaudeVisionAnalyzer:
    """
    Handles real vision analysis using Claude's vision capabilities via AWS Bedrock.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Claude Vision Analyzer.
        
        Args:
            config: Configuration dictionary from conf.yaml
        """
        self.config = config
        self.claude_config = config.get('claude', {})
        self.base_url = self.claude_config.get('BASE_URL')
        self.model = self.claude_config.get('MODEL', 'anthropic.claude-3-7-sonnet-20250219-v1:0')
        self.max_tokens = config.get('MAX_TOKENS', 500)
        self.timeout = config.get('RESPONSE_TIMEOUT', 30)
        
        logger.info(f"ClaudeVisionAnalyzer initialized with model: {self.model}")
    
    async def analyze_image(self, image_data: str, user_question: str = "What is this object?") -> Dict[str, Any]:
        """
        Analyze an image using Claude's vision capabilities.
        
        Args:
            image_data: Base64 encoded image data
            user_question: User's question about the image
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Create the vision analysis prompt
            vision_prompt = self._create_vision_prompt(user_question)
            
            # Prepare the request payload for Claude Vision (Anthropic Messages API format)
            payload = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "system": "You are an expert at analyzing images and identifying objects. Provide detailed, accurate descriptions.",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": vision_prompt
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
                    }
                ]
            }
            
            # Send request to Claude
            response = await self._send_claude_request(payload)
            
            if response and response.get('success'):
                # Parse Claude's response into structured format
                analysis_text = response.get('content', 'Analysis completed')
                return self._format_analysis_result(analysis_text, user_question)
            else:
                logger.error(f"Claude vision request failed: {response}")
                return self._create_error_result("Claude vision analysis failed")
                
        except Exception as e:
            logger.error(f"Error in Claude vision analysis: {str(e)}")
            return self._create_error_result(f"Vision analysis error: {str(e)}")
    
    def _create_vision_prompt(self, user_question: str) -> str:
        """Create a comprehensive vision analysis prompt for Claude."""
        
        return f"""Please analyze this image and provide a detailed, helpful response to the user's question: "{user_question}"

Focus on:
1. **Object Identification**: What is the main object in the image? Be specific about brand, model, type, etc.
2. **Key Characteristics**: Describe important visual features, condition, and notable details
3. **Context & Setting**: What environment or context is the object in?
4. **Practical Information**: If relevant, provide useful information about the object's purpose, value, or condition

For gaming controllers specifically:
- Identify the console brand (PlayStation, Xbox, Nintendo, etc.)
- Note the generation/model (PS5, PS4, Xbox Series X, etc.)
- Describe the condition and any visible features
- Mention any accessories or special editions if visible

For other objects:
- Be specific about brand, model, or type when identifiable
- Note condition, age, or wear if relevant
- Provide context about the object's use or purpose
- Include any safety considerations if applicable

Please provide a clear, informative response that directly answers the user's question while being helpful and accurate."""

    async def _send_claude_request(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send request to Claude via the configured endpoint.
        
        Args:
            payload: Request payload for Claude
            
        Returns:
            Response from Claude or None if failed
        """
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                logger.info(f"Sending vision request to Claude at {self.base_url}")
                
                # Try the vision endpoint first, fallback to regular endpoint
                vision_endpoints = [
                    f"{self.base_url}/vision",  # Try dedicated vision endpoint
                    f"{self.base_url}/messages",  # Try Anthropic messages API endpoint
                    f"{self.base_url}/claude"  # Fallback to regular endpoint
                ]
                
                for endpoint in vision_endpoints:
                    try:
                        logger.info(f"Trying vision endpoint: {endpoint}")
                        
                        async with session.post(
                            endpoint,
                            json=payload,
                            headers=headers
                        ) as response:
                            
                            if response.status == 200:
                                result = await response.json()
                                logger.info(f"Claude vision analysis completed successfully via {endpoint}")
                                
                                # Handle different response formats
                                if 'content' in result and isinstance(result['content'], list):
                                    # Anthropic Messages API format
                                    reply_text = result['content'][0].get('text', '')
                                elif 'content' in result:
                                    # Simple content format
                                    reply_text = result['content']
                                elif 'reply' in result:
                                    # AWS Lambda format
                                    reply_text = result['reply']
                                else:
                                    reply_text = str(result)
                                
                                return {
                                    'success': True,
                                    'content': reply_text,
                                    'usage': result.get('usage', {}),
                                    'endpoint_used': endpoint
                                }
                            else:
                                error_text = await response.text()
                                logger.warning(f"Endpoint {endpoint} failed with {response.status}: {error_text}")
                                continue  # Try next endpoint
                                
                    except Exception as e:
                        logger.warning(f"Endpoint {endpoint} failed with exception: {e}")
                        continue  # Try next endpoint
                
                # If all endpoints failed
                return {
                    'success': False,
                    'error': "All vision endpoints failed. AWS Lambda may need vision support update."
                }
                        
        except asyncio.TimeoutError:
            logger.error("Claude vision request timed out")
            return {
                'success': False,
                'error': "Request timed out"
            }
        except Exception as e:
            logger.error(f"Error sending Claude vision request: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_analysis_result(self, analysis_text: str, user_question: str) -> Dict[str, Any]:
        """
        Format Claude's response into the expected analysis result structure.
        
        Args:
            analysis_text: Raw response from Claude
            user_question: Original user question
            
        Returns:
            Formatted analysis result
        """
        # Extract key information from Claude's response
        category = self._determine_category(analysis_text)
        confidence = self._calculate_confidence(analysis_text)
        
        return {
            "category": category,
            "confidence": confidence,
            "analysis": analysis_text,
            "description": f"Claude Vision Analysis: {user_question}",
            "details": [
                "Real-time Claude vision analysis completed",
                f"Object category: {category}",
                f"Analysis confidence: {confidence:.2f}",
                "Powered by Claude 3.5 Sonnet with vision capabilities"
            ],
            "timestamp": datetime.now().isoformat(),
            "source": "claude_vision",
            "model": self.model
        }
    
    def _determine_category(self, analysis_text: str) -> str:
        """Determine object category from Claude's analysis."""
        text_lower = analysis_text.lower()
        
        # Gaming controllers
        if any(word in text_lower for word in ['controller', 'gamepad', 'ps5', 'ps4', 'xbox', 'nintendo', 'playstation']):
            return 'gaming_controller'
        
        # Electronics
        elif any(word in text_lower for word in ['phone', 'smartphone', 'tablet', 'laptop', 'computer', 'device', 'electronic']):
            return 'electronics'
        
        # Tools
        elif any(word in text_lower for word in ['tool', 'wrench', 'screwdriver', 'hammer', 'drill']):
            return 'tools'
        
        # Automotive
        elif any(word in text_lower for word in ['car', 'automotive', 'tire', 'engine', 'vehicle']):
            return 'automotive'
        
        # Appliances
        elif any(word in text_lower for word in ['appliance', 'refrigerator', 'microwave', 'oven', 'washer']):
            return 'appliances'
        
        else:
            return 'general_object'
    
    def _calculate_confidence(self, analysis_text: str) -> float:
        """Calculate confidence score based on analysis detail and specificity."""
        
        # Base confidence
        confidence = 0.7
        
        # Increase confidence for specific identifications
        if any(word in analysis_text.lower() for word in ['ps5', 'playstation 5', 'dualsense']):
            confidence += 0.2
        elif any(word in analysis_text.lower() for word in ['xbox', 'playstation', 'nintendo']):
            confidence += 0.15
        
        # Increase for detailed descriptions
        if len(analysis_text) > 200:
            confidence += 0.1
        
        # Increase for brand/model mentions
        if any(word in analysis_text.lower() for word in ['sony', 'microsoft', 'apple', 'samsung']):
            confidence += 0.05
        
        return min(0.95, confidence)  # Cap at 95%
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create an error result structure."""
        return {
            "category": "error",
            "confidence": 0.0,
            "analysis": f"Vision analysis failed: {error_message}",
            "description": "Error during vision analysis",
            "details": [
                "Vision analysis encountered an error",
                f"Error: {error_message}",
                "Please try again or check system configuration"
            ],
            "timestamp": datetime.now().isoformat(),
            "source": "claude_vision_error",
            "model": self.model
        }