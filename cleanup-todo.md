# Directory Cleanup Todo List

## Phase 1: Create Documentation Structure ✅ Ready to Execute

### 1.1 Create Documentation Directories
- [ ] Create `LLM-Live2D-Desktop-Assitant-main/docs/` directory
- [ ] Create `LLM-Live2D-Desktop-Assitant-main/docs/architecture/` 
- [ ] Create `LLM-Live2D-Desktop-Assitant-main/docs/fixes/`
- [ ] Create `LLM-Live2D-Desktop-Assitant-main/docs/migration/`
- [ ] Create `LLM-Live2D-Desktop-Assitant-main/docs/troubleshooting/`
- [ ] Create `LLM-Live2D-Desktop-Assitant-main/docs/live2d/`

### 1.2 Move Architecture & Design Documentation
- [ ] Move `ARCHITECTURE_DIAGRAM.md` → `docs/architecture/`
- [ ] Move `IMPLEMENTATION_TODO.md` → `docs/architecture/`
- [ ] Move `REACT_VITE_MIGRATION_PLAN.md` → `docs/architecture/`

### 1.3 Move Live2D Documentation
- [ ] Move `live2d-debug-tool.md` → `docs/live2d/`
- [ ] Move `live2d-implementation-summary.md` → `docs/live2d/`
- [ ] Move `live2d-minimal-implementation.md` → `docs/live2d/`
- [ ] Move `live2d-refactoring-guide.md` → `docs/live2d/`
- [ ] Move `live2d-testing-guide.md` → `docs/live2d/`
- [ ] Move `live2d-troubleshooting-guide.md` → `docs/live2d/`

### 1.4 Move Fix & Diagnostic Documentation
- [ ] Move `ASR_FIX_DOCUMENTATION.md` → `docs/fixes/`
- [ ] Move `AUDIO_FIX_README.md` → `docs/fixes/`
- [ ] Move `AUDIO_SUBTITLE_FIX.md` → `docs/fixes/`
- [ ] Move `AUDIO_WAKE_WORD_FIX_README.md` → `docs/fixes/`
- [ ] Move `CLAUDE_CONVERSATION_VALIDATION_FIX.md` → `docs/fixes/`
- [ ] Move `CLAUDE_VISION_VALIDATION_ERROR_FIX.md` → `docs/fixes/`
- [ ] Move `CODING_MISTAKES_FIXES.md` → `docs/fixes/`
- [ ] Move `COMPLETE_CODING_MISTAKES_REPORT.md` → `docs/fixes/`
- [ ] Move `CONFIG_FIX_README.md` → `docs/fixes/`
- [ ] Move `CONNECTION_FIX_GUIDE.md` → `docs/fixes/`
- [ ] Move `CONNECTION_FIXES_APPLIED.md` → `docs/fixes/`
- [ ] Move `CONTEXT_MENU_AND_PORT_FIXES.md` → `docs/fixes/`
- [ ] Move `CRITICAL_FIXES_APPLIED.md` → `docs/fixes/`
- [ ] Move `DEBUG_FIXES_APPLIED.md` → `docs/fixes/`
- [ ] Move `ELECTRON_STARTUP_FIX.md` → `docs/fixes/`
- [ ] Move `FIXES_README.md` → `docs/fixes/`
- [ ] Move `GAMING_CONTROLLER_BIAS_DIAGNOSTIC_APPLIED.md` → `docs/fixes/`
- [ ] Move `MIC_LOOP_FIX_APPLIED.md` → `docs/fixes/`
- [ ] Move `MIC_START_STOP_LOOP_DIAGNOSIS.md` → `docs/fixes/`
- [ ] Move `SPEECH_PIPELINE_FIXES.md` → `docs/fixes/`
- [ ] Move `STT_FIX_SUMMARY.md` → `docs/fixes/`
- [ ] Move `SUBTITLE_DIAGNOSTIC_REPORT.md` → `docs/fixes/`
- [ ] Move `SUBTITLE_FIX_DOCUMENTATION.md` → `docs/fixes/`
- [ ] Move `VISION_*_FIX*.md` files → `docs/fixes/`
- [ ] Move `WEBSOCKET_*_FIX*.md` files → `docs/fixes/`

### 1.5 Move Migration Documentation
- [ ] Move `AWS_CLAUDE_INTEGRATION_TODO.md` → `docs/migration/`
- [ ] Move `AWS_CLAUDE_SETUP.md` → `docs/migration/`
- [ ] Move `AWS_LAMBDA_VISION_UPDATE_GUIDE.md` → `docs/migration/`
- [ ] Move `AWS_MIGRATION_SUMMARY.md` → `docs/migration/`
- [ ] Move `CLAUDE_3.7_UPGRADE_SUMMARY.md` → `docs/migration/`
- [ ] Move `FINAL_MIGRATION_STATUS.md` → `docs/migration/`
- [ ] Move `MIGRATION_COMPLETE_SUCCESS.md` → `docs/migration/`
- [ ] Move `MIGRATION_COMPLETE.md` → `docs/migration/`
- [ ] Move `MIGRATION_SUCCESS_REPORT.md` → `docs/migration/`
- [ ] Move `PHASE*_COMPLETION_SUMMARY.md` → `docs/migration/`
- [ ] Move `PHASE2_SETUP_GUIDE.md` → `docs/migration/`

### 1.6 Move Troubleshooting Documentation
- [ ] Move `DEBUG_README.md` → `docs/troubleshooting/`
- [ ] Move `STT_DIAGNOSTIC_TESTING_GUIDE.md` → `docs/troubleshooting/`
- [ ] Move `TROUBLESHOOTING_GUIDE.md` → `docs/troubleshooting/`
- [ ] Move `vision_debug_instructions.md` → `docs/troubleshooting/`

### 1.7 Move Status & Summary Documentation
- [ ] Move `CURRENT_STATUS_AND_NEXT_STEPS.md` → `docs/`
- [ ] Move `FINAL_FIX_SUMMARY.md` → `docs/`
- [ ] Move `how-to-apply-fix.md` → `docs/`
- [ ] Move `immediate-model-fix.md` → `docs/`
- [ ] Move `IMMEDIATE_VISION_FIX_REQUIRED.md` → `docs/`
- [ ] Move `RESTART_INSTRUCTIONS.md` → `docs/`

## Phase 2: Organize Test Files ✅ Ready to Execute

### 2.1 Create Test Directory Structure
- [ ] Create `LLM-Live2D-Desktop-Assitant-main/tests/unit/`
- [ ] Create `LLM-Live2D-Desktop-Assitant-main/tests/integration/`
- [ ] Create `LLM-Live2D-Desktop-Assitant-main/tests/diagnostics/`
- [ ] Create `LLM-Live2D-Desktop-Assitant-main/tests/vision/`
- [ ] Create `LLM-Live2D-Desktop-Assitant-main/tests/audio/`
- [ ] Create `LLM-Live2D-Desktop-Assitant-main/tests/claude/`
- [ ] Create `LLM-Live2D-Desktop-Assitant-main/tests/websocket/`
- [ ] Create `LLM-Live2D-Desktop-Assitant-main/tests/live2d/`

### 2.2 Move Audio/ASR Test Files
- [ ] Move `test_asr_fix.py` → `tests/audio/`
- [ ] Move `test_audio_playback.py` → `tests/audio/`
- [ ] Move `test-audio-playback.html` → `tests/audio/`
- [ ] Move `stt_diagnostic_patch.py` → `tests/diagnostics/`
- [ ] Move `test_stt_direct.py` → `tests/audio/`

### 2.3 Move Claude API Test Files
- [ ] Move `test_claude_aws_streaming.py` → `tests/claude/`
- [ ] Move `test_claude_aws.py` → `tests/claude/`
- [ ] Move `claude_conversation_diagnostic.py` → `tests/diagnostics/`
- [ ] Move `claude_message_structure_fix.py` → `tests/diagnostics/`
- [ ] Move `claude_vision_api_fix.py` → `tests/diagnostics/`
- [ ] Move `claude_vision_payload_diagnostic.py` → `tests/diagnostics/`
- [ ] Move `test_claude_vision_diagnostic.py` → `tests/claude/`
- [ ] Move `test_claude_vision_integration.py` → `tests/claude/`
- [ ] Move `test_conversation_validation_fix.py` → `tests/claude/`

### 2.4 Move Vision System Test Files
- [ ] Move `test_hybrid_vision_system.py` → `tests/vision/`
- [ ] Move `test_improved_vision.py` → `tests/vision/`
- [ ] Move `test_vision_analysis_fix.py` → `tests/vision/`
- [ ] Move `test_vision_fix_validation.py` → `tests/vision/`
- [ ] Move `test_vision_http_api.py` → `tests/vision/`
- [ ] Move `test_vision_message_type_fix.py` → `tests/vision/`
- [ ] Move `test_vision_standalone.py` → `tests/vision/`
- [ ] Move `test_vision_system.py` → `tests/vision/`
- [ ] Move `test_vision_with_photos.py` → `tests/vision/`
- [ ] Move `test_vision_with_real_endpoint.py` → `tests/vision/`
- [ ] Move `vision_analysis_diagnostic.py` → `tests/diagnostics/`
- [ ] Move `vision_analysis_timeout_diagnostic.py` → `tests/diagnostics/`
- [ ] Move `vision_analysis_timeout_fix.py` → `tests/diagnostics/`
- [ ] Move `vision_bias_diagnostic.py` → `tests/diagnostics/`
- [ ] Move `vision_image_data_diagnostic.py` → `tests/diagnostics/`
- [ ] Move `vision_tts_diagnostic.py` → `tests/diagnostics/`
- [ ] Move `vision_tts_integration_fix.py` → `tests/diagnostics/`

### 2.5 Move WebSocket Test Files
- [ ] Move `test_websocket_audio.py` → `tests/websocket/`
- [ ] Move `test_websocket_connection.bat` → `tests/websocket/`
- [ ] Move `test_ws.js` → `tests/websocket/`
- [ ] Move `websocket_transmission_diagnostic.py` → `tests/diagnostics/`

### 2.6 Move HTTP/Connection Test Files
- [ ] Move `test_connection_fix.js` → `tests/integration/`
- [ ] Move `test_connection_live.js` → `tests/integration/`
- [ ] Move `test_http_direct.js` → `tests/integration/`
- [ ] Move `test_http.js` → `tests/integration/`

### 2.7 Move Configuration Test Files
- [ ] Move `test_config_loading.py` → `tests/unit/`
- [ ] Move `test_electron_config.js` → `tests/unit/`

### 2.8 Move Live2D Test Files
- [ ] Move `test_live2d.js` → `tests/live2d/`
- [ ] Move `test-mic-loop-fix.js` → `tests/live2d/`

### 2.9 Move Integration Test Files
- [ ] Move `test_fixes.py` → `tests/integration/`
- [ ] Move `test_integrated_pipeline.py` → `tests/integration/`
- [ ] Move `test_pipeline_node.js` → `tests/integration/`
- [ ] Move `test_with_mock_endpoint.py` → `tests/integration/`

### 2.10 Move Diagnostic Scripts
- [ ] Move `debug_audio_conversation.py` → `tests/diagnostics/`
- [ ] Move `diagnose_connection.py` → `tests/diagnostics/`
- [ ] Move `diagnostic_validation.js` → `tests/diagnostics/`
- [ ] Move `fix_audio_conversation_issues.py` → `tests/diagnostics/`
- [ ] Move `config_vision_fix.py` → `tests/diagnostics/`

### 2.11 Move Batch Files
- [ ] Move `test-subtitles.bat` → `tests/audio/`

## Phase 3: Remove Unnecessary Files ⚠️ Requires Careful Review

### 3.1 Identify Obsolete Files (Review Before Deletion)
- [ ] Review `*_COMPLETE.md` files for archival
- [ ] Review duplicate diagnostic files
- [ ] Review old phase completion summaries
- [ ] Review temporary debug scripts

### 3.2 Archive Important Historical Information
- [ ] Create `docs/archive/` directory
- [ ] Move important historical files to archive
- [ ] Create summary document of archived information

### 3.3 Safe Deletion Candidates (After Review)
- [ ] `FINAL_PS5_CONTROLLER_FIX_SUMMARY.md` (if no longer relevant)
- [ ] Duplicate diagnostic files
- [ ] Old temporary fix files
- [ ] Redundant completion reports

## Phase 4: Clean Root Directory ✅ Final Step

### 4.1 Verify Essential Files Remain
- [ ] Keep `main.py`, `main.js`
- [ ] Keep `package.json`, `requirements.txt`
- [ ] Keep `README.md`, `README.CN.md`
- [ ] Keep `.env*`, `.git*` files
- [ ] Keep `dockerfile`, `tsconfig.json`
- [ ] Keep essential startup scripts

### 4.2 Update Documentation References
- [ ] Update any hardcoded paths in documentation
- [ ] Update README files with new structure
- [ ] Update test runner configurations

### 4.3 Final Verification
- [ ] Test application startup
- [ ] Verify test suites run correctly
- [ ] Check all documentation links work
- [ ] Confirm no broken functionality

## Success Metrics
- [ ] Root directory contains <20 files
- [ ] All documentation organized logically
- [ ] All tests consolidated and categorized
- [ ] No broken functionality
- [ ] Clear project navigation

## Rollback Plan
- [ ] Keep backup of original structure
- [ ] Document all moves for potential reversal
- [ ] Test incrementally to catch issues early