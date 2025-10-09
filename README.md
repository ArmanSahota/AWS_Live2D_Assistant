# AWS VTuber LLM Project

A sophisticated LLM-powered Live2D Desktop Assistant with AWS integration capabilities, featuring RAG (Retrieval-Augmented Generation) for enhanced manufacturing and technical support.

## 🚨 Security Notice

This project has been cleaned and organized with security best practices:
- **All sensitive AWS information has been removed**
- **Use `.env.example` as a template for your configuration**
- **Never commit actual credentials to version control**

## 📁 Project Structure

```
├── .env.example                        # Environment configuration template
├── .gitignore                          # Enhanced security rules
├── package.json                        # Root package configuration
├── package-lock.json                   # Package lock file
├── README.md                           # This file
│
├── archive/                            # Archived files (organized cleanup)
│   ├── duplicates/                     # Duplicate AWS setup guides
│   ├── old-docs/                       # Legacy documentation
│   ├── old-tests/                      # Archived test files
│   └── app-docs/                       # Application-specific docs
│
├── assets/                             # Audio and binary assets
│   ├── test_stt_recording.wav          # Sample STT recording
│   ├── test_tts_output.mp3             # Sample TTS output
│   └── 伊蕾娜_zh_wasm_v3_0_0.ppn        # Wake word model file
│
├── config/                             # Configuration files
├── docs/                               # Current documentation
│   ├── aws/                            # AWS-related documentation
│   ├── guides/                         # User guides and tutorials
│   ├── status/                         # Project status reports
│   └── troubleshooting/                # Troubleshooting guides
│
├── scripts/                            # Utility scripts
├── Claude_Prompts_RooCode/             # Claude prompts and code
└── LLM-Live2D-Desktop-Assitant-main/   # Main application
```

## 🎯 Main Application Features

The core application (`LLM-Live2D-Desktop-Assitant-main/`) includes:

- **🤖 AI Assistant**: Claude-powered conversational AI
- **🎭 Live2D Integration**: Animated character interface
- **🗣️ Speech Processing**: STT (Speech-to-Text) and TTS (Text-to-Speech)
- **🔍 RAG System**: AWS Knowledge Base integration for manufacturing support
- **🌐 Web Interface**: Browser-based interaction
- **🔧 Manufacturing Mode**: Specialized technical assistance

### Core Components:
- **src/**: Source code for the main application
- **static/**: Static assets including Live2D models and web resources
- **tests/**: Application-specific test suites
- **tts/**: Text-to-speech implementations
- **asr/**: Automatic speech recognition modules
- **translate/**: Translation services
- **utils/**: Utility functions and helpers

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your actual AWS credentials and configuration
# NEVER commit the .env file to version control
```

### 2. Install Dependencies
```bash
# Navigate to the main application
cd LLM-Live2D-Desktop-Assitant-main

# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configure AWS (Optional)
If using AWS RAG features:
- Set up AWS credentials in `.env`
- Configure Knowledge Base ID
- Ensure proper IAM permissions

### 4. Run the Application
```bash
# From the main application directory
python server.py

# Or use the provided scripts
../scripts/start_app.bat
```

## 📚 Documentation

- **Setup Guides**: See [`docs/guides/`](docs/guides/) for installation and configuration
- **AWS Integration**: See [`docs/aws/`](docs/aws/) for cloud deployment information
- **Troubleshooting**: See [`docs/troubleshooting/`](docs/troubleshooting/) for common issues and fixes
- **Project Status**: See [`docs/status/`](docs/status/) for current project status

## 🔒 Security Features

### Enhanced `.gitignore`
- AWS credentials and sensitive files
- Environment configuration files
- Debug and diagnostic outputs
- Temporary and backup files
- Large binary files

### Configuration Management
- Template-based configuration (`.env.example`)
- Sensitive data isolation
- No hardcoded credentials

## 🧪 Testing

Run tests using the scripts in the main application's `tests/` directory:

```bash
cd LLM-Live2D-Desktop-Assitant-main/tests
# Various test suites available for different components
```

## 🗂️ Archive Information

The `archive/` directory contains:
- **duplicates/**: Duplicate AWS setup guides (moved for cleanup)
- **old-docs/**: Legacy documentation files
- **old-tests/**: Archived test files from root level
- **app-docs/**: Application-specific documentation

These files are preserved for reference but are no longer part of the active project structure.

## 🛠️ Development

### Project Organization
- Clean separation of concerns
- Modular architecture
- Comprehensive testing
- Security-first approach

### Contributing Guidelines
1. Never commit sensitive information
2. Use environment variables for configuration
3. Follow the established project structure
4. Update documentation for significant changes

## 📋 Requirements

- **Python 3.8+**
- **Node.js 16+**
- **AWS Account** (optional, for RAG features)
- **Modern web browser** for the interface

## 🔧 Configuration

### Environment Variables
See `.env.example` for all available configuration options:
- AWS credentials and region
- Knowledge Base configuration
- Application settings
- Debug options

### AWS Setup (Optional)
For RAG functionality:
1. Set up AWS Bedrock access
2. Create Knowledge Base
3. Configure OpenSearch Serverless
4. Set appropriate IAM permissions

## 📞 Support

- Check [`docs/troubleshooting/`](docs/troubleshooting/) for common issues
- Review archived documentation in `archive/` if needed
- Ensure environment variables are properly configured

---

**⚠️ Security Reminder**: This project has been cleaned of sensitive information. Always use environment variables for credentials and never commit sensitive data to version control.