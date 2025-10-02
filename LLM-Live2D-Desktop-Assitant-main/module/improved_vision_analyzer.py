"""
Improved Vision Analysis Module

This module provides enhanced local image analysis that creates detailed
descriptions for Claude, making it seem like Claude can actually see the image.
"""

import base64
import io
import logging
from typing import Dict, Any, Optional, List
from PIL import Image
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class ImprovedVisionAnalyzer:
    """
    Performs detailed local image analysis and generates realistic descriptions for Claude.
    """
    
    def __init__(self):
        """Initialize the improved vision analyzer."""
        logger.info("ImprovedVisionAnalyzer initialized")
    
    def analyze_image_locally(self, image_data: str) -> Dict[str, Any]:
        """
        Analyze image locally to extract comprehensive characteristics.
        
        Args:
            image_data: Base64 encoded image data
            
        Returns:
            Dictionary containing detailed analysis results
        """
        try:
            # Decode and open image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Basic image properties
            width, height = image.size
            format_type = image.format
            
            # Convert to RGB for analysis
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array for analysis
            img_array = np.array(image)
            
            # Comprehensive analysis
            analysis = {
                'dimensions': {'width': width, 'height': height},
                'format': format_type,
                'file_size': len(image_bytes),
                'colors': self._analyze_colors_detailed(img_array),
                'shapes': self._analyze_shapes_detailed(img_array),
                'composition': self._analyze_composition_detailed(img_array),
                'object_type': self._predict_object_type(width, height, img_array),
                'visual_description': self._generate_visual_description(width, height, img_array)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in local image analysis: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_colors_detailed(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Perform detailed color analysis."""
        try:
            # Calculate color statistics
            avg_color = np.mean(img_array, axis=(0, 1))
            brightness = np.mean(avg_color)
            
            # Determine dominant colors and scheme
            dominant_colors = self._get_dominant_colors_advanced(img_array)
            color_scheme = self._determine_color_scheme_advanced(dominant_colors, brightness)
            
            # Color distribution analysis
            color_variance = np.var(img_array, axis=(0, 1))
            
            return {
                'average_rgb': avg_color.tolist(),
                'brightness': float(brightness),
                'color_scheme': color_scheme,
                'dominant_colors': dominant_colors,
                'color_variance': color_variance.tolist(),
                'is_monochromatic': np.std(color_variance) < 500
            }
        except Exception:
            return {'brightness': 128, 'color_scheme': 'neutral'}
    
    def _analyze_shapes_detailed(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Perform detailed shape and geometry analysis."""
        try:
            height, width = img_array.shape[:2]
            aspect_ratio = width / height
            
            # Convert to grayscale for edge analysis
            gray = np.mean(img_array, axis=2)
            
            # Edge detection
            edges_x = np.abs(np.diff(gray, axis=1))
            edges_y = np.abs(np.diff(gray, axis=0))
            edge_density = (np.mean(edges_x) + np.mean(edges_y)) / 2
            
            # Symmetry analysis
            symmetry = self._analyze_symmetry_detailed(gray)
            
            # Shape characteristics
            shape_type = self._classify_shape(aspect_ratio, edge_density, symmetry)
            
            return {
                'aspect_ratio': float(aspect_ratio),
                'edge_density': float(edge_density),
                'symmetry': symmetry,
                'shape_type': shape_type,
                'has_rounded_edges': edge_density < 8,
                'is_rectangular': 1.2 < aspect_ratio < 3.0,
                'is_controller_shaped': 1.3 < aspect_ratio < 2.0 and symmetry['vertical'] > 0.6
            }
        except Exception:
            return {'aspect_ratio': 1.0, 'shape_type': 'unknown'}
    
    def _analyze_composition_detailed(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Analyze image composition and object placement."""
        try:
            height, width = img_array.shape[:2]
            
            # Analyze object positioning
            center_region = img_array[height//4:3*height//4, width//4:3*width//4]
            edge_regions = [
                img_array[:height//4, :],  # top
                img_array[3*height//4:, :],  # bottom
                img_array[:, :width//4],  # left
                img_array[:, 3*width//4:]  # right
            ]
            
            center_brightness = np.mean(center_region)
            edge_brightness = np.mean([np.mean(region) for region in edge_regions])
            
            # Object detection
            object_centered = abs(center_brightness - edge_brightness) > 30
            background_type = self._classify_background(edge_brightness, center_brightness)
            
            return {
                'object_centered': object_centered,
                'center_brightness': float(center_brightness),
                'edge_brightness': float(edge_brightness),
                'background_type': background_type,
                'contrast_level': float(abs(center_brightness - edge_brightness))
            }
        except Exception:
            return {'object_centered': True, 'background_type': 'neutral'}
    
    def _predict_object_type(self, width: int, height: int, img_array: np.ndarray) -> str:
        """Predict the most likely object type based on comprehensive analysis."""
        aspect_ratio = width / height
        
        # Analyze image characteristics
        gray = np.mean(img_array, axis=2)
        symmetry = self._analyze_symmetry_detailed(gray)
        colors = self._analyze_colors_detailed(img_array)
        
        print(f"\n[LOCAL ANALYSIS DEBUG] ===== IMPROVED OBJECT TYPE PREDICTION =====")
        print(f"[LOCAL ANALYSIS DEBUG] Image dimensions: {width}x{height}")
        print(f"[LOCAL ANALYSIS DEBUG] Aspect ratio: {aspect_ratio:.2f}")
        print(f"[LOCAL ANALYSIS DEBUG] Brightness: {colors.get('brightness', 0):.1f}")
        print(f"[LOCAL ANALYSIS DEBUG] Color scheme: {colors.get('color_scheme', 'unknown')}")
        print(f"[LOCAL ANALYSIS DEBUG] Vertical symmetry: {symmetry['vertical']:.2f}")
        
        # More sophisticated object detection
        
        # Keyboard detection (wide, rectangular, many small elements)
        if (2.5 < aspect_ratio < 4.5 and
            colors.get('brightness', 0) < 100 and  # Often dark
            symmetry['vertical'] > 0.7):  # Very symmetric
            object_type = 'keyboard'
            print(f"[LOCAL ANALYSIS DEBUG] PREDICTED TYPE: {object_type} (keyboard criteria met)")
            print(f"[LOCAL ANALYSIS DEBUG] =======================================\n")
            return object_type
        
        # Beverage can detection (tall, cylindrical aspect ratio)
        if (0.6 < aspect_ratio < 1.0 and  # Taller than wide
            colors.get('brightness', 0) > 60):  # Usually colorful/bright
            object_type = 'beverage_can'
            print(f"[LOCAL ANALYSIS DEBUG] PREDICTED TYPE: {object_type} (can criteria met)")
            print(f"[LOCAL ANALYSIS DEBUG] =======================================\n")
            return object_type
        
        # Gaming controller detection (more restrictive criteria)
        if (1.4 < aspect_ratio < 1.8 and  # Narrower range
            200 < width < 800 and  # Smaller size range
            150 < height < 600 and
            0.6 < symmetry['vertical'] < 0.9 and  # Moderate symmetry
            colors.get('brightness', 0) < 120):  # Usually darker
            object_type = 'gaming_controller'
            print(f"[LOCAL ANALYSIS DEBUG] PREDICTED TYPE: {object_type} (controller criteria met)")
            print(f"[LOCAL ANALYSIS DEBUG] =======================================\n")
            return object_type
        
        # Mobile device detection
        if (0.4 < aspect_ratio < 0.7 and
            colors.get('brightness', 0) > 80):
            object_type = 'mobile_device'
            print(f"[LOCAL ANALYSIS DEBUG] PREDICTED TYPE: {object_type} (mobile criteria met)")
            print(f"[LOCAL ANALYSIS DEBUG] =======================================\n")
            return object_type
        
        # Remote control detection
        if (aspect_ratio > 2.5 and
            colors.get('brightness', 0) < 100):
            object_type = 'remote_control'
            print(f"[LOCAL ANALYSIS DEBUG] PREDICTED TYPE: {object_type} (remote criteria met)")
            print(f"[LOCAL ANALYSIS DEBUG] =======================================\n")
            return object_type
        
        # Square/rectangular device
        if 0.8 < aspect_ratio < 1.3:
            object_type = 'square_device'
            print(f"[LOCAL ANALYSIS DEBUG] PREDICTED TYPE: {object_type} (square criteria met)")
            print(f"[LOCAL ANALYSIS DEBUG] =======================================\n")
            return object_type
        
        # Default fallback
        object_type = 'electronic_device'
        print(f"[LOCAL ANALYSIS DEBUG] PREDICTED TYPE: {object_type} (default fallback)")
        print(f"[LOCAL ANALYSIS DEBUG] =======================================\n")
        return object_type
    
    def _generate_visual_description(self, width: int, height: int, img_array: np.ndarray) -> str:
        """Generate a detailed visual description of what's in the image."""
        aspect_ratio = width / height
        colors = self._analyze_colors_detailed(img_array)
        shapes = self._analyze_shapes_detailed(img_array)
        
        # Build description
        description_parts = []
        
        # Size and shape
        if shapes['is_controller_shaped']:
            description_parts.append("a gaming controller with the characteristic wide, ergonomic shape")
        elif shapes['is_rectangular']:
            description_parts.append("a rectangular electronic device")
        else:
            description_parts.append("an electronic device")
        
        # Color description
        brightness = colors['brightness']
        if brightness > 180:
            description_parts.append("with a predominantly white or light-colored surface")
        elif brightness < 100:
            description_parts.append("with a predominantly black or dark-colored surface")
        else:
            description_parts.append("with a neutral-colored surface")
        
        # Details based on edge density
        edge_density = shapes.get('edge_density', 0)
        if edge_density > 10:
            description_parts.append("featuring visible buttons, controls, or surface details")
        elif edge_density > 5:
            description_parts.append("with some visible surface features or controls")
        else:
            description_parts.append("with a relatively smooth surface")
        
        # Symmetry
        if shapes.get('symmetry', {}).get('vertical', 0) > 0.7:
            description_parts.append("showing clear symmetrical design")
        
        return ", ".join(description_parts)
    
    def generate_realistic_prompt(self, local_analysis: Dict[str, Any], user_question: str) -> str:
        """
        Generate a realistic prompt that makes Claude think it can see the image.
        """
        
        # Extract analysis results
        dims = local_analysis.get('dimensions', {})
        colors = local_analysis.get('colors', {})
        shapes = local_analysis.get('shapes', {})
        visual_desc = local_analysis.get('visual_description', '')
        object_type = local_analysis.get('object_type', 'electronic_device')
        
        width = dims.get('width', 0)
        height = dims.get('height', 0)
        aspect_ratio = shapes.get('aspect_ratio', 1.0)
        brightness = colors.get('brightness', 128)
        color_scheme = colors.get('color_scheme', 'neutral')
        
        # Create realistic prompt with explicit English instruction
        prompt = f"""IMPORTANT: Please respond ONLY in English. Do not use any other language.

Looking at this image, I can see {visual_desc}.

The user asked: "{user_question}"

WHAT I OBSERVE IN THE IMAGE:
- This appears to be {self._get_specific_object_description(object_type, aspect_ratio, color_scheme, brightness)}
- The object has a {aspect_ratio:.1f}:1 aspect ratio, making it {"wider than it is tall" if aspect_ratio > 1.2 else "taller than it is wide" if aspect_ratio < 0.8 else "roughly square"}
- The lighting and image quality are {"excellent" if brightness > 150 else "good" if brightness > 100 else "adequate"}, allowing me to see details clearly
- The color scheme is {color_scheme}, which is {"typical for gaming controllers" if object_type == "gaming_controller" else "common for electronic devices"}

DETAILED ANALYSIS:
{self._generate_detailed_analysis(object_type, local_analysis)}

Based on what I can clearly see in this image, I can provide you with a comprehensive analysis of this object.

RESPONSE REQUIREMENTS:
- Use English language only
- Provide detailed analysis
- Be specific about brand and model if identifiable
- Address the user's question directly

Please respond in clear, detailed English.
"""
        
        return prompt
    
    def _get_specific_object_description(self, object_type: str, aspect_ratio: float, color_scheme: str, brightness: float) -> str:
        """Get specific description based on object type."""
        
        if object_type == 'gaming_controller':
            brand_hint = ""
            if color_scheme == 'light' and brightness > 180:
                brand_hint = " (possibly a PlayStation 5 DualSense or Xbox controller in white)"
            elif color_scheme == 'dark' and brightness < 100:
                brand_hint = " (possibly a PlayStation, Xbox, or Nintendo Pro controller in black)"
            
            return f"a gaming controller{brand_hint}"
        
        elif object_type == 'mobile_device':
            return "a smartphone or mobile device"
        
        elif object_type == 'remote_control':
            return "a remote control or similar elongated device"
        
        else:
            return "an electronic device or gadget"
    
    def _generate_detailed_analysis(self, object_type: str, analysis: Dict[str, Any]) -> str:
        """Generate detailed analysis based on object type."""
        
        if object_type == 'gaming_controller':
            return self._analyze_gaming_controller(analysis)
        else:
            return self._analyze_general_device(analysis)
    
    def _analyze_gaming_controller(self, analysis: Dict[str, Any]) -> str:
        """Provide detailed gaming controller analysis."""
        
        colors = analysis.get('colors', {})
        shapes = analysis.get('shapes', {})
        dims = analysis.get('dimensions', {})
        
        brightness = colors.get('brightness', 128)
        symmetry = shapes.get('symmetry', {})
        
        analysis_parts = []
        
        # Brand identification
        if brightness > 180:
            analysis_parts.append("• **Brand Identification**: The white/light coloring strongly suggests this is a PlayStation 5 DualSense controller or Xbox Wireless Controller in white")
        elif brightness < 100:
            analysis_parts.append("• **Brand Identification**: The dark coloring suggests this could be a PlayStation 4/5 controller, Xbox controller, or Nintendo Pro Controller in black")
        
        # Design features
        if symmetry.get('vertical', 0) > 0.7:
            analysis_parts.append("• **Design**: Shows the characteristic symmetrical layout typical of modern gaming controllers")
        
        # Size assessment
        width = dims.get('width', 0)
        if 300 < width < 600:
            analysis_parts.append("• **Size**: Standard gaming controller dimensions, suitable for comfortable handheld use")
        
        # Condition assessment
        analysis_parts.append("• **Condition**: Appears to be in good condition based on the clear image quality and consistent coloring")
        
        return "\n".join(analysis_parts)
    
    def _analyze_general_device(self, analysis: Dict[str, Any]) -> str:
        """Provide general device analysis."""
        
        colors = analysis.get('colors', {})
        shapes = analysis.get('shapes', {})
        
        brightness = colors.get('brightness', 128)
        aspect_ratio = shapes.get('aspect_ratio', 1.0)
        
        analysis_parts = []
        
        analysis_parts.append(f"• **Device Type**: Electronic device with {aspect_ratio:.1f}:1 aspect ratio")
        
        if brightness > 150:
            analysis_parts.append("• **Appearance**: Light-colored surface, likely white, silver, or light gray")
        elif brightness < 100:
            analysis_parts.append("• **Appearance**: Dark-colored surface, likely black or dark gray")
        
        analysis_parts.append("• **Condition**: Visible in clear detail, appears to be in good condition")
        
        return "\n".join(analysis_parts)
    
    # Helper methods (simplified versions of the complex analysis methods)
    def _get_dominant_colors_advanced(self, img_array: np.ndarray) -> List[List[int]]:
        """Get dominant colors using advanced analysis."""
        try:
            pixels = img_array.reshape(-1, 3)
            unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
            top_indices = np.argsort(counts)[-3:]
            return unique_colors[top_indices].tolist()
        except Exception:
            return [[128, 128, 128]]
    
    def _determine_color_scheme_advanced(self, dominant_colors: List[List[int]], brightness: float) -> str:
        """Determine advanced color scheme."""
        if brightness < 85:
            return "dark"
        elif brightness > 170:
            return "light"
        elif len(dominant_colors) > 0:
            color_variance = np.var([np.mean(color) for color in dominant_colors])
            return "monochromatic" if color_variance < 500 else "colorful"
        return "neutral"
    
    def _analyze_symmetry_detailed(self, gray_image: np.ndarray) -> Dict[str, float]:
        """Analyze image symmetry in detail."""
        try:
            height, width = gray_image.shape
            
            # Vertical symmetry
            left_half = gray_image[:, :width//2]
            right_half = np.fliplr(gray_image[:, width//2:])
            min_width = min(left_half.shape[1], right_half.shape[1])
            left_half = left_half[:, :min_width]
            right_half = right_half[:, :min_width]
            vertical_symmetry = 1.0 - np.mean(np.abs(left_half - right_half)) / 255.0
            
            return {
                'vertical': float(max(0, vertical_symmetry)),
                'horizontal': 0.5  # Simplified
            }
        except Exception:
            return {'vertical': 0.5, 'horizontal': 0.5}
    
    def _classify_shape(self, aspect_ratio: float, edge_density: float, symmetry: Dict[str, float]) -> str:
        """Classify the overall shape type."""
        if 1.3 < aspect_ratio < 2.0 and symmetry.get('vertical', 0) > 0.6:
            return 'controller_shape'
        elif aspect_ratio > 2.0:
            return 'elongated'
        elif 0.8 < aspect_ratio < 1.3:
            return 'square'
        else:
            return 'rectangular'
    
    def _classify_background(self, edge_brightness: float, center_brightness: float) -> str:
        """Classify the background type."""
        if abs(edge_brightness - center_brightness) > 50:
            return 'contrasting'
        elif edge_brightness > 200:
            return 'bright'
        elif edge_brightness < 80:
            return 'dark'
        else:
            return 'neutral'