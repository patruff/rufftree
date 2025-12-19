# Grok Voice Agent Deployment Guide

This guide explains how to deploy the Rufftree Voice Assistant - a real-time voice interface for asking questions about family history.

## Overview

The voice assistant uses:
- **Grok Voice Agent API** - Real-time voice conversations via WebSocket
- **Google GenAI RAG** - Search family documents for answers
- **FastAPI Server** - WebSocket proxy that handles RAG queries server-side
- **Web Interface** - Browser-based voice UI with microphone input

## Architecture

```
Browser (Microphone)
    ↓ WebSocket
FastAPI Server (voice_server.py)
    ↓ WebSocket
Grok Voice Agent API
    ↓ Function Call (when user asks about family)
Google GenAI RAG (searches family documents)
    ↓ Answer with Citations
Grok → Voice Response → Browser
```

## Prerequisites

1. **xAI API Key** - Get from [console.x.ai](https://console.x.ai)
2. **Google GenAI API Key** - Get from [aistudio.google.com](https://aistudio.google.com/apikey)
3. **Python 3.11+**
4. **Family documents uploaded** to Google GenAI File Search

## Local Development Setup

### 1. Install Dependencies

```bash
cd rufftree
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Create .env file
cat > .env << 'EOF'
# xAI API Key for Grok Voice Agent
XAI_API_KEY=your-xai-api-key-here

# Google GenAI API Key for RAG
GOOGLE_GENAI_API_KEY=your-google-api-key-here

# Rufftree File Search Store Name
RUFFTREE_STORE_NAME=fileSearchStores/rufftreefamilydocuments-nrf1ymofronp
EOF

# Load environment variables
export $(cat .env | xargs)
```

### 3. Run the Server

```bash
python voice_server.py
```

The server will start on `http://localhost:8000`

### 4. Test the Voice Interface

1. Open browser to `http://localhost:8000`
2. Click "Enable Microphone" (grant permission)
3. Click the microphone button
4. Say: "What do you know about Joe Ruff?"
5. Grok will:
   - Hear your question
   - Call the RAG function
   - Search family documents
   - Respond with voice answer

## Deploying to Production

### Option 1: Deploy to Fly.io (Recommended)

Fly.io offers free tier and WebSocket support.

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create fly.toml**
   ```toml
   app = "rufftree-voice"
   primary_region = "iad"

   [build]
   dockerfile = "Dockerfile"

   [http_service]
   internal_port = 8000
   force_https = true
   auto_stop_machines = true
   auto_start_machines = true
   min_machines_running = 0

   [[vm]]
   cpu_kind = "shared"
   cpus = 1
   memory_mb = 256
   ```

3. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY voice_server.py .
   COPY voice_query.html .
   COPY queries.html .
   COPY index.html .
   COPY graph.html .

   EXPOSE 8000

   CMD ["python", "voice_server.py"]
   ```

4. **Deploy**
   ```bash
   # Login
   fly auth login

   # Launch app
   fly launch

   # Set secrets
   fly secrets set XAI_API_KEY=your-xai-key
   fly secrets set GOOGLE_GENAI_API_KEY=your-google-key
   fly secrets set RUFFTREE_STORE_NAME=fileSearchStores/rufftreefamilydocuments-nrf1ymofronp

   # Deploy
   fly deploy
   ```

Your app will be available at `https://rufftree-voice.fly.dev`

### Option 2: Deploy to Railway

Railway also supports WebSocket and has a free tier.

1. Go to [railway.app](https://railway.app)
2. Create new project from GitHub repo
3. Add environment variables in dashboard:
   - `XAI_API_KEY`
   - `GOOGLE_GENAI_API_KEY`
   - `RUFFTREE_STORE_NAME`
4. Railway will auto-detect and deploy

### Option 3: Deploy to Your Own Server

If you have a VPS (AWS, DigitalOcean, etc.):

```bash
# SSH to server
ssh user@your-server.com

# Clone repo
git clone https://github.com/patruff/rufftree.git
cd rufftree

# Install dependencies
pip3 install -r requirements.txt

# Set environment variables
export XAI_API_KEY=your-xai-key
export GOOGLE_GENAI_API_KEY=your-google-key
export RUFFTREE_STORE_NAME=fileSearchStores/rufftreefamilydocuments-nrf1ymofronp

# Run with systemd or screen
screen -S voice-agent
python3 voice_server.py
```

For production, use a process manager:

```bash
# Install supervisor
sudo apt install supervisor

# Create config
sudo nano /etc/supervisor/conf.d/rufftree-voice.conf
```

```ini
[program:rufftree-voice]
directory=/home/user/rufftree
command=/usr/bin/python3 voice_server.py
environment=XAI_API_KEY="your-key",GOOGLE_GENAI_API_KEY="your-key",RUFFTREE_STORE_NAME="fileSearchStores/rufftreefamilydocuments-nrf1ymofronp"
autostart=true
autorestart=true
user=user
stdout_logfile=/var/log/rufftree-voice.log
stderr_logfile=/var/log/rufftree-voice.err.log
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start rufftree-voice
```

## GitHub Actions Deployment

If you want to deploy automatically on push:

**.github/workflows/deploy-voice.yml**
```yaml
name: Deploy Voice Agent

on:
  push:
    branches: [main]
    paths:
      - 'voice_server.py'
      - 'voice_query.html'
      - 'requirements.txt'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Fly.io
        uses: superfly/flyctl-actions/setup-flyctl@master
        with:
          version: latest

      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Add `FLY_API_TOKEN` to GitHub repository secrets.

## Cost Estimates

### xAI Grok Voice Agent
- **Free Tier**: $25 credit on signup
- **Pay-as-you-go**: ~$0.10 per minute of conversation
- **Expected family usage**: 10-30 mins/month = **$1-3/month**

### Google GenAI
- **RAG queries**: ~$0.05 per 1000 queries
- **Expected usage**: ~50 queries/month = **$0.00/month** (negligible)

### Hosting (Fly.io Free Tier)
- **Compute**: Free for apps that scale to zero
- **Bandwidth**: 100GB/month free

**Total estimated cost: $1-3/month** for typical family usage

## Features

### What Users Can Do

✅ **Ask questions by voice**: "When did Joe Ruff immigrate to America?"
✅ **Get voice answers**: Grok responds naturally with information from family documents
✅ **See transcripts**: Both questions and answers are transcribed
✅ **Source citations**: Answers include which documents were referenced
✅ **Natural conversation**: Can ask follow-up questions

### Example Interactions

**User**: "Tell me about Patrick and Jenny"
**Grok**: *[Searches family documents]* "Patrick Ruff and Jenny Wang got married in 2015. According to the wedding story, they met at..."

**User**: "When did the family come to America?"
**Grok**: *[Searches family documents]* "The Ruff family immigrated to America in the early 1900s. Based on immigration records..."

## Monitoring and Logs

### Check Server Health

```bash
curl http://your-server.com/health
```

Returns:
```json
{
  "status": "ok",
  "xai_configured": true,
  "genai_configured": true
}
```

### View Logs (Fly.io)

```bash
fly logs
```

### View Logs (Local)

Server prints logs to stdout:
```
🔌 Connecting to Grok Voice Agent API...
✅ Connected to Grok
✅ Grok session configured with RAG tool
🔧 Function called: query_family_history
   Arguments: {'question': 'What do you know about Joe Ruff?'}
   Querying: What do you know about Joe Ruff?
   ✅ RAG query completed, result sent to Grok
🗣️  Grok: Joe Ruff Sr. was born in...
```

## Troubleshooting

### Microphone Not Working
- Ensure HTTPS is enabled (required for microphone access)
- Check browser permissions (should prompt on first use)
- Try a different browser (Chrome/Edge recommended)

### Connection Errors
- Check that both API keys are set correctly
- Verify WebSocket port is open (8000)
- Check server logs for errors

### No Voice Response
- Check that Grok is calling the function (see logs)
- Verify Google GenAI store has documents
- Test RAG query separately: `python test_file_search.py`

### Audio Quality Issues
- Adjust sample rate in `voice_server.py` (default: 24000 Hz)
- Check network latency (use closer server region)
- Ensure microphone quality is good

## Security Considerations

1. **API Keys**: Never commit API keys to git
2. **HTTPS**: Use HTTPS in production for microphone access
3. **Rate Limiting**: Consider adding rate limits for public access
4. **Authentication**: Add user authentication if needed

## Next Steps

Once deployed:

1. ✅ Test with family members
2. ✅ Share the URL: `https://your-deployment.com`
3. ✅ Monitor usage and costs
4. ✅ Collect feedback on voice quality
5. ✅ Consider adding more voices (Grok supports 5 different voices)

## Alternative Voices

You can change the voice in `voice_server.py`:

```python
"voice": "Ara",  # Default - warm, friendly female
# Options:
# "Rex" - confident male
# "Sal" - smooth neutral
# "Eve" - energetic female
# "Leo" - authoritative male
```

## Support

- xAI Docs: https://docs.x.ai/docs
- Google GenAI Docs: https://ai.google.dev/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- GitHub Issues: https://github.com/patruff/rufftree/issues
