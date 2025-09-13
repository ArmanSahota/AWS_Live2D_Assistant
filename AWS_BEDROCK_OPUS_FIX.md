# AWS Bedrock Claude Opus Fix

## Issue
AWS Bedrock now requires using an **Inference Profile** for Claude Opus models instead of direct model invocation. The error message:
```
Invocation of model ID anthropic.claude-opus-4-1-20250805-v1:0 with on-demand throughput isn't supported. 
Retry your request with the ID or ARN of an inference profile that contains this model.
```

## Solution Options

### Option 1: Use Claude 3.5 Sonnet (Recommended - Immediate Fix)
Claude 3.5 Sonnet is more cost-effective and supports direct invocation:

1. Update `LLM-Live2D-Desktop-Assitant-main/backend/template.yml`:
```yaml
Environment:
  Variables:
    MODEL_ID: anthropic.claude-3-5-sonnet-20241022-v2:0  # Changed from Opus
```

2. Redeploy:
```bash
cd LLM-Live2D-Desktop-Assitant-main/backend
sam build
sam deploy
```

### Option 2: Create an Inference Profile for Opus
If you specifically need Opus:

1. Go to AWS Console → Bedrock → Inference profiles
2. Click "Create inference profile"
3. Select:
   - Model: Claude Opus 4.1
   - Throughput: On-demand
   - Region: us-west-2
4. Note the Profile ARN (e.g., `arn:aws:bedrock:us-west-2:xxxxx:inference-profile/your-profile-id`)
5. Update template.yml with the Profile ARN instead of model ID

### Option 3: Use a Different Model
Other available Claude models that support direct invocation:
- `anthropic.claude-3-haiku-20240307-v1:0` (Fastest, cheapest)
- `anthropic.claude-3-5-sonnet-20241022-v2:0` (Best balance)
- `anthropic.claude-instant-v1` (Legacy, fast)

## Quick Test with Sonnet
For immediate testing, let's use Claude 3.5 Sonnet which is actually newer and more capable than the Opus version you're using:

```python
# Updated test_claude_sonnet.py
import requests
import json
import os

HTTP_BASE = 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev'

response = requests.post(
    f"{HTTP_BASE}/claude",
    json={
        "text": "Hello! What model are you?",
        "system": "You are a helpful VTuber assistant."
    },
    timeout=30
)

print(response.json())
```

## Current Status
- ✅ TTS Working (Edge TTS)
- ✅ STT Working (Whisper)
- ❌ Claude Opus (Requires inference profile)
- ⏳ Claude Sonnet (Can work with direct invocation)

## Next Steps
1. **For Quick Testing**: Switch to Claude 3.5 Sonnet
2. **For Production**: Create an inference profile for your preferred model
3. **Launch App**: Once Claude is working, run `start_app.bat`