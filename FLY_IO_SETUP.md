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

**IMPORTANT: You MUST add all 4 secrets before pushing code!**

1. Go to your GitHub repo: `https://github.com/patruff/rufftree`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these secrets:

| Secret Name | Value | Where to Get |
|-------------|-------|--------------|
| `FLY_API_TOKEN` | Your Fly.io token | From Step 2 above |
| `XAI_API_KEY` | Your xAI API key | [console.x.ai](https://console.x.ai) - click API Keys |
| `GOOGLE_GENAI_API_KEY` | Your Google AI key | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| `RUFFTREE_STORE_NAME` | `fileSearchStores/rufftreefamilydocuments-nrf1ymofronp` | Exact value shown |

**Double-check each secret:**
- Click on the secret name after creating it
- GitHub will show "Last updated" - make sure it's recent
- If you see "XAI_API_KEY not set" in logs, the secret wasn't created properly

**Getting xAI API Key:**
1. Go to [console.x.ai](https://console.x.ai)
2. Sign up/login
3. Click "API Keys" in sidebar
4. Click "Create API Key"
5. Copy the key (starts with `xai-...`)
6. Paste into GitHub secret

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

### ERROR: "XAI_API_KEY not set" in Logs

**This is the most common issue!** If you see this in Fly.io logs, the secrets weren't set correctly.

**Fix:**

**Option 1 - GitHub Secrets (Recommended):**
1. Go to `https://github.com/patruff/rufftree/settings/secrets/actions`
2. Verify all 4 secrets exist:
   - `FLY_API_TOKEN`
   - `XAI_API_KEY`
   - `GOOGLE_GENAI_API_KEY`
   - `RUFFTREE_STORE_NAME`
3. If missing, click "New repository secret" and add them
4. Push a small code change to trigger re-deploy:
   ```bash
   git commit --allow-empty -m "Trigger redeploy with secrets"
   git push origin main
   ```
5. Wait 2 minutes and check logs: `fly logs`
6. You should see: `✅ XAI_API_KEY configured (xai-12345...)`

**Option 2 - Fly CLI (Quick Fix):**
```bash
# Install Fly CLI if not installed
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Set secrets manually
fly secrets set XAI_API_KEY=your-xai-key-here
fly secrets set GOOGLE_GENAI_API_KEY=your-google-key-here
fly secrets set RUFFTREE_STORE_NAME=fileSearchStores/rufftreefamilydocuments-nrf1ymofronp

# This triggers automatic redeploy - wait 1-2 minutes
# Check logs
fly logs
```

**Verify secrets are set:**
```bash
fly secrets list
```

You should see:
```
NAME                      DIGEST                           CREATED AT
GOOGLE_GENAI_API_KEY      abc123...                        1m ago
RUFFTREE_STORE_NAME       def456...                        1m ago
XAI_API_KEY               ghi789...                        1m ago
```

**Check deployment logs:**
```bash
fly logs
```

**Correct output should show:**
```
✅ XAI_API_KEY configured (xai-12345...)
✅ GOOGLE_GENAI_API_KEY configured (AIzaSyXXX...)
✅ RUFFTREE_STORE_NAME: fileSearchStores/rufftreefamilydocuments-nrf1ymofronp
✅ All environment variables configured correctly!
```

### Deployment Failed

1. Check GitHub Actions logs: `https://github.com/patruff/rufftree/actions`
2. Common issues:
   - Missing secrets: Add all 4 secrets in GitHub (see above)
   - App name taken: Change `app = "rufftree-voice"` in `fly.toml`
   - Token expired: Generate new Fly.io token

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
