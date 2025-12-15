# Story Submission API Setup

## Overview

The story submission form uses a serverless API endpoint to securely create GitHub issues without exposing authentication tokens in the client-side code.

## Architecture

```
User fills form → submit_story.js → /api/create-story-issue → GitHub API → Issue created
                                    (Serverless Function)
                                    (Uses secure token)
```

## Deployment Instructions

### Option 1: Deploy to Vercel (Recommended)

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy the project**:
   ```bash
   vercel
   ```

4. **Add GitHub Token as Environment Variable**:

   a. Create a GitHub Personal Access Token:
      - Go to https://github.com/settings/tokens
      - Click "Generate new token" → "Generate new token (classic)"
      - Name: `RuffTree Story Submission`
      - Scopes: Select `public_repo` (or `repo` for private repos)
      - Click "Generate token" and copy it

   b. Add to Vercel:
      - Go to your Vercel project dashboard
      - Navigate to "Settings" → "Environment Variables"
      - Add new variable:
        - Name: `GITHUB_TOKEN`
        - Value: (paste your token)
        - Environments: Select "Production", "Preview", and "Development"
      - Click "Save"

5. **Redeploy** (to apply environment variables):
   ```bash
   vercel --prod
   ```

### Option 2: Deploy to Netlify

1. **Install Netlify CLI**:
   ```bash
   npm i -g netlify-cli
   ```

2. **Login to Netlify**:
   ```bash
   netlify login
   ```

3. **Create `netlify.toml`** in the project root:
   ```toml
   [build]
     publish = "."

   [functions]
     directory = "api"
   ```

4. **Deploy**:
   ```bash
   netlify deploy --prod
   ```

5. **Add Environment Variable**:
   - Go to Netlify dashboard → Site settings → Environment variables
   - Add `GITHUB_TOKEN` with your GitHub token

### Option 3: Local Development

1. **Install dependencies** (if using local Vercel dev server):
   ```bash
   npm install -g vercel
   ```

2. **Create `.env` file** in project root:
   ```bash
   cp .env.example .env
   # Edit .env and add your GitHub token
   ```

3. **Run local development server**:
   ```bash
   vercel dev
   ```

4. The form will now work at `http://localhost:3000`

## Security Considerations

- **Never commit the `.env` file** - it's already in `.gitignore`
- **Never expose the GitHub token** in client-side code
- The serverless function runs on the server and keeps the token secure
- The token should have minimal permissions (only `public_repo` scope)

## Testing

To test the API endpoint:

```bash
curl -X POST http://localhost:3000/api/create-story-issue \
  -H "Content-Type: application/json" \
  -d '{
    "title": "[Story] Test Story",
    "body": "### Story Title\n\nTest\n\n### Your Name (Author)\n\nTester\n\n### Your Story\n\nThis is a test story.",
    "labels": ["family-story", "story:pending"]
  }'
```

Expected response:
```json
{
  "success": true,
  "issueUrl": "https://github.com/patruff/rufftree/issues/XXX",
  "issueNumber": XXX
}
```

## Troubleshooting

### Error: "Server configuration error"
- The `GITHUB_TOKEN` environment variable is not set
- Solution: Add the token in Vercel/Netlify environment variables and redeploy

### Error: "Failed to create GitHub issue"
- The GitHub token may be invalid or expired
- The token may not have the correct permissions
- Solution: Generate a new token with `public_repo` scope

### Form submits but no issue is created
- Check the browser console for errors
- Verify the API endpoint URL is correct
- Check Vercel/Netlify function logs for errors

## File Structure

```
/home/user/rufftree/
├── api/
│   └── create-story-issue.js   # Serverless function
├── submit_story.html            # Form UI
├── submit_story.js              # Form logic (calls API)
├── vercel.json                  # Vercel configuration
├── .env.example                 # Environment variable template
└── API_SETUP.md                # This file
```
