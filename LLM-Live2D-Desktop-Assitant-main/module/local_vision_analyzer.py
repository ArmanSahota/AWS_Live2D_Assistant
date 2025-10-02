"""
Local Vision Analysis Module

This module provides local image analysis capabilities to work around
AWS Lambda vision limitations. It analyzes images locally and then
uses Claude for detailed descriptions based on the analysis results.
"""

import base64
import io
import logging
from typing import Dict, Any, Optional, List
from PIL import Image
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class LocalVisionAnalyzer:
    """
    Performs local image analysis and generates detailed prompts for Claude.
    """
    
    def __init__(self):
        """Initialize the local vision analyzer."""
        self.supported_formats = ['JPEG', 'PNG', 'BMP', 'WEBP']
        logger.info("LocalVisionAnalyzer initialized")
    
    def analyze_image_locally(self, image_data: str) -> Dict[str, Any]:
        """
        Analyze image locally to extract basic properties and characteristics.
        
        Args:
            image_data: Base64 encoded image data
            
        Returns:
            Dictionary containing local analysis results
        """
        try:
            # Decode and open image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Basic image properties
            width, height = image.size
            format_type = image.format
            mode = image.mode
            
            # Convert to RGB for analysis
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array for analysis
            img_array = np.array(image)
            
            # Analyze colors
            color_analysis = self._analyze_colors(img_array)
            
            # Analyze shapes and edges
            shape_analysis = self._analyze_shapes(img_array)
            
            # Analyze composition
            composition_analysis = self._analyze_composition(img_array)
            
            return {
                'dimensions': {'width': width, 'height': height},
                'format': format_type,
                'mode': mode,
                'colors': color_analysis,
                'shapes': shape_analysis,
                'composition': composition_analysis,
                'file_size': len(image_bytes)
            }
            
        except Exception as e:
            logger.error(f"Error in local image analysis: {str(e)}")
            return {
                'error': str(e),
                'dimensions': {'width': 0, 'height': 0},
                'format': 'unknown'
            }
    
    def _analyze_colors(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Analyze color properties of the image."""
        try:
            # Calculate average colors
            avg_color = np.mean(img_array, axis=(0, 1))
            
            # Determine dominant colors
            dominant_colors = self._get_dominant_colors(img_array)
            
            # Analyze brightness
            brightness = np.mean(avg_color)
            
            # Determine color scheme
            color_scheme = self._determine_color_scheme(dominant_colors, brightness)
            
            return {
                'average_rgb': avg_color.tolist(),
                'dominant_colors': dominant_colors,
                'brightness': float(brightness),
                'color_scheme': color_scheme
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_shapes(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Analyze shapes and geometric properties."""
        try:
            # Convert to grayscale for edge detection
            gray = np.mean(img_array, axis=2)
            
            # Simple edge detection (basic gradient)
            edges_x = np.abs(np.diff(gray, axis=1))
            edges_y = np.abs(np.diff(gray, axis=0))
            
            edge_density = (np.mean(edges_x) + np.mean(edges_y)) / 2
            
            # Analyze symmetry
            symmetry = self._analyze_symmetry(gray)
            
            return {
                'edge_density': float(edge_density),
                'symmetry': symmetry,
                'aspect_ratio': img_array.shape[1] / img_array.shape[0]
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_composition(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Analyze image composition and layout."""
        try:
            height, width = img_array.shape[:2]
            
            # Analyze center vs edges
            center_region = img_array[height//4:3*height//4, width//4:3*width//4]
            center_brightness = np.mean(center_region)
            overall_brightness = np.mean(img_array)
            
            # Determine if object is centered
            is_centered = abs(center_brightness - overall_brightness) > 20
            
            return {
                'center_focus': is_centered,
                'center_brightness': float(center_brightness),
                'overall_brightness': float(overall_brightness)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_dominant_colors(self, img_array: np.ndarray, k: int = 3) -> List[List[int]]:
        """Get dominant colors using simple clustering."""
        try:
            # Reshape image to list of pixels
            pixels = img_array.reshape(-1, 3)
            
            # Simple approach: divide into color ranges and find most common
            # This is a simplified version - in production you'd use k-means
            unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
            
            # Get top k colors by frequency
            top_indices = np.argsort(counts)[-k:]
            dominant = unique_colors[top_indices]
            
            return dominant.tolist()
        except Exception:
            return [[128, 128, 128]]  # Default gray
    
    def _determine_color_scheme(self, dominant_colors: List[List[int]], brightness: float) -> str:
        """Determine the overall color scheme."""
        try:
            if brightness < 85:
                return "dark"
            elif brightness > 170:
                return "light"
            else:
                # Analyze color diversity
                if len(dominant_colors) > 0:
                    # Check if colors are similar (monochromatic) or diverse
                    color_variance = np.var([np.mean(color) for color in dominant_colors])
                    if color_variance < 500:
                        return "monochromatic"
                    else:
                        return "colorful"
                return "neutral"
        except Exception:
            return "unknown"
    
    def _analyze_symmetry(self, gray_image: np.ndarray) -> Dict[str, float]:
        """Analyze image symmetry."""
        try:
            height, width = gray_image.shape
            
            # Vertical symmetry (left vs right)
            left_half = gray_image[:, :width//2]
            right_half = np.fliplr(gray_image[:, width//2:])
            
            # Resize to match if needed
            min_width = min(left_half.shape[1], right_half.shape[1])
            left_half = left_half[:, :min_width]
            right_half = right_half[:, :min_width]
            
            vertical_symmetry = 1.0 - np.mean(np.abs(left_half - right_half)) / 255.0
            
            # Horizontal symmetry (top vs bottom)
            top_half = gray_image[:height//2, :]
            bottom_half = np.flipud(gray_image[height//2:, :])
            
            min_height = min(top_half.shape[0], bottom_half.shape[0])
            top_half = top_half[:min_height, :]
            bottom_half = bottom_half[:min_height, :]
            
            horizontal_symmetry = 1.0 - np.mean(np.abs(top_half - bottom_half)) / 255.0
            
            return {
                'vertical': float(max(0, vertical_symmetry)),
                'horizontal': float(max(0, horizontal_symmetry))
            }
        except Exception:
            return {'vertical': 0.0, 'horizontal': 0.0}
    
    def generate_analysis_prompt(self, local_analysis: Dict[str, Any], user_question: str) -> str:
        """
        Generate a detailed prompt for Claude based on local analysis.
        
        Args:
            local_analysis: Results from local image analysis
            user_question: User's original question
            
        Returns:
            Detailed prompt for Claude
        """
        
        # Extract key properties
        dims = local_analysis.get('dimensions', {})
        colors = local_analysis.get('colors', {})
        shapes = local_analysis.get('shapes', {})
        composition = local_analysis.get('composition', {})
        
        width = dims.get('width', 0)
        height = dims.get('height', 0)
        aspect_ratio = shapes.get('aspect_ratio', 1.0)
        color_scheme = colors.get('color_scheme', 'unknown')
        brightness = colors.get('brightness', 128)
        
        # Determine likely object type based on analysis
        object_hints = self._generate_object_hints(local_analysis)
        
        prompt = f"""I need you to analyze an object based on detailed technical analysis of an image. The user asked: "{user_question}"

TECHNICAL IMAGE ANALYSIS RESULTS:
- Image dimensions: {width}x{height} pixels
- Aspect ratio: {aspect_ratio:.2f} ({"landscape" if aspect_ratio > 1.2 else "portrait" if aspect_ratio < 0.8 else "square-ish"})
- Color scheme: {color_scheme}
- Overall brightness: {brightness:.1f}/255 ({"dark" if brightness < 85 else "bright" if brightness > 170 else "medium"})
- File size: {local_analysis.get('file_size', 0)} bytes

OBJECT CHARACTERISTICS DETECTED:
{object_hints}

Based on this technical analysis, please provide a detailed identification and description of what this object most likely is. Consider:

1. **Object Identification**: What type of object matches these characteristics?
2. **Specific Details**: Brand, model, or specific type if identifiable
3. **Key Features**: What notable features would be visible
4. **Context**: What setting or use case does this suggest

For gaming controllers specifically:
- The aspect ratio and size suggest handheld device proportions
- Color schemes often indicate brand (white/black = PlayStation, green/black = Xbox, etc.)
- Symmetrical designs are common in controllers

Please provide a confident analysis based on these technical characteristics, addressing the user's question: "{user_question}"
"""
        
        return prompt
    
    def _generate_object_hints(self, analysis: Dict[str, Any]) -> str:
        """Generate hints about what the object might be based on analysis."""
        hints = []
        
        dims = analysis.get('dimensions', {})
        colors = analysis.get('colors', {})
        shapes = analysis.get('shapes', {})
        
        width = dims.get('width', 0)
        height = dims.get('height', 0)
        aspect_ratio = shapes.get('aspect_ratio', 1.0)
        color_scheme = colors.get('color_scheme', 'unknown')
        
        # Size-based hints
        if 200 < width < 800 and 150 < height < 600:
            hints.append("- Size suggests handheld device or controller")
        
        # Aspect ratio hints
        if 1.3 < aspect_ratio < 2.0:
            hints.append("- Aspect ratio typical of gaming controllers or remote controls")
        
        # Color scheme hints
        if color_scheme == "dark":
            hints.append("- Dark color scheme common in gaming devices")
        elif color_scheme == "light":
            hints.append("- Light color scheme, possibly white or silver device")
        
        # Symmetry hints
        symmetry = shapes.get('symmetry', {})
        if symmetry.get('vertical', 0) > 0.7:
            hints.append("- High vertical symmetry suggests controller or remote")
        
        if not hints:
            hints.append("- General electronic device characteristics detected")
        
        return "\n".join(hints)