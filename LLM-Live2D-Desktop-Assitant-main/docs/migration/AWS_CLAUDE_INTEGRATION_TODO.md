# AWS Bedrock Claude Integration TODO List

## Phase 0 — Repo Audit (COMPLETED)
- [x] Locate current TTS/STT integration points
- [x] Identify chat pipeline and network layer
- [x] Find best places for configuration and IPC wiring
- [x] Assess status UI and settings components
- [x] Document risks and unknowns

## Phase 1 — Speech Component Fixes (COMPLETED)

- [x] **Investigate Audio Pipeline Issues**
  - [x] Analyze current audio flow between Python TTS engines and JS frontend
  - [x] Document audio flow and potential issues
  - [x] Created comprehensive audio_pipeline_analysis.md

- [x] **Fix Local TTS Integration**
  - [x] Create ttsBridge.ts wrapper around local TTS with error handling
  - [x] Add proper error fallbacks and diagnostics
  - [x] **Acceptance**: TTS can be called from TypeScript and properly plays audio

- [x] **Fix Local STT Integration**
  - [x] Create sttBridge.ts wrapper around local STT
  - [x] Add error handling for STT failures
  - [x] **Acceptance**: STT correctly transcribes speech and delivers text to application

- [x] **Update Audio Component Initialization**
  - [x] Add safety checks and proper handling for window.model2
  - [x] Enhance error handling for audio failures
  - [x] **Acceptance**: Audio components initialize properly and handle errors gracefully

## Phase 2 — Config & Settings (IN PROGRESS)

- [x] **src/types/http.ts**
  - [x] Add authentication header types
  - [x] Add AWS config type
  - [x] Extend ClaudeRequest/Response types

- [ ] **src/config/appConfig.ts**
  - [ ] Add defaultHttpBase and httpTimeout fields
  - [ ] Ensure electron-store persists HTTP settings
  - [ ] Add speech-related configuration options
  - [ ] **Acceptance**: Config loads from ENV, defaults to empty, persists changes

- [ ] **src/app/settings/SettingsPanel.tsx**
  - [ ] Add HTTP base URL field with validation
  - [ ] Add toggle switches for feature flags
  - [ ] Add speech sensitivity and device selection UI
  - [ ] **Acceptance**: Settings panel saves/loads HTTP base URL, feature flags, and speech settings correctly

## Phase 3 — HTTP Client (Main Process) + IPC (IN PROGRESS)

- [x] **src/main/claudeClient.ts**
  - [x] Implement askClaude with error handling
  - [x] Add optional Authorization header if token exists
  - [x] Add request/response logging (no PII)
  - [x] **Acceptance**: askClaude sends properly formatted requests and handles responses/errors

- [x] **src/main/ipc.ts**
  - [x] Enhance claude:ask handler with better error handling
  - [x] Add generateSpeech handler
  - [x] Add handlers for speech operations
  - [x] **Acceptance**: IPC handlers correctly proxy requests between renderer and main

- [ ] **src/infra/http/api.ts**
  - [ ] Add Claude-specific API call function
  - [ ] Implement proper error handling and timeout
  - [ ] **Acceptance**: API correctly formats requests to Claude endpoint

## Phase 4 — Renderer Chat Path (HTTP) (IN PROGRESS)

- [x] **src/app/chat/httpPath.ts**
  - [x] Implement sendUserTextHTTP with proper UI updates
  - [x] Handle loading states and errors
  - [x] Connect to TTS for spoken replies
  - [x] **Acceptance**: Complete round-trip conversation works via HTTP

- [x] **static/desktop/preload.js**
  - [x] Add window.api.askClaude method
  - [x] Add window.api.getHealth method
  - [x] Add window.api.generateSpeech method
  - [x] Expose speech control methods
  - [x] **Acceptance**: Renderer can access all needed IPC methods

- [ ] **static/desktop/websocket.js**
  - [ ] Make websocket operations optional
  - [ ] Add graceful fallbacks to HTTP
  - [ ] Ensure state transitions work with both HTTP and WS
  - [ ] **Acceptance**: Frontend can work with both HTTP and WS backends

## Phase 5 — Speech Wrappers (COMPLETED)

- [x] **src/app/speech/ttsBridge.ts**
  - [x] Create robust wrapper around local TTS
  - [x] Ensure proper audio format handling
  - [x] Add metrics and diagnostics
  - [x] **Acceptance**: TTS speaks Claude replies from HTTP path

- [x] **src/app/speech/sttBridge.ts**
  - [x] Create robust wrapper around local STT
  - [x] Add speech detection status indicators
  - [x] Implement automatic timeout and reset
  - [x] **Acceptance**: STT captures user speech and feeds to HTTP path

- [ ] **static/desktop/vad.js**
  - [ ] Update speech probability threshold handling
  - [ ] Fix microphone selection and initialization
  - [ ] Improve error handling for speech detection
  - [ ] **Acceptance**: VAD correctly detects speech and triggers STT

## Phase 6 — Status & Observability

- [ ] **src/app/components/StatusBar.tsx**
  - [ ] Add cloud health indicator
  - [ ] Add feature flag indicators
  - [ ] Add speech system status indicators
  - [ ] **Acceptance**: Status bar shows accurate system state

- [ ] **src/main/healthCheck.ts**
  - [ ] Implement periodic health checks (60s)
  - [ ] Add speech system health checks
  - [ ] Publish status updates via IPC
  - [ ] **Acceptance**: App knows cloud health status at all times

- [ ] **src/app/utils/logger.ts**
  - [ ] Implement request/response timing logging
  - [ ] Add speech operation logging
  - [ ] Surface logs in developer console
  - [ ] **Acceptance**: All operations are logged with timing information

## Phase 7 — WebSocket (Future Prep)

- [ ] **src/infra/ws/wsClient.ts**
  - [ ] Ensure it can be toggled on/off
  - [ ] Create clean interface for future streaming
  - [ ] **Acceptance**: WS code doesn't interfere with HTTP path but remains functional

- [ ] **src/app/chat/wsPath.ts**
  - [ ] Move WebSocket-specific chat logic here
  - [ ] Make it toggleable via config
  - [ ] **Acceptance**: WebSocket chat path can be enabled/disabled without affecting HTTP

## Phase 8 — Security & Future Work (Placeholders)

- [ ] **docs/future-auth.md**
  - [ ] Document Cognito Hosted UI integration plan
  - [ ] Document Lambda Authorizer approach
  - [ ] Document JWT handling for HTTP

- [ ] **docs/future-rag.md**
  - [ ] Document S3 upload workflow
  - [ ] Document vector store options
  - [ ] Document /rag/query endpoint plans

- [ ] **docs/security-checklist.md**
  - [ ] Document IAM hardening for Bedrock
  - [ ] Document WAF/rate limiting plans
  - [ ] Document request body limits

## Definition of Done for MVP

1. GET /health works from app Settings panel and reports status
2. POST /claude accepts text input and returns a reply
3. Claude's reply is spoken using local TTS with audio clearly audible
4. Local STT correctly transcribes user speech and sends it to Claude
5. Errors (network, auth, validation, speech) are handled gracefully with user-friendly messages
6. No secrets are stored in client code; all config is via environment variables or persisted settings
7. TypeScript build is clean with no type errors
8. No CORS issues (all requests go through main process)
9. Settings are persisted across app restarts
10. App can function when offline (with appropriate error handling)
11. WebSocket code remains but is not required for Claude functionality
