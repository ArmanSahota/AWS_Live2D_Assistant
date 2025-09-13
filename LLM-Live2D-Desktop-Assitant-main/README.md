# LLM Live2D Desktop Assistant

A desktop AI assistant with a Live2D VTuber interface powered by AWS Claude, designed to be at your service.

## Overview

LLM Live2D Desktop Assistant combines the power of AWS Claude's language capabilities with a visually engaging Live2D avatar to create an interactive desktop assistant. The application runs as an always-available desktop companion that can assist with various tasks through natural voice or text interaction.

![Desktop Assistant Screenshot]

## Key Features

- **Interactive Live2D Avatar**: Visual representation of your AI assistant with facial expressions and animations
- **Natural Voice Interaction**: Speak naturally with your assistant using local speech recognition and text-to-speech
- **AWS Claude Integration**: Powered by Claude via AWS Bedrock for intelligent, context-aware responses
- **Service-Oriented Persona**: Professional, helpful assistant designed to be at your service
- **Desktop Integration**: Access clipboard content and screen information to provide contextual assistance
- **Wake Word Detection**: Activate your assistant with a customizable wake word
- **Singing Capability**: Ask your assistant to sing songs from its repertoire
- **Hybrid Architecture**: Local processing for privacy with cloud-based intelligence

## Architecture

The application uses a hybrid architecture that combines local processing with cloud-based intelligence:

- **Frontend**: Electron-based desktop application with Live2D rendering
- **Backend**: Python server handling ASR (Automatic Speech Recognition), TTS (Text-to-Speech), and LLM communication
- **AWS Integration**: Claude API via AWS Bedrock for natural language processing
- **Local Processing**: Speech recognition and synthesis handled locally for privacy and low latency
- **WebSocket Communication**: Real-time communication between components

## Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js and npm
- AWS account with Bedrock access
- Live2D model (default provided)

### AWS Backend Setup

1. Deploy the AWS SAM template in the `backend` directory:
   ```bash
   cd backend
   sam deploy
   ```

2. Configure environment variables:
   - Windows: `call set_aws_env.bat`
   - Linux/macOS: `source set_aws_env.sh`

3. Update your configuration:
   - Set the HTTP Base URL in `.env` or through the Settings panel
   - Configure `conf.yaml` to use the AWS HTTP endpoint

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/LLM-Live2D-Desktop-Assistant
   cd LLM-Live2D-Desktop-Assistant
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Node.js dependencies:
   ```bash
   npm install
   ```

4. Configure the application:
   - Edit `conf.yaml` with your settings
   - Set up your Live2D model (if using a custom one)

## Usage

### Starting the Assistant

1. Start the backend server:
   ```bash
   python server.py
   ```

2. Launch the desktop application:
   ```bash
   npm start
   ```

   Alternatively, use the built executable if available.

### Interacting with the Assistant

- **Voice Commands**: Simply speak after the assistant is listening
- **Wake Word**: Say the configured wake word to activate the assistant from sleep mode
- **Settings**: Access settings through the system tray icon
- **Special Commands**:
  - Ask for songs: "Can you sing [song name]?"
  - Screen capture: Use a snipping tool to share screen content
  - Clipboard access: The assistant can access clipboard content when shared

## Configuration

### Assistant Persona

The assistant comes with a service-oriented persona by default, designed to be helpful, attentive, and professional. You can customize the persona in `conf.yaml`:

```yaml
PERSONA_CHOICE: "service_assistant"  # Default service-oriented persona
```

Available personas:
- `service_assistant`: Professional, helpful desktop assistant (default)
- `elaina2`: Character-based persona with a magical theme
- Other personas available in the `prompts/persona/` directory

### Speech Recognition Options

Configure speech recognition in `conf.yaml`:
```yaml
ASR_MODEL: "Faster-Whisper"  # Options: Faster-Whisper, WhisperCPP, etc.
```

### Text-to-Speech Options

Configure text-to-speech in `conf.yaml`:
```yaml
TTS_MODEL: "edgeTTS"  # Options: edgeTTS, AzureTTS, etc.
```

## Development

### Project Structure

```
/LLM-Live2D-Desktop-Assistant
  /backend          # Python backend server
  /frontend         # Electron frontend
  /asr              # Automatic Speech Recognition modules
  /tts              # Text-to-Speech modules
  /llm              # Language Model integration
  /prompts          # System prompts and personas
  /static           # Static assets and Live2D models
```

### Building for Distribution

To build the desktop application:

```bash
npm run build
```

This will generate executables in the `dist/` directory:
- Windows: `.exe` file
- macOS: `.dmg` file

The backend server still needs to be run separately.

## Troubleshooting

### Common Issues

1. **Connection Issues**:
   - Verify AWS credentials are set correctly
   - Check that the backend server is running
   - Ensure WebSocket URL is correctly configured

2. **Audio Problems**:
   - Check microphone permissions
   - Verify TTS engine is properly configured
   - See `AUDIO_FIX_README.md` for detailed solutions

3. **AWS Integration**:
   - Verify AWS Bedrock access is properly configured
   - Check Lambda function deployment
   - See `AWS_CLAUDE_SETUP.md` for detailed instructions

## Future Enhancements

- Improved computer control functions
- Enhanced UI with chat history
- More Live2D expressions and idle animations
- Cloud STT/TTS fallbacks
- Cognito authentication for AWS backend

## License

[MIT License](LICENSE)

## Acknowledgements

- Based on [Open-LLM-VTuber](https://github.com/t41372/Open-LLM-VTuber)
- Live2D model by [MNDIA](https://www.aplaybox.com/details/model/0MAXIOhAZAUw)
- Voice model by [灰发的伊蕾娜](https://www.bilibili.com/video/BV1Df421m7bm/)
