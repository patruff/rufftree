# Rufftree RAG System

A Retrieval Augmented Generation (RAG) system for Ruff family documents using Google's Gemini File Search API. This system automatically syncs documents from a Google Drive folder and provides AI-powered search and question answering capabilities.

## 🌳 View the Family Tree Online

**Live Demo**: [https://patruff.github.io/rufftree/](https://patruff.github.io/rufftree/)

The interactive family tree is automatically deployed to GitHub Pages and updates whenever you push changes to the `main` branch.

## 🔒 Privacy & Repository Settings

**Repository Privacy:**
- **Private Repository + Public Pages**: Keep your repository private (recommended for family privacy) while making the GitHub Pages site public. This allows family members to view the tree and ask questions without accessing source code or RAG system.
- **Fully Public**: Make everything public if you want to share the entire project openly.

**GitHub Pages with Private Repos:**
- GitHub Pages works on private repositories with GitHub Pro, Team, or Enterprise
- Alternatively, you can keep the repo private and deploy only the Pages site publicly
- Family members only need the URL to view the tree and submit questions

## Features

- **Interactive Family Tree**: Beautiful web-based visualization of the Ruff family genealogy
- **Family Query System**: Family members can ask questions, answered via AI RAG with source citations
- **Query Archive**: All questions and answers stored and displayed on the website
- **Editable JSON Data**: Manually edit `family_tree.json` to update family members and relationships
- **Document Upload**: Support for PDFs, Google Docs, DOCX, TXT, and Markdown files
- **Google Drive Sync**: Automatic synchronization from the "rufftree" Google Drive folder
- **RAG Queries**: Natural language search with AI-generated answers and citations
- **MCP Integration**: Model Context Protocol server for Claude Desktop integration
- **Free Storage**: Unlimited free storage in Google's File Search stores
- **Cost Efficient**: Only pay for initial indexing ($0.15 per 1M tokens), queries are free

## Architecture

```
Google Drive "rufftree" folder
        ↓
sync_drive_documents.py (automatic sync)
        ↓
Google File Search Store (separate from longevitypdf)
        ↓
mcp_server.py (MCP tools) ← Claude Desktop
        ↓
Gemini 2.5 Flash/Pro (RAG queries)
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Google GenAI API Key

1. Visit https://aistudio.google.com/apikey
2. Create an API key
3. Add to `.env` file:

```bash
GOOGLE_GENAI_API_KEY=your_api_key_here
```

### 3. Set Up Google Drive Service Account (for sync)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing project
3. Enable the Google Drive API
4. Create a Service Account:
   - Go to "IAM & Admin" → "Service Accounts"
   - Click "Create Service Account"
   - Give it a name like "rufftree-sync"
   - Click "Create and Continue"
   - Skip granting roles (click "Continue")
   - Click "Done"
5. Create a JSON key:
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Select "JSON" and click "Create"
   - Save the downloaded JSON file
6. Share your Google Drive folder with the service account:
   - Go to your Google Drive
   - Find or create the "rufftree" folder
   - Right-click and select "Share"
   - Add the service account email (found in the JSON file)
   - Give it "Viewer" permissions
7. Add the JSON contents to your environment:
   ```bash
   # Copy the entire JSON file contents to this variable
   GOOGLE_DRIVE_CREDENTIALS='{"type":"service_account","project_id":"..."}'
   ```

### 4. Configure Claude Desktop (Optional)

Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "rufftree": {
      "command": "python",
      "args": ["/absolute/path/to/rufftree/mcp_server.py"],
      "env": {
        "GOOGLE_GENAI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Usage

### View the Family Tree

Open `index.html` in your web browser to view the interactive family tree visualization.

#### Editing the Family Tree

1. Open `family_tree.json` in any text editor
2. Edit family member information:
   - `name`: Full name of the person
   - `dob`: Birth year in YYYY format
   - `dod`: Death year in YYYY format, or `"alive"` if living
   - `spouse`: Optional spouse object with same structure
   - `children`: Optional array of children
3. Save the file and refresh `index.html`

Example entry:
```json
{
  "id": "1",
  "name": "John Ruff",
  "dob": "1920",
  "dod": "1995",
  "spouse": {
    "id": "2",
    "name": "Mary Smith",
    "dob": "1922",
    "dod": "2000"
  },
  "children": [...]
}
```

The tree displays:
- **Name** of each person
- **Lifespan** (birth year - death year or "Present")
- **Age** (current age or years lived)
- **Visual indicators**: Green for living, purple for deceased
- **Statistics**: Total members, living, deceased, and generations

#### Setting Up GitHub Pages

To enable the live family tree website:

1. Go to your GitHub repository settings
2. Navigate to **Pages** (in the left sidebar)
3. Under **Build and deployment**:
   - Source: Select "GitHub Actions"
4. Push changes to the `main` branch
5. The workflow will automatically deploy your family tree
6. Visit `https://patruff.github.io/rufftree/` to see it live

**Automatic Updates**: Every time you push changes to `index.html` or `family_tree.json` on the main branch, GitHub Pages will automatically redeploy with your updates.

### Family Query System

Family members can ask questions about the family history, and you can answer them using the RAG system.

#### How It Works:

1. **Family Members Submit Questions**
   - Visit `queries.html` on the live site
   - Fill out the question form
   - Clicking "Submit" creates a GitHub Issue with their question

2. **You Answer Using RAG**
   ```bash
   # Set up environment
   export GOOGLE_GENAI_API_KEY=your_api_key

   # Answer a question interactively
   python answer_query.py --interactive

   # Or answer directly from command line
   python answer_query.py "When did the Ruff family immigrate to America?"
   ```

3. **Answer Appears on Website**
   - The script queries your RAG system
   - Saves the answer with citations to `stored_queries.json`
   - Push to `main` branch
   - Answer automatically appears on `queries.html`

#### Query Workflow:

```
Family member visits queries.html
        ↓
Submits question via form
        ↓
Creates GitHub Issue (you get notified)
        ↓
You run: python answer_query.py --interactive
        ↓
RAG system generates answer with citations
        ↓
Answer saved to stored_queries.json
        ↓
Push to main branch
        ↓
GitHub Pages updates
        ↓
Family member sees answer on queries.html
```

#### Stored Queries File:

`stored_queries.json` contains all Q&A pairs:

```json
{
  "queries": [
    {
      "id": "1",
      "question": "When did the Ruff family immigrate?",
      "answer": "According to family records...",
      "citations": ["Immigration Records - Ellis Island"],
      "askedBy": "Sarah Ruff",
      "date": "2025-01-10",
      "answeredBy": "RAG System"
    }
  ]
}
```

### Upload Documents Manually

```bash
# Set up environment
export GOOGLE_GENAI_API_KEY=your_api_key

# Upload a document
python test_file_search.py
# Set DOCUMENT_PATH environment variable to specify a file
export DOCUMENT_PATH=/path/to/your/document.pdf
python test_file_search.py
```

### Sync from Google Drive

```bash
# Set up environment
export GOOGLE_GENAI_API_KEY=your_api_key
export GOOGLE_DRIVE_CREDENTIALS='{"type":"service_account",...}'

# Run sync
python sync_drive_documents.py
```

This will:
1. Connect to your Google Drive
2. Find the "rufftree" folder
3. Download new documents (PDFs, Google Docs, etc.)
4. Upload them to the File Search store
5. Track synced files to avoid duplicates

### Query Documents

```bash
# Via test script
export QUERY="What documents are in the Ruff family archive?"
python test_file_search.py

# Or use the MCP server with Claude Desktop
# Just ask Claude questions about the Ruff family!
```

### MCP Tools

When using Claude Desktop, you'll have access to these tools:

1. **upload_ruff_document** - Upload a document to the RAG system
2. **query_ruff_documents** - Ask questions about the documents
3. **list_indexed_documents** - See all uploaded documents
4. **get_store_info** - View store configuration
5. **delete_document** - Remove a document from the system

## File Search Store

The Rufftree system uses a dedicated Google File Search store:

**Store Name**: `fileSearchStores/rufftreefamilydocuments-nrf1ymofronp`
**Display Name**: `rufftree-family-documents`

The store is automatically discovered by searching for 'rufftree' in the display name or store name. This ensures:

- Ruff family documents are kept separate from other projects
- Queries only search relevant Ruff family content
- No need to manage config files - the store is auto-discovered
- Workflows always find the same store

### Store Management

**List Store Contents**:
```bash
export GOOGLE_GENAI_API_KEY=your_api_key
python test_file_search.py
```

**Sync State**: `~/.rufftree_mcp/synced_files.json` (local tracking of synced files)

## Supported File Types

- **PDF**: `.pdf`
- **Microsoft Word**: `.docx`, `.doc`
- **Text**: `.txt`
- **Markdown**: `.md`
- **Google Docs**: Automatically exported as PDF

## Pricing

- **Storage**: FREE (unlimited)
- **Query embeddings**: FREE
- **Initial indexing**: $0.15 per 1M tokens (one-time cost)

**Example Cost**: A 20-page document (~10K tokens) costs approximately $0.0015 to index.

## Google Drive Folder Structure

```
Google Drive/
└── rufftree/                    # Main folder (share with service account)
    ├── Family History.pdf
    ├── Genealogy Records.docx
    ├── Photos Catalog.txt
    └── Stories and Memories      # Google Doc (auto-exported as PDF)
```

## Differences from longevitypdf

| Feature | longevitypdf | rufftree |
|---------|-------------|----------|
| **Folder Name** | "longevitypapers" | "rufftree" |
| **File Search Store** | Separate store | Separate store |
| **Config Path** | `~/.longevity_papers_mcp/` | `~/.rufftree_mcp/` |
| **Supported Files** | PDFs only | PDFs, DOCX, TXT, MD, Google Docs |
| **Purpose** | Scientific papers | Family documents |
| **MCP Server Name** | "longevity-papers-rag" | "rufftree-rag" |

## Troubleshooting

### Google Drive sync fails

- Verify service account email has access to the "rufftree" folder
- Check that `GOOGLE_DRIVE_CREDENTIALS` is valid JSON
- Ensure Google Drive API is enabled in your GCP project

### Documents not appearing in queries

- Wait 10-15 seconds after upload for indexing to complete
- Check document state with `list_indexed_documents` tool
- Verify the File Search store name matches in config

### API key errors

- Verify `GOOGLE_GENAI_API_KEY` is set correctly
- Check API key is enabled at https://aistudio.google.com/apikey
- Ensure you have quota remaining

## Contributing

This project is adapted from the longevitypdf RAG system. To contribute:

1. Test changes with `test_file_search.py`
2. Verify Google Drive sync works with `sync_drive_documents.py`
3. Test MCP integration with Claude Desktop

## License

MIT License - feel free to adapt for your own family archive projects!

## Resources

- [Gemini File Search Documentation](https://ai.google.dev/gemini-api/docs/file-search)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Google Drive API Documentation](https://developers.google.com/drive)
