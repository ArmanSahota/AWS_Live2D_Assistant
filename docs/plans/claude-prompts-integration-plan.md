# Claude Prompts Best Practices Integration Plan
## AWS VTuber LLM Desktop Assistant Enhancement

## Executive Summary

This plan integrates the proven methodologies from [`Claude_Prompts_RooCode`](Claude_Prompts_RooCode/) with the existing AWS VTuber LLM project. Rather than replacing the excellent [`implementation-todo-list.md`](implementation-todo-list.md), this enhances it with VTuber-specific adaptations of systematic debugging, memory management, automated testing, and multi-model AI workflows.

## Current Project Status Analysis

### ✅ What's Already Excellent
- **Working System**: AWS Claude 3.5 Sonnet integration operational
- **Comprehensive Planning**: [`implementation-todo-list.md`](implementation-todo-list.md) covers 6 phases
- **AWS Architecture**: Detailed migration plan in [`aws-migration-plan.md`](aws-migration-plan.md)
- **Live2D Integration**: Desktop VTuber with drag functionality
- **Audio Pipeline**: Whisper STT + Edge TTS working

### 🔄 Integration Opportunities
- **Memory Bank System**: Adapt for VTuber-specific context tracking
- **Circuit Breaker Debugging**: Apply to Live2D and audio pipeline issues
- **Puppeteer Testing**: Create VTuber desktop interaction tests
- **Multi-Model Workflows**: Implement for different development tasks
- **Code Reuse Analysis**: Audit existing codebase systematically

---

## Phase 1: VTuber Memory Bank System (Week 1)

### 1.1 Create VTuber-Specific Memory Bank Structure

```bash
mkdir memory-bank
mkdir memory-bank/features
mkdir memory-bank/debugging-sessions
mkdir memory-bank/testing-results
```

### 1.2 Core Memory Files (VTuber-Adapted)

#### [`memory-bank/projectbrief.md`](memory-bank/projectbrief.md)
```markdown
# AWS VTuber LLM Desktop Assistant - Project Brief

## Core Mission
Create an always-available desktop AI companion with Live2D avatar, powered by AWS Claude, providing natural voice interaction and contextual assistance.

## Key Success Criteria
- Sub-2 second response latency for voice interactions
- Seamless Live2D animation sync with speech
- 99.9% AWS Claude integration uptime
- Natural desktop integration (drag, minimize, system tray)
- Privacy-first local audio processing
```

#### [`memory-bank/activeContext.md`](memory-bank/activeContext.md)
```markdown
# Current Development Context

## Active Work Focus
- System is operational with Claude 3.5 Sonnet
- AWS endpoints configured and working
- Live2D free-roaming desktop character implemented

## Recent Achievements
- Fixed Live2D model loading issues
- Implemented drag functionality
- AWS Claude integration complete
- Audio pipeline (Whisper + Edge TTS) operational

## Current Priorities
1. Security fixes (Python injection vulnerability)
2. Wake word implementation
3. Performance optimization
4. Enhanced testing automation

## Known Issues
- Wake word files missing (using empty file workaround)
- Python injection vulnerability in ipc.js:296
- First Claude response slow (cold start)
```

#### [`memory-bank/systemPatterns.md`](memory-bank/systemPatterns.md)
```markdown
# VTuber System Architecture Patterns

## Communication Flow
```
User Voice → Whisper STT → Text Processing → AWS Claude → Response → Edge TTS → Audio + Live2D Animation
```

## Key Components
- **Frontend**: Electron app with Live2D rendering
- **Backend**: Python server (port 1018) with WebSocket
- **AI**: AWS Bedrock Claude 3.5 Sonnet
- **Audio**: Local Whisper + Edge TTS for privacy
- **Desktop**: Free-roaming draggable character

## Critical Patterns
- WebSocket for real-time communication
- Local audio processing for low latency
- AWS for intelligence, local for privacy
- Live2D animation sync with speech timing
```

### 1.3 VTuber-Specific Feature Documentation

#### [`memory-bank/features/live2d-desktop-integration.md`](memory-bank/features/live2d-desktop-integration.md)
```markdown
# Live2D Desktop Integration

## Current Implementation
- Free-roaming desktop character
- Drag functionality implemented
- Model loading fixes applied
- Animation sync with TTS

## Key Files
- `static/desktop/live2d.js` - Core Live2D logic
- `static/desktop/models/default/` - Default model assets
- `src/main/models.js` - Model management

## Common Issues & Solutions
- Model loading: Check file paths and permissions
- Animation sync: Verify TTS timing callbacks
- Performance: Monitor FPS and memory usage
```

### 1.4 Immediate Action Items

- [ ] **Create memory bank directory structure**
- [ ] **Document current system state in memory files**
- [ ] **Add memory bank update script to [`package.json`](LLM-Live2D-Desktop-Assitant-main/package.json)**
- [ ] **Create memory bank reading workflow for development sessions**

---

## Phase 2: VTuber Circuit Breaker Debugging (Week 2)

### 2.1 VTuber-Specific Debugging Scenarios

#### Common VTuber Issues & Circuit Breaker Patterns

```python
# utils/vtuber_debugging_circuit_breaker.py
class VTuberDebuggingCircuitBreaker:
    def __init__(self):
        self.common_issues = {
            'live2d_model_loading': 0,
            'audio_sync_problems': 0,
            'aws_connection_failures': 0,
            'websocket_disconnects': 0,
            'tts_audio_issues': 0
        }
        self.max_attempts = 3
    
    def debug_live2d_issue(self, error_type):
        """Apply systematic debugging to Live2D issues"""
        if self.should_try_different_approach(error_type):
            return self.escalate_to_multi_model_analysis(error_type)
        
        # Standard debugging workflow
        return self.apply_systematic_debugging(error_type)
    
    def common_vtuber_debugging_steps(self, issue_type):
        """VTuber-specific debugging workflows"""
        workflows = {
            'live2d_model_loading': [
                'Check model file paths and permissions',
                'Verify model3.json structure',
                'Test with default model',
                'Check console for WebGL errors'
            ],
            'audio_sync_problems': [
                'Verify TTS timing callbacks',
                'Check audio buffer sizes',
                'Test with different TTS voices',
                'Monitor WebSocket message timing'
            ],
            'aws_connection_failures': [
                'Verify AWS credentials',
                'Check endpoint URLs',
                'Test with curl/Postman',
                'Monitor CloudWatch logs'
            ]
        }
        return workflows.get(issue_type, [])
```

### 2.2 Enhanced Diagnostic Scripts

#### Update Existing Diagnostic Tools
- [ ] **Enhance [`LLM-Live2D-Desktop-Assitant-main/static/desktop/diagnostics.js`](LLM-Live2D-Desktop-Assitant-main/static/desktop/diagnostics.js)** with circuit breaker
- [ ] **Add systematic debugging to audio pipeline tests**
- [ ] **Create VTuber-specific error tracking**

### 2.3 Debugging Session Documentation

#### [`memory-bank/debugging-sessions/template.md`](memory-bank/debugging-sessions/template.md)
```markdown
# VTuber Debugging Session: [Issue Description]

## Issue Type: [live2d_model_loading | audio_sync_problems | aws_connection_failures]

### Hypothesis 1: [What you think is wrong]
- **Test**: [How you'll test it]
- **Result**: [What happened]
- **Conclusion**: [Was hypothesis correct?]

### Hypothesis 2: [Different angle]
- **Test**: [Different test approach]  
- **Result**: [What happened]
- **Conclusion**: [Learning from this test]

### Circuit Breaker Status
- **Attempts**: [Current attempt count]
- **Escalation Needed**: [Yes/No - if 3+ attempts of same approach]

### Solution Found
- **Root Cause**: [Actual problem]
- **Fix Applied**: [What fixed it]
- **Prevention**: [How to avoid in future]
```

---

## Phase 3: VTuber Puppeteer Testing (Week 3)

### 3.1 VTuber-Specific Test Scenarios

#### Desktop Interaction Tests
```javascript
// tests/puppeteer/vtuber-desktop-tests.js
class VTuberDesktopTests {
    async testLive2DRendering() {
        // Test Live2D model loading and rendering
        await this.navigateToDesktopApp();
        await this.waitForLive2DLoad();
        await this.verifyModelRendering();
        await this.testAnimationPlayback();
    }
    
    async testDragFunctionality() {
        // Test desktop character dragging
        const characterElement = await this.findLive2DCharacter();
        await this.dragCharacterToPosition(100, 100);
        await this.verifyCharacterPosition();
    }
    
    async testAudioPipeline() {
        // Test voice interaction workflow
        await this.simulateVoiceInput("Hello, can you hear me?");
        await this.waitForSTTProcessing();
        await this.waitForClaudeResponse();
        await this.waitForTTSPlayback();
        await this.verifyLive2DAnimationSync();
    }
    
    async testAWSIntegration() {
        // Test AWS Claude connectivity
        await this.sendTestMessage("Test AWS connection");
        await this.verifyClaudeResponse();
        await this.checkResponseLatency();
    }
}
```

### 3.2 Electron App Testing Strategy

#### Desktop-Specific Test Patterns
```javascript
// tests/puppeteer/electron-vtuber-tests.js
class ElectronVTuberTests {
    async testSystemTrayIntegration() {
        // Test system tray functionality
        await this.minimizeToTray();
        await this.restoreFromTray();
        await this.verifyAppState();
    }
    
    async testAlwaysOnTopBehavior() {
        // Test desktop overlay functionality
        await this.enableAlwaysOnTop();
        await this.openOtherApplication();
        await this.verifyVTuberStaysOnTop();
    }
    
    async testPerformanceMetrics() {
        // Monitor VTuber performance
        const metrics = await this.capturePerformanceMetrics();
        await this.verifyFPSTarget(60);
        await this.verifyMemoryUsage();
        await this.verifyResponseLatency();
    }
}
```

### 3.3 Automated Testing Integration

#### Enhanced Package.json Scripts
```json
{
  "scripts": {
    "test:vtuber-full": "node tests/puppeteer/vtuber-full-suite.js",
    "test:live2d": "node tests/puppeteer/live2d-rendering-test.js",
    "test:audio-pipeline": "node tests/puppeteer/audio-pipeline-test.js",
    "test:aws-integration": "node tests/puppeteer/aws-integration-test.js",
    "test:desktop-interaction": "node tests/puppeteer/desktop-interaction-test.js",
    "dev:test-watch": "concurrently \"npm start\" \"npm run test:vtuber-full\""
  }
}
```

---

## Phase 4: Multi-Model AI Workflow Integration (Week 4)

### 4.1 VTuber Development Model Selection

#### Model Assignment Matrix
| Development Task | Primary Model | Rationale |
|------------------|---------------|-----------|
| **Live2D Architecture Design** | Gemini 2.5-Pro | Complex system relationships, visual component planning |
| **Audio Pipeline Implementation** | GPT-5 | Real-time processing algorithms, performance optimization |
| **AWS Integration Analysis** | Claude | Context understanding, debugging, documentation |
| **Desktop UI/UX Design** | Gemini 2.5-Pro | User experience flows, interaction patterns |
| **Performance Optimization** | GPT-5 | Algorithm efficiency, code optimization |
| **Bug Analysis & Debugging** | Claude | Context analysis, systematic problem solving |

### 4.2 Multi-Model Workflow Examples

#### Live2D Model Integration Workflow
```javascript
// 1. Architecture Planning (Gemini)
await mcp__zen__chat({
  model: "gemini-2.5-pro",
  prompt: "Design optimal Live2D model loading and rendering architecture for desktop VTuber",
  files: ["static/desktop/live2d.js", "src/main/models.js"]
});

// 2. Implementation (GPT)
await mcp__zen__chat({
  model: "gpt-5",
  prompt: "Implement efficient Live2D model caching and preloading system",
  files: ["static/desktop/live2d.js"]
});

// 3. Analysis & Testing (Claude)
// Claude handles the verification and integration testing
```

#### Audio Pipeline Optimization Workflow
```javascript
// 1. System Analysis (Claude)
// Analyze current audio pipeline performance and bottlenecks

// 2. Architecture Design (Gemini)
await mcp__zen__chat({
  model: "gemini-2.5-pro", 
  prompt: "Design low-latency audio processing architecture for real-time VTuber interaction",
  files: ["server.py", "module/audio_manager.py"]
});

// 3. Implementation (GPT)
await mcp__zen__chat({
  model: "gpt-5",
  prompt: "Implement optimized audio buffering and streaming for VTuber TTS",
  files: ["tts/edgeTTS.py", "module/audio_manager.py"]
});
```

### 4.3 Development Decision Framework

#### When to Use Multi-Model Approach
- **Complex Architecture Decisions**: Use Gemini for system design
- **Performance-Critical Code**: Use GPT for optimization
- **Debugging & Analysis**: Use Claude for systematic problem solving
- **Integration Challenges**: Use all three in sequence

---

## Phase 5: Code Reuse & Quality Enhancement (Week 5)

### 5.1 VTuber Codebase Audit

#### Systematic Code Reuse Analysis
```bash
# Create code analysis scripts
mkdir scripts/code-analysis

# Audit for duplicate functionality
node scripts/code-analysis/find-duplicates.js

# Check for reusable patterns
node scripts/code-analysis/pattern-analysis.js

# Verify no "v2/new/old" naming
node scripts/code-analysis/naming-audit.js
```

#### Target Areas for Reuse Analysis
- [ ] **Audio processing functions** across TTS modules
- [ ] **WebSocket handling** in multiple files
- [ ] **Live2D model management** utilities
- [ ] **AWS integration** patterns
- [ ] **Error handling** implementations

### 5.2 File Organization Enhancement

#### Apply Claude Prompts File Rules
- [ ] **Remove any "v2", "new", "old" file naming**
- [ ] **Consolidate duplicate functionality**
- [ ] **Ensure files stay under 800 lines where practical**
- [ ] **Replace existing files instead of creating duplicates**

### 5.3 Enhanced Development Scripts

#### [`scripts/vtuber-dev-workflow.js`](scripts/vtuber-dev-workflow.js)
```javascript
// Comprehensive development workflow script
class VTuberDevWorkflow {
    async startDevelopmentSession() {
        // 1. Read memory bank
        await this.readMemoryBank();
        
        // 2. Check for existing functionality
        await this.auditExistingCode();
        
        // 3. Run diagnostic tests
        await this.runDiagnostics();
        
        // 4. Update memory bank with current context
        await this.updateMemoryBank();
    }
    
    async beforeCommit() {
        // Pre-commit quality checks
        await this.runCodeReuseScan();
        await this.runVTuberTests();
        await this.updateDocumentation();
    }
}
```

---

## Immediate Implementation Steps (This Week)

### Day 1-2: Memory Bank Setup
1. **Create memory bank directory structure**
2. **Document current VTuber system state**
3. **Add memory bank scripts to package.json**

### Day 3-4: Circuit Breaker Integration  
1. **Create VTuber debugging circuit breaker**
2. **Enhance existing diagnostic scripts**
3. **Document common VTuber debugging patterns**

### Day 5-7: Testing Foundation
1. **Setup Puppeteer for Electron testing**
2. **Create basic VTuber test scenarios**
3. **Implement automated test runner**

---

## Success Metrics & Validation

### Technical Metrics
- [ ] **Memory Bank Usage**: 100% of development sessions start with memory bank review
- [ ] **Debugging Efficiency**: 50% reduction in debugging time using circuit breaker methodology
- [ ] **Code Reuse Rate**: 80% reuse rate for new VTuber features
- [ ] **Test Coverage**: 90%+ automated test coverage for VTuber interactions

### Quality Metrics  
- [ ] **Bug Reduction**: 70% reduction in recurring VTuber issues
- [ ] **Development Speed**: 40% faster feature implementation
- [ ] **Documentation Quality**: All VTuber features have memory bank documentation
- [ ] **Multi-Model Integration**: Successful use of different AI models for different tasks

---

## Integration with Existing Plans

### Relationship to [`implementation-todo-list.md`](implementation-todo-list.md)
This plan **enhances** rather than replaces the existing implementation plan:

- **Phase 1-2**: Add VTuber-specific memory bank and debugging enhancements
- **Phase 3**: Integrate VTuber Puppeteer testing with existing test plans  
- **Phase 4**: Add multi-model workflows to existing AI integration
- **Phase 5-6**: Apply code reuse principles to existing quality assurance

### Relationship to [`aws-migration-plan.md`](aws-migration-plan.md)
- **Security Fixes**: Apply circuit breaker debugging to security vulnerability resolution
- **Testing Strategy**: Use Puppeteer testing for AWS integration validation
- **Documentation**: Use memory bank system for AWS migration context tracking

---

## Conclusion

This integration plan takes the proven methodologies from [`Claude_Prompts_RooCode`](Claude_Prompts_RooCode/) and adapts them specifically for the AWS VTuber LLM Desktop Assistant project. By building upon the excellent existing plans rather than replacing them, we create a comprehensive development workflow that:

- **Maintains Context** across development sessions with VTuber-specific memory bank
- **Prevents Debugging Loops** with systematic circuit breaker methodology  
- **Automates Validation** with VTuber desktop interaction testing
- **Optimizes AI Usage** with multi-model workflows for different tasks
- **Ensures Quality** with systematic code reuse and organization

The result is a more efficient, systematic, and reliable development process specifically tailored to the unique challenges of building a Live2D desktop VTuber assistant with AWS integration.