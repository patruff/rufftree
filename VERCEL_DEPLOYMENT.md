# Vercel Deployment Guide - Real-Time Query API

This guide walks you through deploying the real-time query API to Vercel, enabling instant answers on your GitHub Pages site.

## Overview

The system consists of:
- **Vercel Serverless Function** (`/api/query.py`) - Handles RAG queries
- **GitHub Pages Frontend** (`queries.html`) - User interface
- **Google GenAI** - RAG backend with family documents

## Prerequisites

1. A Vercel account (free Hobby plan is sufficient)
2. Your `GOOGLE_GENAI_API_KEY`
3. Your rufftree File Search store name

## Step 1: Install Vercel CLI (Optional)

```bash
npm install -g vercel
```

Or use the Vercel web dashboard (recommended for first-time users).

## Step 2: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard (Recommended)

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "Add New Project"
3. Import your `patruff/rufftree` GitHub repository
4. Configure the project:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave default)
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty
5. Click "Deploy"

### Option B: Deploy via CLI

```bash
cd /path/to/rufftree
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? (select your account)
- Link to existing project? **N**
- Project name? **rufftree** (or your choice)
- In which directory is your code located? **./**
- Deploy? **Y**

## Step 3: Set Environment Variables

After deploying, you need to add your API key:

### Via Vercel Dashboard:

1. Go to your project dashboard
2. Click "Settings" tab
3. Click "Environment Variables" in sidebar
4. Add these variables:

   | Variable Name | Value |
   |---------------|-------|
   | `GOOGLE_GENAI_API_KEY` | Your Google AI API key |
   | `RUFFTREE_STORE_NAME` | `fileSearchStores/rufftreefamilydocuments-nrf1ymofronp` |

5. Click "Save"

### Via CLI:

```bash
vercel env add GOOGLE_GENAI_API_KEY
# Paste your API key when prompted

vercel env add RUFFTREE_STORE_NAME
# Enter: fileSearchStores/rufftreefamilydocuments-nrf1ymofronp
```

## Step 4: Redeploy with Environment Variables

After adding environment variables, trigger a new deployment:

### Via Dashboard:
1. Go to "Deployments" tab
2. Click "..." menu on latest deployment
3. Click "Redeploy"

### Via CLI:
```bash
vercel --prod
```

## Step 5: Update queries.html with Your Vercel URL

1. After deployment, Vercel will give you a URL like: `https://rufftree-abc123.vercel.app`

2. Edit `queries.html` line 443 and replace the placeholder:

   ```javascript
   // Change this:
   const apiUrl = window.location.hostname === 'localhost'
       ? 'http://localhost:3000/api/query'
       : 'https://YOUR-VERCEL-DEPLOYMENT.vercel.app/api/query';

   // To this (use your actual URL):
   const apiUrl = window.location.hostname === 'localhost'
       ? 'http://localhost:3000/api/query'
       : 'https://rufftree-abc123.vercel.app/api/query';
   ```

3. Commit and push the change:

   ```bash
   git add queries.html
   git commit -m "Update API endpoint with Vercel deployment URL"
   git push
   ```

4. GitHub Pages will rebuild (takes 1-2 minutes)

## Step 6: Test the Deployment

1. Visit your Vercel function directly to verify it's working:
   ```
   https://your-deployment.vercel.app/api/query
   ```
   You should see JSON with API info.

2. Visit your GitHub Pages site:
   ```
   https://patruff.github.io/rufftree/queries.html
   ```

3. Ask a test question like "What do we know about the Ruff family?"

4. You should get an answer in 2-5 seconds!

## Troubleshooting

### Function Timeout
If queries timeout, increase `maxDuration` in `vercel.json`:
```json
{
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.11",
      "maxDuration": 60
    }
  }
}
```
Note: Hobby plan max is 60 seconds.

### CORS Errors
Make sure `vercel.json` has the CORS headers configured (already included).

### API Key Not Working
1. Verify the environment variable is set correctly
2. Redeploy after adding environment variables
3. Check Vercel function logs in dashboard

### Function Returns 500 Error
1. Go to Vercel Dashboard → Your Project → Functions
2. Click on the `/api/query` function
3. View the logs to see the error details

## Monitoring Usage

### Vercel Dashboard
Monitor your usage at: Dashboard → Settings → Usage

Key metrics on Hobby plan:
- Function Invocations: 1,000,000/month (free)
- Function Duration: 100 GB-Hours/month (free)
- Bandwidth: 100 GB/month (free)

### Expected Usage
- Each query = 1 invocation
- Each query ≈ 2-5 seconds (depending on complexity)
- Typical family usage well within free limits

## Cost Estimate

### Vercel (Hobby Plan - FREE)
- ✅ 1M function invocations/month
- ✅ 100 GB-hours execution time
- ✅ Should handle hundreds of queries per day easily

### Google GenAI
- File Search queries: ~$0.05 per 1000 queries
- With typical family usage (10-50 queries/month): **~$0.00-0.01/month**

**Total estimated cost: $0-1/month** 🎉

## Going Live

Once everything works:

1. ✅ Vercel deployment complete
2. ✅ Environment variables set
3. ✅ queries.html updated with correct URL
4. ✅ Test queries returning answers
5. ✅ Share the link with family!

Your family can now get instant answers about family history at:
`https://patruff.github.io/rufftree/queries.html`

## Updating the Function

To update the query function:

1. Make changes to `api/query.py`
2. Commit and push to GitHub
3. Vercel will automatically deploy (if you enabled GitHub integration)

Or deploy manually:
```bash
vercel --prod
```

## Support

- Vercel Docs: https://vercel.com/docs
- Google GenAI Docs: https://ai.google.dev/docs
- Function Logs: Vercel Dashboard → Functions → View Logs
