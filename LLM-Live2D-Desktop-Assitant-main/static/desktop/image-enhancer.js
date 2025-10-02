/**
 * Image Enhancement Module
 * 
 * This module provides image quality optimization capabilities for better
 * object recognition and analysis. It includes contrast enhancement, sharpening,
 * noise reduction, and lighting correction.
 */

class ImageEnhancer {
    constructor() {
        this.contrastBoost = 1.2;
        this.brightnessAdjust = 10;
        this.sharpening = true;
        this.noiseReduction = true;
        this.colorCorrection = true;
        this.targetResolution = { width: 1024, height: 768 };
        
        console.log('[ImageEnhancer] Initialized with optimization settings');
    }

    /**
     * Enhance image for better analysis
     * @param {string} imageData - Base64 image data
     * @returns {Promise<string>} - Enhanced image data
     */
    async enhanceForAnalysis(imageData) {
        try {
            console.log('[ImageEnhancer] Starting image enhancement');
            
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            const img = new Image();
            img.src = imageData;
            
            await new Promise((resolve, reject) => {
                img.onload = resolve;
                img.onerror = reject;
            });
            
            // Resize to optimal resolution if needed
            const { width, height } = this.calculateOptimalSize(img.width, img.height);
            canvas.width = width;
            canvas.height = height;
            
            console.log(`[ImageEnhancer] Resizing from ${img.width}x${img.height} to ${width}x${height}`);
            
            // Apply basic enhancements using canvas filters
            ctx.filter = this.buildFilterString();
            ctx.drawImage(img, 0, 0, width, height);
            
            // Reset filter for additional processing
            ctx.filter = 'none';
            
            // Apply advanced enhancements
            if (this.sharpening) {
                await this.applySharpeningFilter(ctx, width, height);
            }
            
            if (this.noiseReduction) {
                await this.applyNoiseReduction(ctx, width, height);
            }
            
            if (this.colorCorrection) {
                await this.applyColorCorrection(ctx, width, height);
            }
            
            const enhancedData = canvas.toDataURL('image/jpeg', 0.9);
            console.log('[ImageEnhancer] Image enhancement completed');
            
            return enhancedData;
        } catch (error) {
            console.error('[ImageEnhancer] Error during enhancement:', error);
            return imageData; // Return original on error
        }
    }

    /**
     * Calculate optimal image size for analysis
     * @param {number} originalWidth - Original width
     * @param {number} originalHeight - Original height
     * @returns {Object} - Optimal dimensions
     */
    calculateOptimalSize(originalWidth, originalHeight) {
        const maxWidth = this.targetResolution.width;
        const maxHeight = this.targetResolution.height;
        
        // If image is already smaller than target, keep original size
        if (originalWidth <= maxWidth && originalHeight <= maxHeight) {
            return { width: originalWidth, height: originalHeight };
        }
        
        // Calculate aspect ratio preserving resize
        const aspectRatio = originalWidth / originalHeight;
        
        let newWidth, newHeight;
        
        if (aspectRatio > 1) {
            // Landscape orientation
            newWidth = Math.min(originalWidth, maxWidth);
            newHeight = newWidth / aspectRatio;
            
            if (newHeight > maxHeight) {
                newHeight = maxHeight;
                newWidth = newHeight * aspectRatio;
            }
        } else {
            // Portrait orientation
            newHeight = Math.min(originalHeight, maxHeight);
            newWidth = newHeight * aspectRatio;
            
            if (newWidth > maxWidth) {
                newWidth = maxWidth;
                newHeight = newWidth / aspectRatio;
            }
        }
        
        return {
            width: Math.round(newWidth),
            height: Math.round(newHeight)
        };
    }

    /**
     * Build CSS filter string for basic enhancements
     * @returns {string} - CSS filter string
     */
    buildFilterString() {
        const filters = [];
        
        if (this.contrastBoost !== 1) {
            filters.push(`contrast(${this.contrastBoost})`);
        }
        
        if (this.brightnessAdjust !== 0) {
            const brightnessValue = 1 + (this.brightnessAdjust / 100);
            filters.push(`brightness(${brightnessValue})`);
        }
        
        // Add saturation boost for better color recognition
        filters.push('saturate(1.1)');
        
        return filters.join(' ');
    }

    /**
     * Apply sharpening filter using unsharp mask
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {number} width - Image width
     * @param {number} height - Image height
     */
    async applySharpeningFilter(ctx, width, height) {
        console.log('[ImageEnhancer] Applying sharpening filter');
        
        const imageData = ctx.getImageData(0, 0, width, height);
        const data = imageData.data;
        const sharpened = new Uint8ClampedArray(data);
        
        // Unsharp mask kernel
        const kernel = [
            0, -1, 0,
            -1, 5, -1,
            0, -1, 0
        ];
        
        const kernelSize = 3;
        const half = Math.floor(kernelSize / 2);
        
        for (let y = half; y < height - half; y++) {
            for (let x = half; x < width - half; x++) {
                for (let c = 0; c < 3; c++) { // RGB channels only
                    let sum = 0;
                    
                    for (let ky = 0; ky < kernelSize; ky++) {
                        for (let kx = 0; kx < kernelSize; kx++) {
                            const py = y + ky - half;
                            const px = x + kx - half;
                            const idx = (py * width + px) * 4 + c;
                            const kernelIdx = ky * kernelSize + kx;
                            
                            sum += data[idx] * kernel[kernelIdx];
                        }
                    }
                    
                    const outputIdx = (y * width + x) * 4 + c;
                    sharpened[outputIdx] = Math.max(0, Math.min(255, sum));
                }
            }
        }
        
        const newImageData = new ImageData(sharpened, width, height);
        ctx.putImageData(newImageData, 0, 0);
    }

    /**
     * Apply noise reduction using median filter
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {number} width - Image width
     * @param {number} height - Image height
     */
    async applyNoiseReduction(ctx, width, height) {
        console.log('[ImageEnhancer] Applying noise reduction');
        
        const imageData = ctx.getImageData(0, 0, width, height);
        const data = imageData.data;
        const filtered = new Uint8ClampedArray(data);
        
        const filterSize = 3;
        const half = Math.floor(filterSize / 2);
        
        for (let y = half; y < height - half; y++) {
            for (let x = half; x < width - half; x++) {
                for (let c = 0; c < 3; c++) { // RGB channels only
                    const values = [];
                    
                    // Collect neighboring pixel values
                    for (let ky = -half; ky <= half; ky++) {
                        for (let kx = -half; kx <= half; kx++) {
                            const py = y + ky;
                            const px = x + kx;
                            const idx = (py * width + px) * 4 + c;
                            values.push(data[idx]);
                        }
                    }
                    
                    // Sort and take median
                    values.sort((a, b) => a - b);
                    const median = values[Math.floor(values.length / 2)];
                    
                    const outputIdx = (y * width + x) * 4 + c;
                    filtered[outputIdx] = median;
                }
            }
        }
        
        const newImageData = new ImageData(filtered, width, height);
        ctx.putImageData(newImageData, 0, 0);
    }

    /**
     * Apply color correction for better object recognition
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {number} width - Image width
     * @param {number} height - Image height
     */
    async applyColorCorrection(ctx, width, height) {
        console.log('[ImageEnhancer] Applying color correction');
        
        const imageData = ctx.getImageData(0, 0, width, height);
        const data = imageData.data;
        
        // Calculate histogram for auto-levels
        const histogram = { r: new Array(256).fill(0), g: new Array(256).fill(0), b: new Array(256).fill(0) };
        
        for (let i = 0; i < data.length; i += 4) {
            histogram.r[data[i]]++;
            histogram.g[data[i + 1]]++;
            histogram.b[data[i + 2]]++;
        }
        
        // Find 1% and 99% percentiles for each channel
        const totalPixels = width * height;
        const lowPercentile = Math.floor(totalPixels * 0.01);
        const highPercentile = Math.floor(totalPixels * 0.99);
        
        const levels = { r: { min: 0, max: 255 }, g: { min: 0, max: 255 }, b: { min: 0, max: 255 } };
        
        ['r', 'g', 'b'].forEach(channel => {
            let count = 0;
            
            // Find minimum level
            for (let i = 0; i < 256; i++) {
                count += histogram[channel][i];
                if (count >= lowPercentile) {
                    levels[channel].min = i;
                    break;
                }
            }
            
            count = 0;
            // Find maximum level
            for (let i = 255; i >= 0; i--) {
                count += histogram[channel][i];
                if (count >= (totalPixels - highPercentile)) {
                    levels[channel].max = i;
                    break;
                }
            }
        });
        
        // Apply level correction
        for (let i = 0; i < data.length; i += 4) {
            // Red channel
            data[i] = Math.max(0, Math.min(255, 
                255 * (data[i] - levels.r.min) / (levels.r.max - levels.r.min)
            ));
            
            // Green channel
            data[i + 1] = Math.max(0, Math.min(255, 
                255 * (data[i + 1] - levels.g.min) / (levels.g.max - levels.g.min)
            ));
            
            // Blue channel
            data[i + 2] = Math.max(0, Math.min(255, 
                255 * (data[i + 2] - levels.b.min) / (levels.b.max - levels.b.min)
            ));
        }
        
        ctx.putImageData(imageData, 0, 0);
    }

    /**
     * Analyze image quality metrics
     * @param {string} imageData - Base64 image data
     * @returns {Promise<Object>} - Quality metrics
     */
    async analyzeQuality(imageData) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        const img = new Image();
        img.src = imageData;
        
        await new Promise(resolve => img.onload = resolve);
        
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        
        const imgData = ctx.getImageData(0, 0, img.width, img.height);
        const data = imgData.data;
        
        let totalBrightness = 0;
        let totalContrast = 0;
        let sharpnessSum = 0;
        
        for (let i = 0; i < data.length; i += 4) {
            const brightness = (data[i] + data[i + 1] + data[i + 2]) / 3;
            totalBrightness += brightness;
            
            // Simple sharpness estimation using local variance
            if (i > img.width * 4 && i < data.length - img.width * 4) {
                const variance = Math.abs(brightness - (data[i - img.width * 4] + data[i + img.width * 4]) / 2);
                sharpnessSum += variance;
            }
        }
        
        const pixelCount = data.length / 4;
        
        return {
            averageBrightness: totalBrightness / pixelCount,
            estimatedSharpness: sharpnessSum / pixelCount,
            resolution: { width: img.width, height: img.height },
            aspectRatio: img.width / img.height
        };
    }

    /**
     * Update enhancement parameters
     * @param {Object} params - New parameters
     */
    updateParams(params) {
        if (params.contrastBoost !== undefined) {
            this.contrastBoost = params.contrastBoost;
        }
        if (params.brightnessAdjust !== undefined) {
            this.brightnessAdjust = params.brightnessAdjust;
        }
        if (params.sharpening !== undefined) {
            this.sharpening = params.sharpening;
        }
        if (params.noiseReduction !== undefined) {
            this.noiseReduction = params.noiseReduction;
        }
        if (params.colorCorrection !== undefined) {
            this.colorCorrection = params.colorCorrection;
        }
        if (params.targetResolution !== undefined) {
            this.targetResolution = params.targetResolution;
        }
        
        console.log('[ImageEnhancer] Parameters updated:', {
            contrastBoost: this.contrastBoost,
            brightnessAdjust: this.brightnessAdjust,
            sharpening: this.sharpening,
            noiseReduction: this.noiseReduction,
            colorCorrection: this.colorCorrection,
            targetResolution: this.targetResolution
        });
    }

    /**
     * Get current enhancement settings
     * @returns {Object} - Current settings
     */
    getSettings() {
        return {
            contrastBoost: this.contrastBoost,
            brightnessAdjust: this.brightnessAdjust,
            sharpening: this.sharpening,
            noiseReduction: this.noiseReduction,
            colorCorrection: this.colorCorrection,
            targetResolution: this.targetResolution
        };
    }
}

// Make ImageEnhancer available globally
window.ImageEnhancer = ImageEnhancer;

// Initialize global instance
window.imageEnhancer = new ImageEnhancer();

console.log('[ImageEnhancer] Module loaded and initialized');