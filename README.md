# AWS VTuber LLM Project

This project contains an LLM-powered Live2D Desktop Assistant with AWS integration capabilities.

## Project Structure

```
├── .gitignore                          # Git ignore rules
├── package.json                        # Root package configuration
├── package-lock.json                   # Package lock file
├── README.md                           # This file
│
├── assets/                             # Audio and binary assets
│   ├── test_stt_recording.wav          # Sample STT recording
│   ├── test_tts_output.mp3             # Sample TTS output
│   └── 伊蕾娜_zh_wasm_v3_0_0.ppn        # Wake word model file
│
├── config/                             # Configuration files
│
├── docs/                               # Documentation
│   ├── aws/                            # AWS-related documentation
│   │   ├── AWS_BEDROCK_OPUS_FIX.md     # AWS Bedrock Opus fixes
│   │   ├── aws-hybrid-poc-guide.md     # Hybrid POC guide
│   │   ├── aws-migration-plan.md       # Migration planning
│   │   └── OPUS_SETUP_GUIDE.md         # Opus setup instructions
│   │
│   ├── guides/                         # User guides and tutorials
│   │   ├── FRONTEND_BACKEND_CONNECTION_GUIDE.md
│   │   ├── quick-fix-guide.md
│   │   ├── TESTING_GUIDE.md
│   │   └── WAKE_WORD_SETUP_GUIDE.md
│   │
│   ├── plans/                          # Project planning documents
│   │   ├── claude-prompts-integration-plan.md
│   │   ├── claude-prompts-integration-todo.md
│   │   ├── claude-prompts-workflow-diagram.md
│   │   ├── comprehensive-development-workflow-plan.md
│   │   ├── object-recognition-implementation-roadmap.md
│   │   ├── object-recognition-vision-plan.md
│   │   ├── vision-architecture-diagram.md
│   │   ├── vision-implementation-todo.md
│   │   ├── vtuber-free-roam-feature.md
│   │   └── vtuber-vision-integration-plan.md
│   │
│   ├── status/                         # Project status reports
│   │   ├── FINAL_PIPELINE_STATUS.md
│   │   ├── FINAL_STATUS_REPORT.md
│   │   ├── implementation-todo-list.md
│   │   └── NEXT_STEPS_EXECUTION.md
│   │
│   └── troubleshooting/                # Troubleshooting guides
│       ├── PIPELINE_INTEGRATION_FIXES.md
│       ├── PIPELINE_TEST_RESULTS.md
│       ├── TEST_RESULTS_REPORT.md
│       ├── websocket-audio-fix-plan.md
│       └── websocket-fix-todo.md
│
├── scripts/                            # Utility scripts
│   ├── fix_frontend_backend_connection.bat
│   ├── fix_ipc_tts.py
│   ├── start_app.bat
│   ├── test_claude_aws.bat
│   └── test_websocket_connection_root.bat
│
├── tests/                              # Test files
│   ├── test_claude_opus.py
│   ├── test_connection_diagnostic.js
│   ├── test_connection.js
│   ├── test_stt.py
│   └── test_tts.py
│
├── .roo/                               # Roo configuration
├── Claude_Prompts_RooCode/             # Claude prompts and code
└── LLM-Live2D-Desktop-Assitant-main/   # Main application
```

## Main Application

The core application is located in `LLM-Live2D-Desktop-Assitant-main/` and contains:

- **src/**: Source code for the main application
- **static/**: Static assets including Live2D models and web resources
- **tests/**: Application-specific test suites
- **tts/**: Text-to-speech implementations
- **asr/**: Automatic speech recognition modules
- **translate/**: Translation services
- **utils/**: Utility functions and helpers

## Quick Start

1. Navigate to the main application directory:
   ```bash
   cd LLM-Live2D-Desktop-Assitant-main
   ```

2. Install dependencies:
   ```bash
   npm install
   pip install -r requirements.txt
   ```

3. Configure your environment (see docs/guides/ for setup instructions)

4. Run the application:
   ```bash
   # Use the provided script
   ../scripts/start_app.bat
   
   # Or run directly
   python server.py
   ```

## Documentation

- **Setup Guides**: See `docs/guides/` for installation and configuration
- **AWS Integration**: See `docs/aws/` for cloud deployment information
- **Troubleshooting**: See `docs/troubleshooting/` for common issues and fixes
- **Project Planning**: See `docs/plans/` for roadmaps and feature planning
- **Status Reports**: See `docs/status/` for current project status

## Testing

Run tests using the scripts in the `tests/` directory or use the provided batch files in `scripts/`.

## Contributing

Please refer to the documentation in `docs/` for development guidelines and project structure information.