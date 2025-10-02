"""
Vision Manager Module

This module handles object analysis requests, image processing, and integration
with Claude's vision capabilities. It provides a clean interface for processing
images and generating expert analysis responses.
"""

import base64
import json
import io
import asyncio
from typing import Dict, List, Optional, Any
from PIL import Image
import logging

# Set up logging
logger = logging.getLogger(__name__)

class VisionManager:
    """
    Manages vision analysis operations including image processing,
    object detection, and integration with Claude's vision capabilities.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Vision Manager with configuration.
        
        Args:
            config: Configuration dictionary containing vision settings
        """
        self.config = config
        self.vision_config = config.get('vision', {})
        
        # Image processing settings
        self.compression_quality = self.vision_config.get('captureQuality', 0.8)
        self.max_resolution = self._parse_resolution(
            self.vision_config.get('resolution', '1280x720')
        )
        self.max_image_size = self.vision_config.get('maxImageSize', 1048576)  # 1MB
        self.confidence_threshold = self.vision_config.get('confidenceThreshold', 0.7)
        
        # Analysis settings
        self.analysis_config = self.vision_config.get('analysis', {})
        self.categories_config = self.vision_config.get('categories', {})
        
        # Rate limiting
        self.rate_limit_ms = self.vision_config.get('rateLimitMs', 5000)
        self.last_analysis_time = {}
        
        logger.info(f"VisionManager initialized with max resolution: {self.max_resolution}")
    
    def _parse_resolution(self, resolution_str: str) -> tuple:
        """Parse resolution string like '1280x720' into tuple (1280, 720)"""
        try:
            width, height = resolution_str.split('x')
            return (int(width), int(height))
        except (ValueError, AttributeError):
            logger.warning(f"Invalid resolution format: {resolution_str}, using default")
            return (1280, 720)
    
    async def process_analysis_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an object analysis request.
        
        Args:
            request_data: Dictionary containing analysis request data
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            analysis_id = request_data.get('analysisId')
            image_data = request_data.get('imageData')
            user_question = request_data.get('userQuestion', 'What is this object?')
            
            logger.info(f"Processing analysis request {analysis_id}")
            
            # Validate request
            if not image_data:
                raise ValueError("No image data provided")
            
            # Check rate limiting
            if not self._check_rate_limit(analysis_id):
                raise ValueError("Rate limit exceeded")
            
            # Process image
            processed_image = await self._process_image(image_data)
            if not processed_image:
                raise ValueError("Failed to process image")
            
            # Perform analysis (placeholder for now - will integrate with Claude)
            analysis_result = await self._analyze_object(
                processed_image, user_question, analysis_id
            )
            
            # Update rate limiting
            self._update_rate_limit(analysis_id)
            
            return {
                'analysisId': analysis_id,
                'success': True,
                'result': analysis_result
            }
            
        except Exception as e:
            logger.error(f"Error processing analysis request: {str(e)}")
            return {
                'analysisId': request_data.get('analysisId'),
                'success': False,
                'error': str(e)
            }
    
    async def _process_image(self, image_data: str) -> Optional[Dict[str, Any]]:
        """
        Process and optimize image data.
        
        Args:
            image_data: Base64 encoded image data
            
        Returns:
            Dictionary containing processed image information
        """
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            
            # Check size limits
            if len(image_bytes) > self.max_image_size:
                logger.warning(f"Image size {len(image_bytes)} exceeds limit {self.max_image_size}")
                # Could implement compression here
            
            # Open image with PIL
            image = Image.open(io.BytesIO(image_bytes))
            original_size = image.size
            
            logger.info(f"Processing image: {original_size[0]}x{original_size[1]}")
            
            # Resize if needed
            if (image.size[0] > self.max_resolution[0] or 
                image.size[1] > self.max_resolution[1]):
                
                # Calculate new size maintaining aspect ratio
                ratio = min(
                    self.max_resolution[0] / image.size[0],
                    self.max_resolution[1] / image.size[1]
                )
                new_size = (
                    int(image.size[0] * ratio),
                    int(image.size[1] * ratio)
                )
                
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized image to: {new_size[0]}x{new_size[1]}")
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Compress and encode
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=int(self.compression_quality * 100))
            compressed_data = base64.b64encode(output.getvalue()).decode()
            
            return {
                'image_data': compressed_data,
                'original_size': original_size,
                'processed_size': image.size,
                'compression_ratio': len(image_data) / len(compressed_data) if len(compressed_data) > 0 else 1,
                'format': 'JPEG'
            }
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None
    
    async def _analyze_object(self, processed_image: Dict[str, Any], 
                            user_question: str, analysis_id: str) -> Dict[str, Any]:
        """
        Analyze object in the processed image.
        
        Args:
            processed_image: Processed image data
            user_question: User's question about the object
            analysis_id: Unique analysis identifier
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # For now, return a placeholder response
            # In the full implementation, this would integrate with Claude Vision API
            
            # Simulate analysis based on image characteristics
            image_size = processed_image['processed_size']
            compression_ratio = processed_image['compression_ratio']
            
            # Generate mock analysis based on configuration
            analysis_text = self._generate_mock_analysis(user_question, image_size)
            
            # Calculate mock confidence based on image quality
            confidence = min(0.95, 0.6 + (compression_ratio * 0.2))
            
            # Determine category (mock)
            category = self._determine_mock_category(user_question)
            
            return {
                'analysis': analysis_text,
                'confidence': confidence,
                'category': category,
                'timestamp': asyncio.get_event_loop().time(),
                'image_info': {
                    'size': image_size,
                    'compression_ratio': compression_ratio,
                    'format': processed_image['format']
                },
                'analysis_config': {
                    'detail_level': self.analysis_config.get('detailLevel', 'comprehensive'),
                    'include_repair_info': self.analysis_config.get('includeRepairInfo', True),
                    'include_cost_estimates': self.analysis_config.get('includeCostEstimates', True),
                    'include_safety_warnings': self.analysis_config.get('includeSafetyWarnings', True)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing object: {str(e)}")
            return {
                'analysis': f"Analysis failed: {str(e)}",
                'confidence': 0.0,
                'category': 'error',
                'timestamp': asyncio.get_event_loop().time()
            }
    
    def _generate_mock_analysis(self, user_question: str, image_size: tuple) -> str:
        """Generate mock analysis response for testing"""
        
        # Basic analysis based on question keywords
        question_lower = user_question.lower()
        
        if any(word in question_lower for word in ['tire', 'wheel', 'car', 'automotive']):
            return """Object Analysis: Automotive Component

Based on the image analysis, this appears to be an automotive tire or wheel component.

Key Observations:
- Circular/cylindrical shape consistent with tire structure
- Surface texture suggests rubber or metal composition
- Size and proportions match standard automotive components

Assessment:
- Condition: Requires closer inspection for damage assessment
- Repairability: Depends on specific damage type and location
- Safety Considerations: Any tire damage should be evaluated by a professional

Recommendations:
- Have the component inspected by a qualified automotive technician
- Check for proper inflation and tread depth
- Look for signs of uneven wear or damage

Cost Estimates:
- Professional inspection: $20-50
- Minor repairs: $25-75
- Replacement: $100-300 depending on tire type"""

        elif any(word in question_lower for word in ['phone', 'smartphone', 'device', 'electronics']):
            return """Object Analysis: Electronic Device

Based on the image analysis, this appears to be a smartphone or electronic device.

Key Observations:
- Rectangular form factor typical of mobile devices
- Screen and button layout consistent with smartphone design
- Size proportions match standard device dimensions

Device Information:
- Type: Likely smartphone or tablet device
- Condition: Visual assessment shows normal wear patterns
- Functionality: Cannot determine operational status from image alone

Specifications (Estimated):
- Display: Appears to be touchscreen interface
- Build: Standard consumer electronics construction
- Age: Requires model identification for accurate dating

Troubleshooting:
- Check power button and charging port functionality
- Verify screen responsiveness
- Test basic connectivity features

Value Assessment:
- Condition-dependent valuation required
- Market value varies by model and functionality
- Professional diagnostic recommended for accurate assessment"""

        else:
            return f"""Object Analysis: General Item Assessment

Based on the image analysis of the {image_size[0]}x{image_size[1]} pixel image:

Visual Characteristics:
- Object appears to be a physical item requiring identification
- Image quality is sufficient for basic analysis
- Additional context may be needed for detailed assessment

Analysis Approach:
- Shape and form factor analysis completed
- Surface texture and material properties evaluated
- Size estimation based on visual cues

Recommendations:
- Provide additional context about the object's intended use
- Consider multiple angles for comprehensive analysis
- Specify particular concerns or questions about the item

Next Steps:
- More specific questions will yield more detailed analysis
- Professional consultation may be beneficial for specialized items
- Additional images from different angles could improve accuracy

Note: This is a preliminary analysis. More detailed assessment requires additional information about the object's context and intended use."""

    def _determine_mock_category(self, user_question: str) -> str:
        """Determine mock category based on question content"""
        question_lower = user_question.lower()
        
        if any(word in question_lower for word in ['tire', 'car', 'automotive', 'engine', 'brake']):
            return 'automotive'
        elif any(word in question_lower for word in ['phone', 'smartphone', 'electronics', 'device']):
            return 'electronics'
        elif any(word in question_lower for word in ['tool', 'wrench', 'screwdriver', 'hammer']):
            return 'tools'
        elif any(word in question_lower for word in ['appliance', 'refrigerator', 'microwave']):
            return 'appliances'
        else:
            return 'general'
    
    def _check_rate_limit(self, analysis_id: str) -> bool:
        """Check if analysis request is within rate limits"""
        import time
        
        current_time = time.time() * 1000  # Convert to milliseconds
        last_time = self.last_analysis_time.get(analysis_id, 0)
        
        if current_time - last_time < self.rate_limit_ms:
            logger.warning(f"Rate limit exceeded for analysis {analysis_id}")
            return False
        
        return True
    
    def _update_rate_limit(self, analysis_id: str):
        """Update rate limiting timestamp"""
        import time
        self.last_analysis_time[analysis_id] = time.time() * 1000
    
    def get_supported_categories(self) -> List[str]:
        """Get list of supported analysis categories"""
        return [
            category for category, enabled in self.categories_config.items()
            if enabled
        ]
    
    def get_analysis_capabilities(self) -> Dict[str, Any]:
        """Get current analysis capabilities and settings"""
        return {
            'categories': self.get_supported_categories(),
            'max_resolution': self.max_resolution,
            'compression_quality': self.compression_quality,
            'max_image_size': self.max_image_size,
            'confidence_threshold': self.confidence_threshold,
            'analysis_features': {
                'repair_info': self.analysis_config.get('includeRepairInfo', True),
                'cost_estimates': self.analysis_config.get('includeCostEstimates', True),
                'safety_warnings': self.analysis_config.get('includeSafetyWarnings', True),
                'specifications': self.analysis_config.get('includeSpecifications', True)
            }
        }
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update vision configuration"""
        self.vision_config.update(new_config)
        
        # Update derived settings
        self.compression_quality = self.vision_config.get('captureQuality', 0.8)
        self.max_resolution = self._parse_resolution(
            self.vision_config.get('resolution', '1280x720')
        )
        self.confidence_threshold = self.vision_config.get('confidenceThreshold', 0.7)
        
        logger.info("Vision configuration updated")