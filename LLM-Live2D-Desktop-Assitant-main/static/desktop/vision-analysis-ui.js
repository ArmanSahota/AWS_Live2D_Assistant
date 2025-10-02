/**
 * Vision Analysis UI Module
 * 
 * This module provides the user interface for object analysis functionality.
 * It handles camera controls, analysis triggers, result display, and user interactions.
 */

class VisionAnalysisUI {
    constructor() {
        this.analysisInProgress = false;
        this.lastAnalysis = null;
        this.confidenceThreshold = 0.7;
        this.analysisHistory = [];
        this.maxHistoryItems = 10;
        
        this.elements = {};
        this.isInitialized = false;
        
        console.log('[VisionAnalysisUI] Initialized');
    }

    /**
     * Initialize the vision analysis interface
     */
    async initialize() {
        if (this.isInitialized) return;
        
        try {
            console.log('[VisionAnalysisUI] Creating analysis interface');
            
            this.createAnalysisInterface();
            this.bindEvents();
            this.updateUI();
            
            this.isInitialized = true;
            console.log('[VisionAnalysisUI] Interface initialized successfully');
            
        } catch (error) {
            console.error('[VisionAnalysisUI] Failed to initialize:', error);
        }
    }

    /**
     * Create the main analysis interface
     */
    createAnalysisInterface() {
        // Create main container
        const container = document.createElement('div');
        container.id = 'vision-analysis-container';
        container.innerHTML = `
            <div class="vision-panel">
                <div class="vision-header">
                    <h3>🔍 Object Analysis</h3>
                    <button id="vision-toggle" class="toggle-btn">Enable Vision</button>
                </div>
                
                <div class="vision-controls">
                    <div class="control-group">
                        <button id="analyze-object-btn" class="primary-btn" disabled>
                            📷 Analyze Object
                        </button>
                        <button id="start-camera-btn" class="secondary-btn">
                            🎥 Start Camera
                        </button>
                    </div>
                    
                    <div class="control-group">
                        <label for="capture-mode">Capture Mode:</label>
                        <select id="capture-mode">
                            <option value="manual">Manual</option>
                            <option value="speech-triggered">On Speech</option>
                            <option value="periodic">Periodic</option>
                        </select>
                    </div>
                    
                    <div class="control-group">
                        <label for="camera-select">Camera:</label>
                        <select id="camera-select">
                            <option value="">Loading cameras...</option>
                        </select>
                    </div>
                </div>
                
                <div id="analysis-status" class="status-indicator">
                    Vision system ready
                </div>
                
                <div id="camera-preview-container" class="preview-container hidden">
                    <canvas id="preview-canvas"></canvas>
                    <div id="detection-overlay" class="overlay"></div>
                </div>
                
                <div id="analysis-results" class="results-container hidden">
                    <div class="result-header">
                        <h4 id="analysis-title">Analysis Results</h4>
                        <div id="confidence-score" class="confidence-badge"></div>
                    </div>
                    <div id="analysis-content" class="content-area"></div>
                    <div class="result-actions">
                        <button id="save-analysis-btn" class="action-btn">💾 Save</button>
                        <button id="share-analysis-btn" class="action-btn">📤 Share</button>
                        <button id="retry-analysis-btn" class="action-btn">🔄 Retry</button>
                    </div>
                </div>
                
                <div id="analysis-history" class="history-container hidden">
                    <h4>Recent Analyses</h4>
                    <div id="history-list" class="history-list"></div>
                </div>
            </div>
        `;
        
        // Add styles
        this.addStyles();
        
        // Insert into existing test panel or create new container
        const testPanel = document.getElementById('test-panel');
        if (testPanel) {
            testPanel.appendChild(container);
        } else {
            document.body.appendChild(container);
        }
        
        // Store element references
        this.elements = {
            container: container,
            toggleBtn: document.getElementById('vision-toggle'),
            analyzeBtn: document.getElementById('analyze-object-btn'),
            startCameraBtn: document.getElementById('start-camera-btn'),
            captureMode: document.getElementById('capture-mode'),
            cameraSelect: document.getElementById('camera-select'),
            status: document.getElementById('analysis-status'),
            previewContainer: document.getElementById('camera-preview-container'),
            previewCanvas: document.getElementById('preview-canvas'),
            detectionOverlay: document.getElementById('detection-overlay'),
            results: document.getElementById('analysis-results'),
            analysisTitle: document.getElementById('analysis-title'),
            confidenceScore: document.getElementById('confidence-score'),
            analysisContent: document.getElementById('analysis-content'),
            saveBtn: document.getElementById('save-analysis-btn'),
            shareBtn: document.getElementById('share-analysis-btn'),
            retryBtn: document.getElementById('retry-analysis-btn'),
            history: document.getElementById('analysis-history'),
            historyList: document.getElementById('history-list')
        };
    }

    /**
     * Add CSS styles for the vision interface
     */
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .vision-panel {
                background: rgba(0, 0, 0, 0.8);
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                color: white;
                font-family: Arial, sans-serif;
                max-width: 400px;
            }
            
            .vision-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                border-bottom: 1px solid #333;
                padding-bottom: 10px;
            }
            
            .vision-header h3 {
                margin: 0;
                color: #4CAF50;
            }
            
            .toggle-btn {
                background: #2196F3;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
            }
            
            .toggle-btn:hover {
                background: #1976D2;
            }
            
            .toggle-btn.active {
                background: #4CAF50;
            }
            
            .vision-controls {
                margin-bottom: 15px;
            }
            
            .control-group {
                margin-bottom: 10px;
            }
            
            .control-group label {
                display: block;
                margin-bottom: 5px;
                font-size: 12px;
                color: #ccc;
            }
            
            .primary-btn, .secondary-btn, .action-btn {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                cursor: pointer;
                margin-right: 5px;
                margin-bottom: 5px;
                font-size: 12px;
            }
            
            .secondary-btn {
                background: #FF9800;
            }
            
            .action-btn {
                background: #2196F3;
                padding: 5px 8px;
                font-size: 11px;
            }
            
            .primary-btn:disabled {
                background: #666;
                cursor: not-allowed;
            }
            
            .primary-btn:hover:not(:disabled) {
                background: #45a049;
            }
            
            .secondary-btn:hover {
                background: #F57C00;
            }
            
            .action-btn:hover {
                background: #1976D2;
            }
            
            select {
                width: 100%;
                padding: 5px;
                border-radius: 4px;
                border: 1px solid #555;
                background: #333;
                color: white;
                font-size: 12px;
            }
            
            .status-indicator {
                background: #333;
                padding: 8px;
                border-radius: 4px;
                text-align: center;
                font-size: 12px;
                margin-bottom: 10px;
            }
            
            .status-indicator.processing {
                background: #FF9800;
                animation: pulse 1.5s infinite;
            }
            
            .status-indicator.success {
                background: #4CAF50;
            }
            
            .status-indicator.error {
                background: #f44336;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.7; }
                100% { opacity: 1; }
            }
            
            .preview-container {
                margin-bottom: 15px;
                position: relative;
                border: 2px solid #333;
                border-radius: 4px;
                overflow: hidden;
            }
            
            #preview-canvas {
                width: 100%;
                height: auto;
                display: block;
            }
            
            .overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                pointer-events: none;
            }
            
            .results-container {
                background: #222;
                border-radius: 4px;
                padding: 10px;
                margin-bottom: 10px;
            }
            
            .result-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            
            .result-header h4 {
                margin: 0;
                color: #4CAF50;
            }
            
            .confidence-badge {
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
            }
            
            .confidence-badge.high-confidence {
                background: #4CAF50;
                color: white;
            }
            
            .confidence-badge.medium-confidence {
                background: #FF9800;
                color: white;
            }
            
            .confidence-badge.low-confidence {
                background: #f44336;
                color: white;
            }
            
            .content-area {
                max-height: 200px;
                overflow-y: auto;
                font-size: 12px;
                line-height: 1.4;
            }
            
            .analysis-section {
                margin-bottom: 10px;
                padding: 8px;
                background: #333;
                border-radius: 4px;
            }
            
            .analysis-section h4 {
                margin: 0 0 5px 0;
                color: #4CAF50;
                font-size: 13px;
            }
            
            .analysis-paragraph {
                margin: 5px 0;
            }
            
            .result-actions {
                margin-top: 10px;
                text-align: center;
            }
            
            .history-container {
                background: #222;
                border-radius: 4px;
                padding: 10px;
                max-height: 150px;
                overflow-y: auto;
            }
            
            .history-container h4 {
                margin: 0 0 10px 0;
                color: #4CAF50;
                font-size: 13px;
            }
            
            .history-item {
                background: #333;
                padding: 5px 8px;
                margin-bottom: 5px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 11px;
            }
            
            .history-item:hover {
                background: #444;
            }
            
            .hidden {
                display: none !important;
            }
        `;
        
        document.head.appendChild(style);
    }

    /**
     * Bind event handlers
     */
    bindEvents() {
        // Vision toggle
        this.elements.toggleBtn.addEventListener('click', () => {
            this.toggleVisionSystem();
        });
        
        // Camera controls
        this.elements.startCameraBtn.addEventListener('click', () => {
            this.toggleCamera();
        });
        
        // Analysis trigger
        this.elements.analyzeBtn.addEventListener('click', () => {
            this.startObjectAnalysis();
        });
        
        // Capture mode change
        this.elements.captureMode.addEventListener('change', (e) => {
            this.updateCaptureMode(e.target.value);
        });
        
        // Camera selection
        this.elements.cameraSelect.addEventListener('change', (e) => {
            this.switchCamera(e.target.value);
        });
        
        // Result actions
        this.elements.saveBtn.addEventListener('click', () => {
            this.saveAnalysis();
        });
        
        this.elements.shareBtn.addEventListener('click', () => {
            this.shareAnalysis();
        });
        
        this.elements.retryBtn.addEventListener('click', () => {
            this.retryAnalysis();
        });
        
        // Listen for camera status changes
        window.addEventListener('cameraStatusChanged', (e) => {
            this.handleCameraStatusChange(e.detail);
        });
        
        // Listen for voice commands
        window.addEventListener('voiceCommand', (e) => {
            this.handleVoiceCommand(e.detail);
        });
    }

    /**
     * Update UI state
     */
    updateUI() {
        // Update camera list
        this.updateCameraList();
        
        // Update button states
        const cameraActive = window.webcamManager && window.webcamManager.isActive;
        this.elements.analyzeBtn.disabled = !cameraActive || this.analysisInProgress;
        this.elements.startCameraBtn.textContent = cameraActive ? '⏹️ Stop Camera' : '🎥 Start Camera';
        
        // Update capture mode
        if (window.webcamManager) {
            this.elements.captureMode.value = window.webcamManager.config.captureMode;
        }
    }

    /**
     * Update available camera list
     */
    async updateCameraList() {
        if (!window.webcamManager) return;
        
        try {
            const devices = window.webcamManager.getDevices();
            const select = this.elements.cameraSelect;
            
            select.innerHTML = '';
            
            if (devices.length === 0) {
                select.innerHTML = '<option value="">No cameras found</option>';
                return;
            }
            
            devices.forEach(device => {
                const option = document.createElement('option');
                option.value = device.id;
                option.textContent = device.label;
                select.appendChild(option);
            });
            
            // Select current device
            if (window.webcamManager.deviceId) {
                select.value = window.webcamManager.deviceId;
            }
            
        } catch (error) {
            console.error('[VisionAnalysisUI] Failed to update camera list:', error);
        }
    }

    /**
     * Toggle vision system on/off
     */
    async toggleVisionSystem() {
        const isEnabled = this.elements.toggleBtn.classList.contains('active');
        
        if (isEnabled) {
            // Disable vision system
            await this.disableVisionSystem();
        } else {
            // Enable vision system
            await this.enableVisionSystem();
        }
    }

    /**
     * Enable vision system
     */
    async enableVisionSystem() {
        try {
            this.updateStatus('Initializing vision system...', 'processing');
            
            // Initialize webcam manager if not already done
            if (window.webcamManager && !window.webcamManager.isActive) {
                const success = await window.webcamManager.initialize();
                if (!success) {
                    throw new Error('Failed to initialize camera system');
                }
            }
            
            this.elements.toggleBtn.classList.add('active');
            this.elements.toggleBtn.textContent = 'Disable Vision';
            
            this.updateStatus('Vision system enabled', 'success');
            this.updateUI();
            
            console.log('[VisionAnalysisUI] Vision system enabled');
            
        } catch (error) {
            console.error('[VisionAnalysisUI] Failed to enable vision system:', error);
            this.updateStatus('Failed to enable vision system', 'error');
        }
    }

    /**
     * Disable vision system
     */
    async disableVisionSystem() {
        try {
            // Stop camera if active
            if (window.webcamManager && window.webcamManager.isActive) {
                await window.webcamManager.stopCamera();
            }
            
            this.elements.toggleBtn.classList.remove('active');
            this.elements.toggleBtn.textContent = 'Enable Vision';
            
            this.elements.previewContainer.classList.add('hidden');
            this.elements.results.classList.add('hidden');
            
            this.updateStatus('Vision system disabled');
            this.updateUI();
            
            console.log('[VisionAnalysisUI] Vision system disabled');
            
        } catch (error) {
            console.error('[VisionAnalysisUI] Failed to disable vision system:', error);
        }
    }

    /**
     * Toggle camera on/off
     */
    async toggleCamera() {
        if (!window.webcamManager) {
            this.updateStatus('Webcam manager not available', 'error');
            return;
        }
        
        try {
            if (window.webcamManager.isActive) {
                await window.webcamManager.stopCamera();
                this.elements.previewContainer.classList.add('hidden');
            } else {
                const success = await window.webcamManager.startCamera();
                if (success) {
                    this.elements.previewContainer.classList.remove('hidden');
                    this.startPreview();
                }
            }
            
            this.updateUI();
            
        } catch (error) {
            console.error('[VisionAnalysisUI] Failed to toggle camera:', error);
            this.updateStatus('Camera error occurred', 'error');
        }
    }

    /**
     * Start camera preview
     */
    startPreview() {
        // This is a simple preview - in a full implementation,
        // you might want to show live camera feed
        const canvas = this.elements.previewCanvas;
        const ctx = canvas.getContext('2d');
        
        canvas.width = 320;
        canvas.height = 240;
        
        // Draw placeholder
        ctx.fillStyle = '#333';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#fff';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Camera Active', canvas.width / 2, canvas.height / 2);
        ctx.font = '12px Arial';
        ctx.fillText('Ready for analysis', canvas.width / 2, canvas.height / 2 + 20);
    }

    /**
     * Start object analysis
     */
    async startObjectAnalysis() {
        if (this.analysisInProgress) return;
        
        try {
            this.analysisInProgress = true;
            this.updateStatus('Capturing and analyzing object...', 'processing');
            this.elements.analyzeBtn.disabled = true;
            
            // Capture image for analysis
            const imageData = await window.webcamManager.captureForAnalysis();
            if (!imageData) {
                throw new Error('Failed to capture image');
            }
            
            // Show preview of captured image
            this.showCapturedImage(imageData);
            
            // Send for analysis via WebSocket
            const result = await this.sendForAnalysis(imageData);
            
            // Display results
            this.displayAnalysisResults(result);
            this.addToHistory(result);
            
            this.updateStatus('Analysis completed', 'success');
            
        } catch (error) {
            console.error('[VisionAnalysisUI] Analysis failed:', error);
            this.updateStatus('Analysis failed: ' + error.message, 'error');
        } finally {
            this.analysisInProgress = false;
            this.updateUI();
        }
    }

    /**
     * Show captured image in preview
     */
    showCapturedImage(imageData) {
        const canvas = this.elements.previewCanvas;
        const ctx = canvas.getContext('2d');
        
        const img = new Image();
        img.onload = () => {
            canvas.width = Math.min(img.width, 320);
            canvas.height = (canvas.width / img.width) * img.height;
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        };
        img.src = imageData;
    }

    /**
     * Send image for analysis
     */
    async sendForAnalysis(imageData) {
        return new Promise((resolve, reject) => {
            const analysisId = Date.now().toString();
            let timeoutId;
            let originalOnMessage;
            
            // Set up timeout
            timeoutId = setTimeout(() => {
                console.log('[VisionAnalysisUI] Analysis timeout after 30 seconds');
                // Restore original message handler
                if (originalOnMessage && window.ws) {
                    window.ws.onmessage = originalOnMessage;
                }
                reject(new Error('Analysis timeout'));
            }, 30000);
            
            // Check WebSocket connection
            if (!window.ws || window.ws.readyState !== WebSocket.OPEN) {
                clearTimeout(timeoutId);
                reject(new Error('WebSocket not connected'));
                return;
            }
            
            // Store original message handler
            originalOnMessage = window.ws.onmessage;
            
            // Set up response handler
            const responseHandler = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('[VisionAnalysisUI] ===== RECEIVED WEBSOCKET MESSAGE =====');
                    console.log('[VisionAnalysisUI] Message type:', data.type);
                    console.log('[VisionAnalysisUI] Analysis ID in message:', data.analysisId);
                    console.log('[VisionAnalysisUI] Expected analysis ID:', analysisId);
                    console.log('[VisionAnalysisUI] Full message:', data);
                    
                    if (data.type === 'object-analysis-result' && data.analysisId === analysisId) {
                        console.log('[VisionAnalysisUI] ✅ ANALYSIS RESULT MATCHED - Processing...');
                        clearTimeout(timeoutId);
                        
                        // Restore original message handler
                        if (originalOnMessage) {
                            window.ws.onmessage = originalOnMessage;
                        }
                        
                        resolve(data.result);
                    } else if (data.type === 'error' && data.analysisId === analysisId) {
                        console.error('[VisionAnalysisUI] ❌ ANALYSIS ERROR MATCHED:', data.error);
                        clearTimeout(timeoutId);
                        
                        // Restore original message handler
                        if (originalOnMessage) {
                            window.ws.onmessage = originalOnMessage;
                        }
                        
                        reject(new Error(data.error || 'Analysis failed'));
                    } else {
                        console.log('[VisionAnalysisUI] 📨 Message not for this analysis - passing to original handler');
                        // Pass other messages to original handler
                        if (originalOnMessage) {
                            originalOnMessage(event);
                        }
                    }
                } catch (error) {
                    console.error('[VisionAnalysisUI] ❌ Error parsing WebSocket response:', error);
                    console.error('[VisionAnalysisUI] Raw event data:', event.data);
                    // Pass to original handler in case it's not our message
                    if (originalOnMessage) {
                        originalOnMessage(event);
                    }
                }
            };
            
            // Set new message handler
            window.ws.onmessage = responseHandler;
            
            // Send analysis request
            const requestMessage = {
                type: 'object-analysis-request',
                analysisId: analysisId,
                imageData: imageData.split(',')[1], // Remove data URL prefix
                userQuestion: 'What is this object? Can you analyze it?',
                timestamp: Date.now()
            };
            
            console.log('[VisionAnalysisUI] Sending analysis request with ID:', analysisId);
            console.log('[VisionAnalysisUI] WebSocket state:', window.ws.readyState);
            console.log('[VisionAnalysisUI] Request message:', {
                type: requestMessage.type,
                analysisId: requestMessage.analysisId,
                imageDataLength: requestMessage.imageData ? requestMessage.imageData.length : 0,
                userQuestion: requestMessage.userQuestion,
                timestamp: requestMessage.timestamp
            });
            
            window.ws.send(JSON.stringify(requestMessage));
            console.log('[VisionAnalysisUI] Message sent successfully');
        });
    }

    /**
     * Display analysis results
     */
    displayAnalysisResults(result) {
        this.lastAnalysis = result;
        
        // Update title and confidence
        this.elements.analysisTitle.textContent = result.category || 'Object Analysis';
        
        const confidence = result.confidence || 0;
        this.elements.confidenceScore.textContent = `${Math.round(confidence * 100)}% confidence`;
        this.elements.confidenceScore.className = `confidence-badge ${this.getConfidenceClass(confidence)}`;
        
        // Format and display content
        this.elements.analysisContent.innerHTML = this.formatAnalysisContent(result.analysis || 'Analysis completed');
        
        // Show results
        this.elements.results.classList.remove('hidden');
    }

    /**
     * Format analysis content for display
     */
    formatAnalysisContent(analysisText) {
        const sections = analysisText.split('\n\n');
        let html = '';
        
        sections.forEach(section => {
            if (section.trim()) {
                if (section.includes(':')) {
                    const [title, ...content] = section.split(':');
                    html += `
                        <div class="analysis-section">
                            <h4>${title.trim()}</h4>
                            <p>${content.join(':').trim()}</p>
                        </div>
                    `;
                } else {
                    html += `<p class="analysis-paragraph">${section.trim()}</p>`;
                }
            }
        });
        
        return html || '<p>Analysis completed successfully.</p>';
    }

    /**
     * Get confidence class for styling
     */
    getConfidenceClass(confidence) {
        if (confidence >= 0.8) return 'high-confidence';
        if (confidence >= 0.6) return 'medium-confidence';
        return 'low-confidence';
    }

    /**
     * Add analysis to history
     */
    addToHistory(result) {
        this.analysisHistory.unshift({
            timestamp: Date.now(),
            result: result
        });
        
        // Limit history size
        if (this.analysisHistory.length > this.maxHistoryItems) {
            this.analysisHistory = this.analysisHistory.slice(0, this.maxHistoryItems);
        }
        
        this.updateHistoryDisplay();
    }

    /**
     * Update history display
     */
    updateHistoryDisplay() {
        const historyList = this.elements.historyList;
        historyList.innerHTML = '';
        
        this.analysisHistory.forEach((item, index) => {
            const div = document.createElement('div');
            div.className = 'history-item';
            div.textContent = `${new Date(item.timestamp).toLocaleTimeString()}: ${item.result.category || 'Analysis'}`;
            div.addEventListener('click', () => {
                this.displayAnalysisResults(item.result);
            });
            historyList.appendChild(div);
        });
        
        if (this.analysisHistory.length > 0) {
            this.elements.history.classList.remove('hidden');
        }
    }

    /**
     * Update status display
     */
    updateStatus(message, type = 'info') {
        this.elements.status.textContent = message;
        this.elements.status.className = `status-indicator ${type}`;
    }

    /**
     * Handle camera status changes
     */
    handleCameraStatusChange(detail) {
        this.updateUI();
        
        if (detail.active) {
            this.updateStatus('Camera started successfully', 'success');
        } else {
            this.updateStatus('Camera stopped');
        }
    }

    /**
     * Handle voice commands
     */
    handleVoiceCommand(command) {
        const lowerCommand = command.toLowerCase();
        
        if (lowerCommand.includes('analyze') || lowerCommand.includes('what is this')) {
            if (window.webcamManager && window.webcamManager.isActive) {
                this.startObjectAnalysis();
            } else {
                this.updateStatus('Camera not active for analysis', 'error');
            }
        }
    }

    /**
     * Update capture mode
     */
    updateCaptureMode(mode) {
        if (window.webcamManager) {
            window.webcamManager.updateConfig({ captureMode: mode });
            console.log('[VisionAnalysisUI] Capture mode updated to:', mode);
        }
    }

    /**
     * Switch camera device
     */
    async switchCamera(deviceId) {
        if (window.webcamManager && deviceId) {
            try {
                await window.webcamManager.switchDevice(deviceId);
                this.updateStatus('Camera switched successfully', 'success');
            } catch (error) {
                console.error('[VisionAnalysisUI] Failed to switch camera:', error);
                this.updateStatus('Failed to switch camera', 'error');
            }
        }
    }

    /**
     * Save analysis results
     */
    saveAnalysis() {
        if (!this.lastAnalysis) return;
        
        const data = {
            timestamp: Date.now(),
            analysis: this.lastAnalysis,
            version: '1.0'
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `analysis_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        
        this.updateStatus('Analysis saved successfully', 'success');
    }

    /**
     * Share analysis results
     */
    shareAnalysis() {
        if (!this.lastAnalysis) return;
        
        const text = `Object Analysis Results:\n\n${this.lastAnalysis.analysis}`;
        
        if (navigator.share) {
            navigator.share({
                title: 'Object Analysis Results',
                text: text
            });
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(text).then(() => {
                this.updateStatus('Analysis copied to clipboard', 'success');
            });
        }
    }

    /**
     * Retry last analysis
     */
    retryAnalysis() {
        if (window.webcamManager && window.webcamManager.isActive) {
            this.startObjectAnalysis();
        } else {
            this.updateStatus('Camera not active for retry', 'error');
        }
    }

    /**
     * Handle periodic capture (for periodic mode)
     */
    handlePeriodicCapture(imageData) {
        if (this.analysisInProgress) return;
        
        console.log('[VisionAnalysisUI] Handling periodic capture');
        // Could auto-analyze or just update preview
        this.showCapturedImage(imageData);
    }

    /**
     * Get current UI state
     */
    getState() {
        return {
            isInitialized: this.isInitialized,
            analysisInProgress: this.analysisInProgress,
            historyCount: this.analysisHistory.length,
            lastAnalysisTime: this.lastAnalysis ? this.lastAnalysis.timestamp : null
        };
    }
}

// Make VisionAnalysisUI available globally
window.VisionAnalysisUI = VisionAnalysisUI;

// Initialize global instance
window.visionAnalysisUI = new VisionAnalysisUI();

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await window.visionAnalysisUI.initialize();
        console.log('[VisionAnalysisUI] Auto-initialization completed');
    } catch (error) {
        console.error('[VisionAnalysisUI] Auto-initialization failed:', error);
    }
});

console.log('[VisionAnalysisUI] Module loaded');