# Fly.io Auto-Deploy Setup Guide

This guide shows you how to set up automatic deployment to Fly.io using GitHub Actions. Once configured, the voice agent deploys automatically whenever you push code.

## One-Time Setup (5 minutes)

### Step 1: Create Fly.io Account

1. Go to [fly.io/signup](https://fly.io/signup)
2. Sign up (free tier includes: 3 shared VMs, 160GB bandwidth/month)
3. Add credit card (required but won't be charged on free tier)

### Step 2: Get Your Fly.io API Token

1. Go to [fly.io/user/personal_access_tokens](https://fly.io/user/personal_access_tokens)
2. Click "Create token"
3. Name it: `GitHub Actions`
4. Copy the token (you'll need it in next step)

### Step 3: Add Secrets to GitHub

1. Go to your GitHub repo: `https://github.com/patruff/rufftree`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these secrets:

| Secret Name | Value | Where to Get |
|-------------|-------|--------------|
| `FLY_API_TOKEN` | Your Fly.io token | From Step 2 |
| `XAI_API_KEY` | Your xAI API key | [console.x.ai](https://console.x.ai) |
| `GOOGLE_GENAI_API_KEY` | Your Google AI key | Already have this |
| `RUFFTREE_STORE_NAME` | `fileSearchStores/rufftreefamilydocuments-nrf1ymofronp` | Current store |

### Step 4: Create Fly.io App (One-Time CLI Setup)

You only need to do this once to create the app. After this, GitHub Actions handles all deployments.

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Create app (this reserves your app name)
fly apps create rufftree-voice --region iad

# That's it! GitHub Actions will handle deployments from now on.
```

**Alternative**: Skip CLI entirely and let GitHub Actions create the app on first deploy:
```bash
# Just push to main branch and the workflow will create the app automatically
git push origin main
```

### Step 5: Push Code to Deploy

```bash
# Push to main branch
git push origin main

# GitHub Actions will automatically:
# 1. Build Docker image
# 2. Deploy to Fly.io
# 3. Set environment variables from secrets
# 4. Run health check
```

Watch the deployment: `https://github.com/patruff/rufftree/actions`

Your app will be live at: `https://rufftree-voice.fly.dev`

## That's It! 🎉

From now on, every time you push code that changes voice-related files, it auto-deploys.

## Monitoring

### Check Deployment Status

```bash
fly status
```

### View Logs

```bash
fly logs
```

### Check Health

Visit: `https://rufftree-voice.fly.dev/health`

Should return:
```json
{
  "status": "ok",
  "xai_configured": true,
  "genai_configured": true
}
```

### Open App

```bash
fly open
```

Or visit directly: `https://rufftree-voice.fly.dev`

## Troubleshooting

### Deployment Failed

1. Check GitHub Actions logs: `https://github.com/patruff/rufftree/actions`
2. Common issues:
   - Missing secrets: Add all 4 secrets in GitHub
   - App name taken: Change `app = "rufftree-voice"` in `fly.toml`
   - Token expired: Generate new Fly.io token

### Secrets Not Working

If environment variables aren't being set:

```bash
# Manually set secrets (one-time fix)
fly secrets set XAI_API_KEY=your-key
fly secrets set GOOGLE_GENAI_API_KEY=your-key
fly secrets set RUFFTREE_STORE_NAME=fileSearchStores/rufftreefamilydocuments-nrf1ymofronp
```

### Check Current Secrets

```bash
fly secrets list
```

### App Won't Start

Check logs for errors:
```bash
fly logs --tail
```

Common causes:
- Missing dependencies in `requirements.txt`
- Port mismatch (should be 8000)
- Missing required files

## Manual Deploy (If Needed)

If you ever need to manually deploy:

```bash
fly deploy
```

But normally you don't need this - GitHub Actions handles it!

## Update Secrets

To change secrets later:

**Option 1**: Update in GitHub (recommended)
1. Go to repo → Settings → Secrets
2. Update the secret value
3. Push any code change to trigger redeploy

**Option 2**: Use Fly CLI
```bash
fly secrets set XAI_API_KEY=new-key
```

## Cost

**Fly.io Free Tier Includes:**
- ✅ 3 shared-cpu VMs (1x256MB is plenty)
- ✅ 160GB outbound bandwidth/month
- ✅ Auto-sleep when idle (scales to zero)
- ✅ Perfect for family usage

**Expected Usage:**
- Voice conversations: ~10-30 mins/month
- Bandwidth: ~1-5 GB/month
- Cost: **FREE** (within free tier limits)

If you exceed free tier:
- Additional compute: ~$2-3/month
- Additional bandwidth: ~$0.02/GB

**Total estimate: $0-3/month**

## Files Created

The following files enable auto-deployment:

- ✅ `Dockerfile` - Container configuration
- ✅ `fly.toml` - Fly.io app configuration
- ✅ `.github/workflows/deploy-voice-agent.yml` - Auto-deploy workflow

## Architecture

```
GitHub (push to main)
    ↓
GitHub Actions
    ↓ (builds Docker image)
Fly.io Registry
    ↓ (deploys container)
Fly.io VM (rufftree-voice.fly.dev)
    ↓ (serves)
Voice Agent WebSocket Server
```

## Features

✅ **Auto-deploy on push** - No manual commands needed
✅ **Secrets from GitHub** - Secure and centralized
✅ **Health checks** - Automatic monitoring
✅ **Auto-sleep** - Saves resources when idle
✅ **HTTPS by default** - Required for microphone access
✅ **WebSocket support** - For real-time voice
✅ **Global CDN** - Fast worldwide access

## Next Steps

Once deployed:

1. ✅ Visit `https://rufftree-voice.fly.dev`
2. ✅ Test the voice interface
3. ✅ Share URL with family
4. ✅ Monitor usage in Fly.io dashboard
5. ✅ Update code and push - auto-deploys!

## Support

- Fly.io Docs: https://fly.io/docs
- Fly.io Community: https://community.fly.io
- GitHub Actions: https://docs.github.com/en/actions
- Rufftree Issues: https://github.com/patruff/rufftree/issues
