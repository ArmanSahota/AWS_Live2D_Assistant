# Claude Prompts Integration - Actionable Todo List

## 🎯 Immediate Actions (This Week)

### Day 1: Memory Bank Foundation
- [ ] **Create memory bank directory structure**
  ```bash
  mkdir memory-bank
  mkdir memory-bank/features
  mkdir memory-bank/debugging-sessions
  mkdir memory-bank/testing-results
  ```

- [ ] **Create core memory files**
  - [ ] [`memory-bank/projectbrief.md`](memory-bank/projectbrief.md) - VTuber project mission and success criteria
  - [ ] [`memory-bank/activeContext.md`](memory-bank/activeContext.md) - Current development focus and recent achievements
  - [ ] [`memory-bank/systemPatterns.md`](memory-bank/systemPatterns.md) - VTuber architecture patterns and communication flow
  - [ ] [`memory-bank/techContext.md`](memory-bank/techContext.md) - Technology stack and configuration details
  - [ ] [`memory-bank/progress.md`](memory-bank/progress.md) - Current status and known issues

### Day 2: VTuber-Specific Memory Documentation
- [ ] **Document current VTuber system state**
  - [ ] [`memory-bank/features/live2d-desktop-integration.md`](memory-bank/features/live2d-desktop-integration.md)
  - [ ] [`memory-bank/features/aws-claude-integration.md`](memory-bank/features/aws-claude-integration.md)
  - [ ] [`memory-bank/features/audio-pipeline-whisper-edge.md`](memory-bank/features/audio-pipeline-whisper-edge.md)
  - [ ] [`memory-bank/features/electron-desktop-app.md`](memory-bank/features/electron-desktop-app.md)

- [ ] **Add memory bank scripts to package.json**
  ```json
  {
    "scripts": {
      "memory:read": "node scripts/read-memory-bank.js",
      "memory:update": "node scripts/update-memory-bank.js",
      "dev:with-memory": "npm run memory:read && npm start"
    }
  }
  ```

### Day 3: Circuit Breaker Debugging Setup
- [ ] **Create VTuber debugging utilities**
  - [ ] [`utils/vtuber_debugging_circuit_breaker.py`](utils/vtuber_debugging_circuit_breaker.py)
  - [ ] [`scripts/vtuber-debug-assistant.js`](scripts/vtuber-debug-assistant.js)

- [ ] **Enhance existing diagnostic scripts**
  - [ ] Update [`LLM-Live2D-Desktop-Assitant-main/static/desktop/diagnostics.js`](LLM-Live2D-Desktop-Assitant-main/static/desktop/diagnostics.js) with circuit breaker
  - [ ] Add systematic debugging to [`LLM-Live2D-Desktop-Assitant-main/tests/speech-pipeline-test.js`](LLM-Live2D-Desktop-Assitant-main/tests/speech-pipeline-test.js)

- [ ] **Create debugging session templates**
  - [ ] [`memory-bank/debugging-sessions/template.md`](memory-bank/debugging-sessions/template.md)
  - [ ] [`memory-bank/debugging-sessions/common-vtuber-issues.md`](memory-bank/debugging-sessions/common-vtuber-issues.md)

### Day 4-5: Basic Puppeteer Testing Setup
- [ ] **Install and configure Puppeteer for Electron testing**
  ```bash
  npm install --save-dev puppeteer
  ```

- [ ] **Create basic VTuber test scenarios**
  - [ ] [`tests/puppeteer/vtuber-basic-tests.js`](tests/puppeteer/vtuber-basic-tests.js)
  - [ ] [`tests/puppeteer/live2d-rendering-test.js`](tests/puppeteer/live2d-rendering-test.js)
  - [ ] [`tests/puppeteer/desktop-interaction-test.js`](tests/puppeteer/desktop-interaction-test.js)

- [ ] **Add Puppeteer test scripts to package.json**
  ```json
  {
    "scripts": {
      "test:vtuber-basic": "node tests/puppeteer/vtuber-basic-tests.js",
      "test:live2d": "node tests/puppeteer/live2d-rendering-test.js"
    }
  }
  ```

### Day 6-7: Multi-Model Workflow Foundation
- [ ] **Create multi-model development scripts**
  - [ ] [`scripts/ai-architecture-review.js`](scripts/ai-architecture-review.js) - Gemini for system design
  - [ ] [`scripts/ai-code-implementation.js`](scripts/ai-code-implementation.js) - GPT for implementation
  - [ ] [`scripts/ai-debugging-assistant.js`](scripts/ai-debugging-assistant.js) - Claude for analysis

- [ ] **Document model selection guidelines**
  - [ ] [`memory-bank/multi-model-workflows.md`](memory-bank/multi-model-workflows.md)

---

## 🚀 Week 2: Enhanced Debugging & Testing

### VTuber Circuit Breaker Implementation
- [ ] **Implement VTuber-specific debugging patterns**
  - [ ] Live2D model loading issues
  - [ ] Audio sync problems  
  - [ ] AWS connection failures
  - [ ] WebSocket disconnects
  - [ ] TTS audio issues

- [ ] **Create debugging workflow integration**
  - [ ] Add circuit breaker to existing Python diagnostic scripts
  - [ ] Enhance JavaScript error handling with systematic debugging
  - [ ] Create debugging session documentation workflow

### Puppeteer VTuber Testing Expansion
- [ ] **Advanced VTuber test scenarios**
  - [ ] [`tests/puppeteer/audio-pipeline-test.js`](tests/puppeteer/audio-pipeline-test.js)
  - [ ] [`tests/puppeteer/aws-integration-test.js`](tests/puppeteer/aws-integration-test.js)
  - [ ] [`tests/puppeteer/electron-app-test.js`](tests/puppeteer/electron-app-test.js)

- [ ] **Desktop-specific testing**
  - [ ] Drag functionality testing
  - [ ] System tray integration testing
  - [ ] Always-on-top behavior testing
  - [ ] Performance metrics monitoring

---

## 📊 Week 3: Code Quality & Reuse Analysis

### Systematic Code Audit
- [ ] **Create code analysis utilities**
  - [ ] [`scripts/code-analysis/find-duplicates.js`](scripts/code-analysis/find-duplicates.js)
  - [ ] [`scripts/code-analysis/pattern-analysis.js`](scripts/code-analysis/pattern-analysis.js)
  - [ ] [`scripts/code-analysis/naming-audit.js`](scripts/code-analysis/naming-audit.js)

- [ ] **Audit VTuber codebase for reuse opportunities**
  - [ ] Audio processing functions across TTS modules
  - [ ] WebSocket handling in multiple files
  - [ ] Live2D model management utilities
  - [ ] AWS integration patterns
  - [ ] Error handling implementations

### File Organization Enhancement
- [ ] **Apply Claude Prompts file rules**
  - [ ] Remove any "v2", "new", "old" file naming
  - [ ] Consolidate duplicate functionality
  - [ ] Ensure files stay under 800 lines where practical
  - [ ] Replace existing files instead of creating duplicates

---

## 🔄 Week 4: Full Integration & Optimization

### Complete Multi-Model Workflow
- [ ] **Implement model-specific development workflows**
  - [ ] Gemini for Live2D architecture design
  - [ ] GPT for audio pipeline optimization
  - [ ] Claude for AWS integration analysis

- [ ] **Create development decision framework**
  - [ ] When to use which AI model
  - [ ] Multi-model consultation patterns
  - [ ] Workflow automation scripts

### Comprehensive Testing Suite
- [ ] **Full VTuber Puppeteer test suite**
  - [ ] End-to-end user interaction flows
  - [ ] Performance benchmarking
  - [ ] Error scenario testing
  - [ ] AWS integration validation

- [ ] **Automated quality assurance**
  - [ ] Pre-commit hooks with memory bank updates
  - [ ] Continuous testing integration
  - [ ] Code quality metrics tracking

---

## 📋 Quality Checklist (Before Each Development Session)

### Memory Bank Workflow
- [ ] **Read ALL memory bank files** at session start
- [ ] **Update activeContext.md** with current focus
- [ ] **Document any new patterns** in systemPatterns.md
- [ ] **Update progress.md** with status changes

### Circuit Breaker Debugging
- [ ] **Check for existing similar functionality** before creating new code
- [ ] **Apply three-strike rule** if debugging issues
- [ ] **Document debugging attempts** in debugging-sessions/
- [ ] **Escalate to multi-model analysis** if stuck

### Testing & Validation
- [ ] **Run VTuber Puppeteer tests** after changes
- [ ] **Verify Live2D rendering** still works
- [ ] **Test audio pipeline** functionality
- [ ] **Validate AWS integration** endpoints

### Code Quality
- [ ] **No "v2/new/old" file naming**
- [ ] **Check for code reuse opportunities**
- [ ] **Update documentation** for changes
- [ ] **Verify file size limits** (800 lines)

---

## 🎯 Success Metrics

### Week 1 Goals
- [ ] Memory bank system operational
- [ ] Basic circuit breaker debugging implemented
- [ ] Initial Puppeteer tests running
- [ ] Multi-model workflow foundation established

### Week 2 Goals  
- [ ] VTuber-specific debugging patterns documented
- [ ] Advanced Puppeteer testing scenarios working
- [ ] Debugging efficiency improvements measurable

### Week 3 Goals
- [ ] Code reuse analysis completed
- [ ] File organization enhanced
- [ ] Quality metrics baseline established

### Week 4 Goals
- [ ] Full integration operational
- [ ] All workflows automated
- [ ] Performance improvements documented
- [ ] Development efficiency gains measured

---

## 🔗 Integration Points

### With Existing Plans
- **Enhances** [`implementation-todo-list.md`](implementation-todo-list.md) Phases 1-4
- **Supports** [`aws-migration-plan.md`](aws-migration-plan.md) testing and documentation
- **Builds on** [`FINAL_STATUS_REPORT.md`](FINAL_STATUS_REPORT.md) operational system

### With Current Codebase
- **Enhances** existing diagnostic scripts
- **Improves** current testing approaches  
- **Systematizes** debugging workflows
- **Optimizes** development processes

---

## 🚀 Getting Started

### Immediate Next Steps
1. **Create memory bank directory structure** (5 minutes)
2. **Document current VTuber system state** (30 minutes)
3. **Add memory bank scripts to package.json** (10 minutes)
4. **Start using memory bank workflow** (immediate)

### This Week's Priority
Focus on **Phase 1: Memory Bank Foundation** - this provides immediate value and sets up all subsequent improvements.

The memory bank system will provide context continuity across development sessions, which is the foundation for all other Claude Prompts best practices.