# Claude Opus Setup Guide for VTuber Assistant

## ✅ Changes Made for Claude Opus

### 1. AWS Backend Configuration
Updated `backend/template.yml`:
- **Model**: `anthropic.claude-opus-4-1-20250805-v1:0`
- **Lambda Timeout**: 60 seconds (increased from 15)
- **Lambda Memory**: 1024 MB (increased from 256)
- **Max Tokens**: 2048 (increased from 1024)
- **Added CORS support** for browser testing

### 2. Local Configuration
Updated `conf.yaml`:
- Simplified configuration for testing
- Disabled complex features initially
- Focus on TTS/STT functionality

### 3. Test Files Created
- `test_tts.py` - Test Text-to-Speech
- `test_stt.py` - Test Speech-to-Text
- `test_connection.js` - Test WebSocket connection
- `test_claude_opus.py` - Test Claude Opus model
- `start_app.bat` - Easy app launcher

## 🚀 Quick Start Instructions

### Step 1: Install Dependencies

```bash
# Python dependencies
pip install edge-tts faster-whisper sounddevice soundfile pygame numpy
pip install fastapi uvicorn websocket-client requests pyyaml loguru

# Node dependencies
cd LLM-Live2D-Desktop-Assitant-main
npm install
```

### Step 2: Deploy AWS Backend with Opus

```bash
# Navigate to backend directory
cd LLM-Live2D-Desktop-Assitant-main/backend

# Build the SAM application
sam build

# Deploy (first time - will prompt for configuration)
sam deploy --guided

# Follow prompts:
# - Stack Name: live2d-aws-backend
# - AWS Region: us-west-2
# - Confirm changes: y
# - Allow SAM CLI to create IAM roles: y
```

After deployment, note the **HttpBase** URL from the outputs.

### Step 3: Configure Your Endpoint

Create `.env` file in root directory:
```env
HTTP_BASE=https://your-actual-api.execute-api.us-west-2.amazonaws.com/dev
```

Or set environment variable:
```bash
# Windows
set HTTP_BASE=https://your-actual-api.execute-api.us-west-2.amazonaws.com/dev

# Mac/Linux
export HTTP_BASE=https://your-actual-api.execute-api.us-west-2.amazonaws.com/dev
```

### Step 4: Request Claude Opus Access in AWS

1. Go to AWS Console → Bedrock → Model access
2. Click "Edit" or "Request access"
3. Find "Anthropic Claude Opus" 
4. Request access (usually instant approval)
5. Wait for status to show "Access granted"

### Step 5: Test Components

```bash
# Test TTS (should hear voice)
python test_tts.py

# Test STT (speak when prompted)
python test_stt.py

# Test Claude Opus
python test_claude_opus.py

# Test WebSocket
node test_connection.js
```

### Step 6: Start the Application

```bash
# Windows - use the batch file
start_app.bat

# Or manually:
# Terminal 1
python server.py

# Terminal 2  
npm start
```

## 🔧 Troubleshooting

### Issue: "Model not found" error
**Solution**: Request access to Claude Opus in AWS Bedrock

### Issue: TTS not working
```bash
pip install --upgrade edge-tts pygame
```

### Issue: STT not working
```bash
pip install --upgrade faster-whisper
# Check microphone permissions in Windows Settings
```

### Issue: Port already in use
```bash
# Find and kill process on port 1018
netstat -ano | findstr :1018
taskkill /PID [PID_NUMBER] /F
```

### Issue: AWS endpoint timeout
- Opus model might be cold starting
- First request can take 20-30 seconds
- Subsequent requests will be faster

## 📊 Claude Opus Specifications

| Feature | Value |
|---------|-------|
| Model ID | anthropic.claude-opus-4-1-20250805-v1:0 |
| Context Window | 200K tokens |
| Max Output | 2048 tokens (configurable) |
| Strengths | Complex reasoning, creativity, nuanced responses |
| Cost | ~$15/million input tokens |
| Response Time | 2-5 seconds (after warm-up) |

## 🎯 Testing Checklist

- [ ] Python dependencies installed
- [ ] Node dependencies installed  
- [ ] AWS backend deployed
- [ ] Claude Opus access granted
- [ ] HTTP_BASE configured
- [ ] TTS test passing
- [ ] STT test passing
- [ ] Claude Opus test passing
- [ ] WebSocket connecting
- [ ] Full app launches

## 💡 Tips for Using Claude Opus

1. **Longer, detailed responses**: Opus excels at complex tasks
2. **Creative writing**: Great for roleplay and personality
3. **Technical explanations**: Can provide in-depth code examples
4. **Multi-step reasoning**: Handles complex logic well

## 📝 Example Prompts for VTuber Persona

```python
# In conf.yaml, update SYSTEM_PROMPT:
SYSTEM_PROMPT: |
  You are an intelligent and cheerful Live2D VTuber assistant named Aria. 
  You have a warm, friendly personality and enjoy helping users with their tasks.
  You speak casually but professionally, using occasional emotes like ^_^ or :)
  You're knowledgeable about technology, programming, and creative topics.
  Keep responses engaging but concise (2-3 sentences for simple questions).
```

## 🚦 Next Steps

Once everything is working:

1. **Add Free-Roaming Feature**: See `vtuber-free-roam-feature.md`
2. **Customize Persona**: Edit system prompt in `conf.yaml`
3. **Adjust Voice**: Change TTS voice in `conf.yaml`
4. **Fine-tune Model**: Adjust temperature and max_tokens

---

**Ready to go!** Your VTuber assistant should now be powered by Claude Opus with working TTS/STT.