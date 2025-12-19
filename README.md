# Rufftree Family Archive

An AI-powered family history system with interactive visualizations, voice Q&A, and intelligent document search using Google's Gemini RAG.

## 🌳 View the Family Tree

**Interactive Tree**: [https://patruff.github.io/rufftree/](https://patruff.github.io/rufftree/)
**Voice Q&A Agent**: [https://rufftree-voice.fly.dev/](https://rufftree-voice.fly.dev/)

Ask questions about family history using natural voice conversation powered by Grok's Voice Agent API.

## 👥 How to Contribute

Family members can participate without any technical knowledge:

| Action | How | What Happens |
|--------|-----|--------------|
| **Ask a question** | Visit the [Voice Agent](https://rufftree-voice.fly.dev/) | Chat with AI about family history |
| **Share a story** | Click "Submit Story" on the website | Story is added to the archive |
| **Request adding someone** | Create an [Add Person Issue](../../issues/new?template=add-person.yml) | Person is added to the tree |

All submissions are automatically processed and appear on the website within minutes.

## ✨ Features

- **Interactive Family Tree** - Beautiful expandable tree with generations, relationships, and health tracking
- **Voice Q&A** - Real-time voice conversations about family history using Grok Voice Agent
- **Smart Document Search** - AI-powered RAG using Google Gemini to search family documents
- **Auto-Processing** - GitHub Actions automatically handle stories, queries, and new people
- **Person Generator** - Web UI for creating detailed family member profiles
- **Health Tracking** - Track conditions, causes of death, and heritable risk factors
- **Genetic Lineages** - Track Y chromosome and mtDNA lines

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

Create a `.env` file:

```bash
# Google Gemini API (for RAG)
GOOGLE_GENAI_API_KEY=your_gemini_key

# XAI API (for voice agent)
XAI_API_KEY=your_xai_key

# Google Drive Service Account (for document sync)
GOOGLE_DRIVE_CREDENTIALS='{"type":"service_account",...}'
```

**Get API Keys:**
- Gemini: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- XAI: [https://console.x.ai/](https://console.x.ai/)

### 3. Set Up GitHub Secrets

For auto-deployment and workflows to work, add these secrets in **Settings → Secrets and variables → Actions**:

- `GOOGLE_GENAI_API_KEY`
- `XAI_API_KEY`
- `GOOGLE_DRIVE_CREDENTIALS`
- `FLY_API_TOKEN` (for voice agent deployment)

### 4. Deploy

Push to `main` branch to auto-deploy:
- GitHub Pages: Family tree website
- Fly.io: Voice agent (via GitHub Actions)

## 📝 Key Workflows

All workflows are in `.github/workflows/` and run automatically:

### Automatic Triggers

| Workflow | Trigger | What It Does |
|----------|---------|--------------|
| **Deploy Pages** | Push to `main` | Updates family tree website |
| **Deploy Voice Agent** | Push to `main` | Updates Fly.io voice agent |
| **Process Story** | `family-story` label added | Saves story to archive |
| **Process Query** | `family-query` label added | Answers question with RAG |
| **Add Person** | `add-person` label added | Adds person to family tree |
| **Sync Drive** | Every 6 hours | Syncs new documents from Google Drive |

### Manual Workflows

Run from **Actions** tab:

| Workflow | Use Case |
|----------|----------|
| **Query Documents** | Test RAG queries |
| **Add Story to RAG** | Quick story entry (owner only) |
| **List RAG Documents** | View all indexed documents |
| **Edit Person** | Update person information |
| **Analyze Coverage** | Check who needs more documentation |

## 🗂️ Project Structure

```
rufftree/
├── index.html              # Interactive family tree
├── graph.html              # Network graph visualization
├── voice_query.html        # Voice Q&A interface (served by Fly.io)
├── person_generator.html   # Create new family members
├── family_tree.json        # All family data
├── voice_server.py         # FastAPI server for voice agent
├── sync_drive_documents.py # Sync docs from Google Drive
├── add_story_to_drive.py   # Add stories to archive
└── .github/workflows/      # GitHub Actions
```

## 🎤 Voice Agent

The voice agent runs on Fly.io and provides real-time voice conversations:

**How it works:**
1. Browser captures microphone audio
2. WebSocket streams to `voice_server.py`
3. Server proxies to Grok Voice Agent API
4. When user asks a question, Grok calls `query_family_history()` function
5. Server executes RAG query using Gemini
6. Grok speaks the answer back

**Tech Stack:**
- FastAPI + WebSockets for proxy server
- Grok Voice Agent API for voice conversation
- Google Gemini File Search for RAG queries
- Fly.io for deployment with auto-sleep

## 📊 Family Data

The `family_tree.json` file contains comprehensive data:

**Core Fields:**
- `id`, `name`, `dob`, `dod` - Basic info
- `spouseId`, `parentIds`, `siblingIds`, `childrenIds` - Relationships
- `generation`, `from_pat` - Auto-calculated generation labels

**Optional Fields:**
- `ethnicity` - Auto-calculated from parents
- `health_condition`, `causeOfDeath` - Health tracking
- `heritable_risk` - Auto-calculated genetic risk
- `home_city`, `home_state` - Location
- `occupation`, `phone`, `notes` - Contact info
- `attributes`, `personality` - Big Five traits

**Auto-Calculation Scripts:**
```bash
python3 add_generations.py       # Calculate generations
python3 add_ethnicity.py         # Calculate ethnicity from parents
python3 add_heritable_risk.py    # Calculate health risk
python3 calculate_completion.py  # Calculate profile completion
```

## 🔍 RAG System

**Store Name**: `rufftree-family-documents`

Documents are synced from Google Drive folder "rufftree" and indexed using Gemini File Search.

**Supported Files**: PDF, DOCX, TXT, MD, Google Docs

**Query with Metadata:**
```python
# Only search stories ABOUT Joe (not stories BY Joe)
query_documents("What are Joe's hobbies?",
                metadata_filter="subject_of_story='Joe Ruff'")
```

**Pricing:**
- Storage: FREE (unlimited)
- Queries: FREE
- Initial indexing: $0.15 per 1M tokens (one-time)

## 🛠️ Development

**Local Testing:**
```bash
# Run voice server locally
python voice_server.py

# Test RAG queries
export QUERY="When did the Ruff family immigrate?"
python test_file_search.py

# Sync documents from Drive
python sync_drive_documents.py
```

**Add a Story:**
```bash
python add_story_to_drive.py \
  --title "Story Title" \
  --about "Person Name" \
  --story "Story content..."
```

**Edit Family Data:**
```bash
# View person info
python edit_person.py "Patrick Ruff" --view-only

# Update person info
python edit_person.py "Patrick Ruff" --occupation "Engineer"
```

## 📦 Deployment

**GitHub Pages:**
- Automatically deploys on push to `main`
- Serves static HTML/CSS/JS from root directory

**Fly.io (Voice Agent):**
- Automatically deploys via `.github/workflows/deploy-voice-agent.yml`
- Uses `Dockerfile` and `fly.toml` for configuration
- Auto-sleeps when idle (free tier)

## 🤝 Contributing

This project is adapted from the longevitypdf RAG system. Feel free to adapt for your own family archive!

## 📄 License

MIT License
