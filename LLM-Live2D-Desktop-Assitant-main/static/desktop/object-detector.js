/**
 * Object Detection and Smart Cropping Module
 * 
 * This module provides intelligent object detection and cropping capabilities
 * for the vision analysis system. It uses edge detection algorithms to isolate
 * objects from backgrounds and optimize images for analysis.
 */

class ObjectDetector {
    constructor() {
        this.captureMode = 'object-focused';
        this.detectionThreshold = 0.7;
        this.cropPadding = 50; // pixels around detected object
        this.minObjectSize = 100; // minimum object size in pixels
        this.maxObjectSize = 800; // maximum object size in pixels
        this.contrastThreshold = 50; // edge detection sensitivity
        
        console.log('[ObjectDetector] Initialized with smart cropping capabilities');
    }

    /**
     * Detect and crop objects from an image
     * @param {string} imageData - Base64 image data
     * @returns {Promise<string>} - Cropped and optimized image data
     */
    async detectAndCrop(imageData) {
        try {
            console.log('[ObjectDetector] Starting object detection and cropping');
            
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            // Load image
            const img = new Image();
            img.src = imageData;
            
            await new Promise((resolve, reject) => {
                img.onload = resolve;
                img.onerror = reject;
            });
            
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
            
            console.log(`[ObjectDetector] Processing image: ${img.width}x${img.height}`);
            
            // Find object boundaries using edge detection
            const bounds = this.findObjectBounds(ctx, img.width, img.height);
            
            if (!bounds || bounds.width < this.minObjectSize || bounds.height < this.minObjectSize) {
                console.log('[ObjectDetector] No significant object detected, returning original image');
                return imageData;
            }
            
            console.log(`[ObjectDetector] Object detected at: ${bounds.x}, ${bounds.y}, ${bounds.width}x${bounds.height}`);
            
            // Crop to object with padding
            const croppedCanvas = this.cropToObject(ctx, bounds, img.width, img.height);
            
            const croppedData = croppedCanvas.toDataURL('image/jpeg', 0.8);
            console.log('[ObjectDetector] Object detection and cropping completed');
            
            return croppedData;
        } catch (error) {
            console.error('[ObjectDetector] Error during detection:', error);
            return imageData; // Return original on error
        }
    }

    /**
     * Find object boundaries using edge detection
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {number} width - Image width
     * @param {number} height - Image height
     * @returns {Object} - Bounding box coordinates
     */
    findObjectBounds(ctx, width, height) {
        const imageData = ctx.getImageData(0, 0, width, height);
        const data = imageData.data;
        
        let minX = width, minY = height, maxX = 0, maxY = 0;
        let edgePixelCount = 0;
        
        // Simple edge detection algorithm using Sobel-like operator
        for (let y = 1; y < height - 1; y++) {
            for (let x = 1; x < width - 1; x++) {
                const idx = (y * width + x) * 4;
                
                // Calculate gradient magnitude using neighboring pixels
                const gx = Math.abs(
                    (data[idx - 4] + 2 * data[idx] + data[idx + 4]) -
                    (data[idx - width * 4 - 4] + 2 * data[idx - width * 4] + data[idx - width * 4 + 4])
                );
                
                const gy = Math.abs(
                    (data[idx - width * 4 - 4] + 2 * data[idx - 4] + data[idx + width * 4 - 4]) -
                    (data[idx - width * 4 + 4] + 2 * data[idx + 4] + data[idx + width * 4 + 4])
                );
                
                const gradient = Math.sqrt(gx * gx + gy * gy);
                
                if (gradient > this.contrastThreshold) {
                    minX = Math.min(minX, x);
                    minY = Math.min(minY, y);
                    maxX = Math.max(maxX, x);
                    maxY = Math.max(maxY, y);
                    edgePixelCount++;
                }
            }
        }
        
        // Check if we found enough edge pixels to constitute an object
        const totalPixels = width * height;
        const edgeRatio = edgePixelCount / totalPixels;
        
        if (edgeRatio < 0.01 || edgeRatio > 0.5) {
            console.log(`[ObjectDetector] Edge ratio ${edgeRatio.toFixed(3)} outside valid range`);
            return null;
        }
        
        // Add padding around detected object
        const paddedBounds = {
            x: Math.max(0, minX - this.cropPadding),
            y: Math.max(0, minY - this.cropPadding),
            width: Math.min(width - (minX - this.cropPadding), maxX - minX + 2 * this.cropPadding),
            height: Math.min(height - (minY - this.cropPadding), maxY - minY + 2 * this.cropPadding)
        };
        
        return paddedBounds;
    }

    /**
     * Crop image to object bounds
     * @param {CanvasRenderingContext2D} ctx - Source canvas context
     * @param {Object} bounds - Bounding box
     * @param {number} originalWidth - Original image width
     * @param {number} originalHeight - Original image height
     * @returns {HTMLCanvasElement} - Cropped canvas
     */
    cropToObject(ctx, bounds, originalWidth, originalHeight) {
        const croppedCanvas = document.createElement('canvas');
        const croppedCtx = croppedCanvas.getContext('2d');
        
        // Ensure bounds are within image
        const safeBounds = {
            x: Math.max(0, Math.min(bounds.x, originalWidth - 1)),
            y: Math.max(0, Math.min(bounds.y, originalHeight - 1)),
            width: Math.max(1, Math.min(bounds.width, originalWidth - bounds.x)),
            height: Math.max(1, Math.min(bounds.height, originalHeight - bounds.y))
        };
        
        croppedCanvas.width = safeBounds.width;
        croppedCanvas.height = safeBounds.height;
        
        // Copy the cropped region
        const sourceImageData = ctx.getImageData(
            safeBounds.x, 
            safeBounds.y, 
            safeBounds.width, 
            safeBounds.height
        );
        
        croppedCtx.putImageData(sourceImageData, 0, 0);
        
        return croppedCanvas;
    }

    /**
     * Analyze image composition for better cropping
     * @param {ImageData} imageData - Image data to analyze
     * @returns {Object} - Composition analysis results
     */
    analyzeComposition(imageData) {
        const data = imageData.data;
        const width = imageData.width;
        const height = imageData.height;
        
        // Calculate center of mass for bright regions
        let totalBrightness = 0;
        let centerX = 0;
        let centerY = 0;
        let pixelCount = 0;
        
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const idx = (y * width + x) * 4;
                const brightness = (data[idx] + data[idx + 1] + data[idx + 2]) / 3;
                
                if (brightness > 100) { // Focus on brighter regions
                    totalBrightness += brightness;
                    centerX += x * brightness;
                    centerY += y * brightness;
                    pixelCount++;
                }
            }
        }
        
        if (totalBrightness > 0) {
            centerX /= totalBrightness;
            centerY /= totalBrightness;
        } else {
            centerX = width / 2;
            centerY = height / 2;
        }
        
        return {
            centerOfMass: { x: centerX, y: centerY },
            averageBrightness: totalBrightness / pixelCount || 0,
            brightPixelRatio: pixelCount / (width * height)
        };
    }

    /**
     * Validate if detected object is suitable for analysis
     * @param {Object} bounds - Object bounds
     * @param {number} imageWidth - Original image width
     * @param {number} imageHeight - Original image height
     * @returns {boolean} - Whether object is suitable
     */
    validateObject(bounds, imageWidth, imageHeight) {
        if (!bounds) return false;
        
        const objectArea = bounds.width * bounds.height;
        const imageArea = imageWidth * imageHeight;
        const areaRatio = objectArea / imageArea;
        
        // Object should be between 5% and 80% of image area
        if (areaRatio < 0.05 || areaRatio > 0.8) {
            console.log(`[ObjectDetector] Object area ratio ${areaRatio.toFixed(3)} outside valid range`);
            return false;
        }
        
        // Object should have reasonable aspect ratio (not too thin/wide)
        const aspectRatio = bounds.width / bounds.height;
        if (aspectRatio < 0.1 || aspectRatio > 10) {
            console.log(`[ObjectDetector] Object aspect ratio ${aspectRatio.toFixed(2)} outside valid range`);
            return false;
        }
        
        return true;
    }

    /**
     * Get detection statistics for debugging
     * @returns {Object} - Detection statistics
     */
    getStats() {
        return {
            detectionThreshold: this.detectionThreshold,
            cropPadding: this.cropPadding,
            minObjectSize: this.minObjectSize,
            maxObjectSize: this.maxObjectSize,
            contrastThreshold: this.contrastThreshold
        };
    }

    /**
     * Update detection parameters
     * @param {Object} params - New parameters
     */
    updateParams(params) {
        if (params.detectionThreshold !== undefined) {
            this.detectionThreshold = params.detectionThreshold;
        }
        if (params.cropPadding !== undefined) {
            this.cropPadding = params.cropPadding;
        }
        if (params.contrastThreshold !== undefined) {
            this.contrastThreshold = params.contrastThreshold;
        }
        
        console.log('[ObjectDetector] Parameters updated:', this.getStats());
    }
}

// Make ObjectDetector available globally
window.ObjectDetector = ObjectDetector;

// Initialize global instance
window.objectDetector = new ObjectDetector();

console.log('[ObjectDetector] Module loaded and initialized');