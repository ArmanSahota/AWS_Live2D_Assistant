/**
 * Webcam Manager Module
 * 
 * This module handles webcam access, image capture, and integration with the
 * object analysis system. It provides a clean interface for camera operations
 * and handles permissions, device selection, and error recovery.
 */

class WebcamManager {
    constructor() {
        this.stream = null;
        this.video = null;
        this.canvas = null;
        this.isActive = false;
        this.isCapturing = false;
        this.deviceId = null;
        this.lastCaptureTime = 0;
        this.minCaptureInterval = 1000; // Minimum 1 second between captures
        
        this.config = {
            resolution: { width: 1280, height: 720 },
            quality: 0.8,
            captureMode: 'manual', // 'manual', 'speech-triggered', 'periodic'
            periodicInterval: 30000, // 30 seconds for periodic mode
            facingMode: 'environment' // 'user' for front camera, 'environment' for back
        };
        
        this.periodicTimer = null;
        this.devices = [];
        
        console.log('[WebcamManager] Initialized');
    }

    /**
     * Initialize webcam system and request permissions
     * @returns {Promise<boolean>} - Success status
     */
    async initialize() {
        try {
            console.log('[WebcamManager] Initializing webcam system');
            
            // Check if getUserMedia is supported
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('getUserMedia not supported in this browser');
            }
            
            // Request initial permission
            const permissionGranted = await this.requestPermission();
            if (!permissionGranted) {
                throw new Error('Camera permission denied');
            }
            
            // Enumerate available devices
            await this.enumerateDevices();
            
            // Create video element for preview
            this.createVideoElement();
            
            console.log('[WebcamManager] Initialization completed successfully');
            return true;
            
        } catch (error) {
            console.error('[WebcamManager] Initialization failed:', error);
            this.handleError(error);
            return false;
        }
    }

    /**
     * Request camera permission
     * @returns {Promise<boolean>} - Permission granted status
     */
    async requestPermission() {
        try {
            console.log('[WebcamManager] Requesting camera permission');
            
            // Request access to test permissions
            const testStream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: this.config.facingMode }
            });
            
            // Stop the test stream immediately
            testStream.getTracks().forEach(track => track.stop());
            
            console.log('[WebcamManager] Camera permission granted');
            return true;
            
        } catch (error) {
            console.error('[WebcamManager] Camera permission denied:', error);
            return false;
        }
    }

    /**
     * Enumerate available camera devices
     * @returns {Promise<Array>} - List of available devices
     */
    async enumerateDevices() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            this.devices = devices.filter(device => device.kind === 'videoinput');
            
            console.log(`[WebcamManager] Found ${this.devices.length} camera devices:`, 
                this.devices.map(d => ({ id: d.deviceId, label: d.label })));
            
            // Select default device if none selected
            if (!this.deviceId && this.devices.length > 0) {
                // Prefer back camera for object analysis
                const backCamera = this.devices.find(d => 
                    d.label.toLowerCase().includes('back') || 
                    d.label.toLowerCase().includes('environment')
                );
                this.deviceId = backCamera ? backCamera.deviceId : this.devices[0].deviceId;
                console.log('[WebcamManager] Selected default camera:', this.deviceId);
            }
            
            return this.devices;
            
        } catch (error) {
            console.error('[WebcamManager] Failed to enumerate devices:', error);
            return [];
        }
    }

    /**
     * Create video element for camera preview
     */
    createVideoElement() {
        if (this.video) return;
        
        this.video = document.createElement('video');
        this.video.id = 'webcam-preview';
        this.video.autoplay = true;
        this.video.muted = true;
        this.video.playsInline = true;
        this.video.style.display = 'none'; // Hidden by default
        
        // Add to DOM for functionality (can be styled to be invisible)
        document.body.appendChild(this.video);
        
        console.log('[WebcamManager] Video element created');
    }

    /**
     * Start camera stream
     * @param {string} deviceId - Optional specific device ID
     * @returns {Promise<boolean>} - Success status
     */
    async startCamera(deviceId = null) {
        try {
            if (this.isActive) {
                console.log('[WebcamManager] Camera already active');
                return true;
            }
            
            console.log('[WebcamManager] Starting camera stream');
            
            const constraints = {
                video: {
                    width: { ideal: this.config.resolution.width },
                    height: { ideal: this.config.resolution.height },
                    facingMode: this.config.facingMode
                }
            };
            
            // Use specific device if provided
            if (deviceId || this.deviceId) {
                constraints.video.deviceId = { exact: deviceId || this.deviceId };
                delete constraints.video.facingMode; // Remove facingMode when using deviceId
            }
            
            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            
            if (this.video) {
                this.video.srcObject = this.stream;
                await new Promise(resolve => {
                    this.video.onloadedmetadata = resolve;
                });
            }
            
            this.isActive = true;
            this.updateCameraIndicator(true);
            
            // Start periodic capture if enabled
            if (this.config.captureMode === 'periodic') {
                this.startPeriodicCapture();
            }
            
            console.log('[WebcamManager] Camera started successfully');
            return true;
            
        } catch (error) {
            console.error('[WebcamManager] Failed to start camera:', error);
            this.handleError(error);
            return false;
        }
    }

    /**
     * Stop camera stream
     */
    async stopCamera() {
        try {
            console.log('[WebcamManager] Stopping camera stream');
            
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
                this.stream = null;
            }
            
            if (this.video) {
                this.video.srcObject = null;
            }
            
            this.isActive = false;
            this.updateCameraIndicator(false);
            
            // Stop periodic capture
            this.stopPeriodicCapture();
            
            console.log('[WebcamManager] Camera stopped');
            
        } catch (error) {
            console.error('[WebcamManager] Error stopping camera:', error);
        }
    }

    /**
     * Capture current frame from camera
     * @returns {Promise<string>} - Base64 image data
     */
    async captureFrame() {
        try {
            if (!this.isActive || !this.video) {
                throw new Error('Camera not active');
            }
            
            // Rate limiting
            const now = Date.now();
            if (now - this.lastCaptureTime < this.minCaptureInterval) {
                console.log('[WebcamManager] Capture rate limited');
                return null;
            }
            
            this.isCapturing = true;
            console.log('[WebcamManager] Capturing frame');
            
            // Create canvas for capture
            if (!this.canvas) {
                this.canvas = document.createElement('canvas');
            }
            
            const ctx = this.canvas.getContext('2d');
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
            
            // Draw current video frame to canvas
            ctx.drawImage(this.video, 0, 0);
            
            // Convert to base64
            const imageData = this.canvas.toDataURL('image/jpeg', this.config.quality);
            
            this.lastCaptureTime = now;
            this.isCapturing = false;
            
            console.log(`[WebcamManager] Frame captured: ${this.canvas.width}x${this.canvas.height}`);
            return imageData;
            
        } catch (error) {
            this.isCapturing = false;
            console.error('[WebcamManager] Failed to capture frame:', error);
            throw error;
        }
    }

    /**
     * Capture and process frame for object analysis
     * @returns {Promise<string>} - Processed image data
     */
    async captureForAnalysis() {
        try {
            console.log('[WebcamManager] Capturing frame for analysis');
            
            // Capture raw frame
            const rawImage = await this.captureFrame();
            if (!rawImage) return null;
            
            // Apply object detection and cropping
            let processedImage = rawImage;
            if (window.objectDetector) {
                processedImage = await window.objectDetector.detectAndCrop(rawImage);
            }
            
            // Apply image enhancement
            if (window.imageEnhancer) {
                processedImage = await window.imageEnhancer.enhanceForAnalysis(processedImage);
            }
            
            console.log('[WebcamManager] Frame processed for analysis');
            return processedImage;
            
        } catch (error) {
            console.error('[WebcamManager] Failed to capture for analysis:', error);
            throw error;
        }
    }

    /**
     * Start periodic image capture
     */
    startPeriodicCapture() {
        if (this.periodicTimer) return;
        
        console.log(`[WebcamManager] Starting periodic capture every ${this.config.periodicInterval}ms`);
        
        this.periodicTimer = setInterval(async () => {
            try {
                const imageData = await this.captureForAnalysis();
                if (imageData && window.visionAnalysisUI) {
                    window.visionAnalysisUI.handlePeriodicCapture(imageData);
                }
            } catch (error) {
                console.error('[WebcamManager] Periodic capture failed:', error);
            }
        }, this.config.periodicInterval);
    }

    /**
     * Stop periodic image capture
     */
    stopPeriodicCapture() {
        if (this.periodicTimer) {
            clearInterval(this.periodicTimer);
            this.periodicTimer = null;
            console.log('[WebcamManager] Periodic capture stopped');
        }
    }

    /**
     * Switch to different camera device
     * @param {string} deviceId - Device ID to switch to
     * @returns {Promise<boolean>} - Success status
     */
    async switchDevice(deviceId) {
        try {
            console.log('[WebcamManager] Switching to device:', deviceId);
            
            const wasActive = this.isActive;
            
            if (wasActive) {
                await this.stopCamera();
            }
            
            this.deviceId = deviceId;
            
            if (wasActive) {
                return await this.startCamera();
            }
            
            return true;
            
        } catch (error) {
            console.error('[WebcamManager] Failed to switch device:', error);
            return false;
        }
    }

    /**
     * Update camera indicator in UI
     * @param {boolean} active - Camera active status
     */
    updateCameraIndicator(active) {
        // Update existing mic-info element or create camera indicator
        const indicator = document.getElementById('camera-indicator') || 
                         document.getElementById('mic-info');
        
        if (indicator) {
            if (active) {
                indicator.textContent = '🔴 Camera Active';
                indicator.style.color = '#ff4444';
                indicator.classList.remove('hidden');
            } else {
                indicator.textContent = 'Camera Off';
                indicator.style.color = '#888';
            }
        }
        
        // Dispatch event for other components
        window.dispatchEvent(new CustomEvent('cameraStatusChanged', { 
            detail: { active, deviceId: this.deviceId }
        }));
    }

    /**
     * Handle camera errors
     * @param {Error} error - Error object
     */
    handleError(error) {
        let message = 'Camera error occurred';
        
        if (error.name === 'NotAllowedError') {
            message = 'Camera permission denied. Please allow camera access.';
        } else if (error.name === 'NotFoundError') {
            message = 'No camera found. Please connect a camera.';
        } else if (error.name === 'NotReadableError') {
            message = 'Camera is being used by another application.';
        } else if (error.name === 'OverconstrainedError') {
            message = 'Camera does not support requested settings.';
        }
        
        console.error('[WebcamManager] Error:', message, error);
        
        // Show error to user
        if (window.showError) {
            window.showError(message);
        }
        
        // Update UI
        this.updateCameraIndicator(false);
    }

    /**
     * Get current camera status
     * @returns {Object} - Status information
     */
    getStatus() {
        return {
            isActive: this.isActive,
            isCapturing: this.isCapturing,
            deviceId: this.deviceId,
            deviceCount: this.devices.length,
            config: this.config,
            lastCaptureTime: this.lastCaptureTime
        };
    }

    /**
     * Update configuration
     * @param {Object} newConfig - New configuration options
     */
    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
        
        console.log('[WebcamManager] Configuration updated:', this.config);
        
        // Restart periodic capture if interval changed
        if (newConfig.periodicInterval && this.config.captureMode === 'periodic' && this.isActive) {
            this.stopPeriodicCapture();
            this.startPeriodicCapture();
        }
    }

    /**
     * Get available camera devices
     * @returns {Array} - List of available devices
     */
    getDevices() {
        return this.devices.map(device => ({
            id: device.deviceId,
            label: device.label || `Camera ${device.deviceId.substr(0, 8)}...`
        }));
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        console.log('[WebcamManager] Cleaning up resources');
        
        this.stopCamera();
        this.stopPeriodicCapture();
        
        if (this.video && this.video.parentNode) {
            this.video.parentNode.removeChild(this.video);
        }
        
        this.video = null;
        this.canvas = null;
        this.stream = null;
    }
}

// Make WebcamManager available globally
window.WebcamManager = WebcamManager;

// Initialize global instance
window.webcamManager = new WebcamManager();

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await window.webcamManager.initialize();
        console.log('[WebcamManager] Auto-initialization completed');
    } catch (error) {
        console.error('[WebcamManager] Auto-initialization failed:', error);
    }
});

console.log('[WebcamManager] Module loaded');