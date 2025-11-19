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

### 🎨 Visualization & Exploration

- **Interactive Family Tree** ([index.html](https://patruff.github.io/rufftree/)): Beautiful expandable tree visualization
  - Click to expand/collapse family members and relationships
  - Visual indicators: Green for living, purple for deceased
  - Hover tooltips showing ethnicity breakdown
  - Real-time statistics: total members, living, deceased, and generations

- **Interactive Family Graph** ([graph.html](https://patruff.github.io/rufftree/graph.html)): Neo4j-style network visualization
  - Drag-and-drop nodes to arrange the family graph
  - Color-coded relationship edges (green: parent-child, pink: spouse, orange: sibling)
  - Click any person to view detailed info panel
  - Zoom, pan, and focus on specific family connections
  - Physics-based auto-layout for optimal positioning

### 👤 Family Data & Tracking

- **Generation Tracking**: Automatic generation labels and relative positioning
  - Labels: Greatest Generation, Silent Generation, Baby Boomer, Gen X, Millennial, Gen Z, Gen Alpha
  - `from_pat` field: Integer showing generations from Patrick Ruff (0 = Millennial baseline, -1 = Gen X, +1 = Gen Z, etc.)
  - Displayed in graph tooltips and info panels with human-readable distance text

- **Ethnicity Tracking**: Country-based ancestry breakdown
  - Percentage-based ethnicity (e.g., German: 34%, Irish: 32%, English: 18%)
  - Automatic calculation from parents (50% from each parent)
  - Supports 8+ countries: Chinese, English, French, German, Irish, Polish, Scottish, Welsh
  - Displayed in graph info panel and tree card tooltips

- **Health & Medical Tracking**: Comprehensive health data for all family members
  - **Health Conditions**: Track chronic/ongoing conditions (diabetes, heart disease, asthma, etc.) for living and deceased
  - **Cause of Death**: 50+ specific causes across 7 categories (Cancer, Cardiovascular, Respiratory, Neurological, etc.)
  - **Heritable Risk**: Auto-calculated genetic predisposition based on parents' conditions and causes of death
  - Risk levels: low, moderate, high, very-high with color-coded display
  - 40+ tracked conditions including cancers, heart disease, Alzheimer's, diabetes, and more

- **Location Tracking**: Track where family members live and are laid to rest
  - **Home Location**: `home_city` and `home_state` for all individuals (living and deceased)
  - **Cemetery Location**: `cemetery_name`, `cemetery_city`, and `cemetery_state` for deceased individuals
  - Displayed in graph info panels and tree tooltips

### 🛠️ Person Management

- **Person Generator** ([person_generator.html](https://patruff.github.io/rufftree/person_generator.html)): Modern web application for creating family profiles
  - **Ethnicity Input**: Dynamic form with add/remove country-percentage rows, real-time validation
  - **47 Positive Attributes**: Multi-select checkboxes (funny, smart, kind, fit, etc.)
  - **Big Five (OCEAN) Personality**: Sliders with smart auto-mapping from attributes
  - **Autocomplete Fields**: Occupation (100+ jobs) and location (100+ US cities)
  - **Structured Dropdowns**: Physical traits, education, life timeline, and more
  - **One-Click Export**: JSON download or clipboard copy for easy integration

- **Automated Integration**: GitHub Action workflow to integrate generated people into the family tree
- **Editable JSON Data**: Manually edit `family_tree.json` to update family members and relationships

### 💬 Query & Search System

- **Family Query System**: AI-powered Q&A with source citations
  - Family members submit questions via web form
  - RAG system provides answers with document citations
  - All Q&A stored and displayed on website

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

**Expandable Tree View** (`index.html`):
- Click on any person card to expand and reveal their spouse, siblings, parents, and children
- Click again to collapse the view
- Hover over cards to see ethnicity breakdown in tooltips
- View real-time statistics at the top of the page

**Interactive Graph View** (`graph.html`):
- Drag nodes to rearrange the family network
- Click any person to see their detailed information in the side panel
- Double-click to focus on a person and their immediate connections
- Use the control buttons to reset view, fit all nodes, or toggle physics
- Hover over nodes to see generation and age information
- Edge colors indicate relationship types:
  - **Green arrows**: Parent → Child relationships
  - **Pink lines**: Spouse connections
  - **Orange dashed lines**: Sibling relationships

### Adding Family Members

#### Using the Person Generator (Recommended)

The Person Generator is a beautiful, user-friendly web application designed to make it easy to create structured family member profiles. The interface features a modern gradient purple design with a clean, organized form layout.

**Accessing the Generator:**
- Visit `person_generator.html` on the live site at [https://patruff.github.io/rufftree/person_generator.html](https://patruff.github.io/rufftree/person_generator.html)
- Or open it locally in your browser

**UI Components:**

The form is organized into several sections with a two-column grid layout:

1. **Basic Information**
   - **First Name** (required): Text input field
   - **Last Name**: Text input, defaults to "Ruff"

2. **Physical Characteristics**
   - **Hair Color**: Dropdown with options (Blonde, Brunette, Redhead, Black, Gray, White, Bald)
   - **Height**: Dropdown (Short, Medium, Tall)

3. **Life Timeline**
   - **Decade Born**: Dropdown from 1900s to 2020s
   - **Year Born (exact)**: Number input for precise birth year (e.g., 1985)
   - **Status**: Dropdown (Alive/Deceased)
   - **Decade Deceased**: Only shown if status is "Deceased"
   - **Year Deceased (exact)**: Number input for precise death year
   - **Cause of Death**: Only shown if status is "Deceased"
     - 50+ options across 7 categories: Cancer, Cardiovascular, Respiratory, Neurological, Other Medical, Accidents & Injuries, General
     - Specific options like pancreatic cancer, heart attack, stroke, Alzheimer's, etc.
   - **Cemetery Information**: Only shown if status is "Deceased"
     - Cemetery Name, City, and State fields

4. **🏥 Health Conditions** (Optional)
   - **Chronic/Ongoing Health Conditions**: Multi-select dropdown for health conditions
   - Applies to both living and deceased individuals
   - 40+ conditions across 6 categories:
     - Cancer, Cardiovascular, Respiratory, Neurological, Metabolic & Endocrine, Other
   - Click "+" to add multiple conditions
   - Examples: diabetes, heart disease, asthma, high blood pressure, arthritis, depression

5. **Education & Career**
   - **Education Level**: Dropdown (Elementary, High School, Some College, College Degree, Master's, PhD)
   - **Occupation**: Autocomplete field with 100+ common occupations (Teacher, Engineer, Doctor, etc.) - type to search or select from dropdown

6. **Location**
   - **Home City**: City where person lives/lived
   - **Home State**: State where person lives/lived (accepts full names or abbreviations)
   - Applies to both living and deceased individuals

7. **🌍 Ethnicity** (Optional)
   - **Ancestry Breakdown**: Dynamic input for country-percentage pairs
   - Click **"+"** to add more countries to the breakdown
   - Click **"−"** to remove a country entry
   - Percentages must total exactly 100%
   - Real-time validation with visual feedback:
     - Green checkmark ✓ when total equals 100%
     - Red warning when total doesn't equal 100%
   - Examples:
     - Irish: 50%, German: 50%
     - Chinese: 100%
     - German: 34%, Irish: 32%, English: 18%, Scottish: 8%, Polish: 8%
   - **Note**: If parents are in the system, ethnicity will be automatically calculated (50% from each parent) when you add the person to the family tree

8. **✨ Positive Attributes**
   - Multi-select checkbox grid displaying 47 positive attributes
   - Attributes are displayed in a responsive grid with clean, rounded checkboxes
   - Click any attribute to select/deselect (multiple selections allowed)
   - Selected attributes get purple highlighting for visual feedback
   - Available attributes include:
     - **Personality**: Funny, Kind, Compassionate, Outgoing, Friendly, Charming, Charismatic, Witty, Cheerful
     - **Intelligence**: Smart, Intelligent, Creative, Curious
     - **Work Ethic**: Hardworking, Disciplined, Organized, Reliable, Clean
     - **Physical**: Fit, Athletic, Handsome, Pretty, Beautiful, Attractive, Stylish, Elegant
     - **Character**: Loyal, Honest, Generous, Humble, Brave, Courageous, Bold, Patient, Calm, Confident, Optimistic
     - **Social**: Caring, Supportive, Empathetic, Thoughtful, Polite, Respectful, Modest, Energetic
   - **Smart OCEAN Mapping**: Each attribute automatically maps to Big Five personality traits (see below)

9. **🧠 Personality (Big Five / OCEAN)**
   - Five interactive sliders (0-100 scale) with real-time value display
   - Each slider has purple gradient styling matching the app theme
   - **Openness (O)**: Imaginative, curious, open to new experiences
   - **Conscientiousness (C)**: Organized, responsible, dependable
   - **Extraversion (E)**: Outgoing, energetic, sociable
   - **Neuroticism (N)**: Emotional stability, calm vs. anxious
   - **Agreeableness (A)**: Kind, cooperative, trusting
   - **Priority System**:
     - If you manually adjust sliders, those values are used (slider values take priority)
     - If sliders remain at default (50) but attributes are selected, personality is auto-calculated from attribute mappings
     - This allows quick entry via attributes or precise control via sliders

10. **Notes**
   - Large text area for additional information, stories, or details

**Attribute-to-OCEAN Mapping Examples:**
- "Funny" → Extraversion: 70, Agreeableness: 65
- "Smart" → Openness: 75
- "Organized" → Conscientiousness: 80
- "Calm" → Neuroticism: 30 (lower = more calm)
- "Kind" → Agreeableness: 80
- "Confident" → Extraversion: 75, Neuroticism: 30

When multiple attributes are selected, the system averages the mapped values for each OCEAN trait to create a personality profile.

**Generating & Downloading:**

1. Fill out the form fields (only first name is required)
2. Select positive attributes by clicking checkboxes
3. Adjust personality sliders if you want precise control (optional)
4. Click the purple **"Generate Person"** button
5. Preview the generated JSON in the output section
6. Click **"Download JSON"** to save the file as `[firstname]_[timestamp].json`
7. Or click **"Copy to Clipboard"** to copy the JSON data

**Integration Workflow:**

1. Download the JSON file from the generator
2. Add the file to the `generated_people/` folder in the repository
3. Push to the repository or run the "Integrate Generated People" workflow
4. The person will be automatically added to `family_tree.json`

#### Manual Editing

1. Open `family_tree.json` in any text editor
2. Edit family member information (see **Family Data Model** section below for all available fields)
3. Save the file
4. Run utility scripts to recalculate auto-generated fields (optional):
   ```bash
   python3 add_generations.py        # Recalculate generation labels
   python3 add_ethnicity.py          # Recalculate ethnicity from parents
   python3 add_heritable_risk.py     # Recalculate health risk factors
   ```
5. Refresh the website to see changes

**Key Fields to Edit:**
- **Required**: `id`, `name`, `dob`, `dod`, relationship IDs
- **Location**: `home_city`, `home_state` (for all), `cemetery_name`, `cemetery_city`, `cemetery_state` (for deceased)
- **Health**: `health_condition` (array), `causeOfDeath` (for deceased)
- **Contact**: `occupation`, `phone`, `maidenName`, `notes`
- **Auto-calculated** (run scripts): `generation`, `from_pat`, `ethnicity`, `heritable_risk`, `heritable_traits`

See the **Family Data Model** section below for the complete list of all 30+ available fields with descriptions.

The tree displays:
- **Name** of each person
- **Lifespan** (birth year - death year or "Present")
- **Age** (current age or years lived)
- **Generation** label (e.g., "Millennial", "Gen Z")
- **Ethnicity** (on hover tooltip)
- **Visual indicators**: Green for living, purple for deceased
- **Statistics**: Total members, living, deceased, and generations

### Family Data Model

The `family_tree.json` file contains comprehensive data about each family member. Below are all available fields:

#### Core Identification Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | String | ✅ Yes | Unique identifier (e.g., "patrick", "joe_jr") |
| `name` | String | ✅ Yes | Full name of the person |
| `dob` | String | ✅ Yes | Birth year in YYYY format (e.g., "1985") |
| `dod` | String | ✅ Yes | Death year in YYYY format, or `"alive"` if living |

#### Relationship Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `spouseId` | String or null | ✅ Yes | ID of spouse, or `null` if no spouse |
| `parentIds` | Array | ✅ Yes | Array of parent IDs (usually 2, can be 0-2) |
| `siblingIds` | Array | ✅ Yes | Array of sibling IDs |
| `childrenIds` | Array | ✅ Yes | Array of children IDs |

#### Generation Fields (Auto-calculated)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `generation` | String | Auto | Generation label based on birth year<br>• Greatest Generation (≤1927)<br>• Silent Generation (1928-1945)<br>• Baby Boomer (1946-1964)<br>• Generation X (1965-1980)<br>• Millennial (1981-1996)<br>• Generation Z (1997-2012)<br>• Generation Alpha (2013+) |
| `from_pat` | Integer | Auto | Generational distance from Patrick Ruff<br>• Negative = before Patrick's generation (e.g., -2 for Boomers)<br>• 0 = Same generation as Patrick (Millennials)<br>• Positive = after Patrick's generation (e.g., +1 for Gen Z) |

#### Location Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `home_city` | String | Optional | City where person lives/lived (e.g., "Philadelphia") |
| `home_state` | String | Optional | State where person lives/lived (e.g., "Pennsylvania" or "PA") |
| `cemetery_name` | String | Optional | Cemetery name for deceased (e.g., "Oak Hill Cemetery") |
| `cemetery_city` | String | Optional | Cemetery city for deceased (e.g., "Philadelphia") |
| `cemetery_state` | String | Optional | Cemetery state for deceased (e.g., "Pennsylvania" or "PA") |

#### Ethnicity Field (Auto-calculated from parents)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ethnicity` | Object | Optional | Country-to-percentage mapping (must sum to 100%)<br>• Example: `{"German": 34, "Irish": 32, "English": 18}`<br>• Children inherit 50% from each parent<br>• Manually set for root ancestors |

#### Health & Medical Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `causeOfDeath` | String | Optional | Cause of death for deceased individuals<br>• Values: "heart-attack", "pancreatic-cancer", "stroke", etc.<br>• 50+ options across 7 categories (Cancer, Cardiovascular, Respiratory, Neurological, Other Medical, Accidents & Injuries, General) |
| `health_condition` | Array | Optional | Chronic/ongoing health conditions<br>• Values: ["diabetes", "heart-disease", "asthma"]<br>• Applies to both living and deceased<br>• 40+ conditions available |
| `heritable_risk` | Object | Auto | Genetic predisposition risk levels<br>• Auto-calculated from parents' `causeOfDeath` and `health_condition`<br>• Format: `{"heart-disease": "moderate", "diabetes": "high"}`<br>• Risk levels: "low", "moderate", "high", "very-high" |
| `heritable_traits` | Object | Auto | Genetic traits following Mendelian inheritance<br>• Auto-calculated from parents' genotypes<br>• Format: `{"eye_color": {"genotype": "Bb", "phenotype": "Brown"}}`<br>• Tracks: eye color (BB/Bb/bb), hair texture (CC/Cc/cc), dimples (DD/Dd/dd) |

#### Contact & Personal Information
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `occupation` | String | Optional | Job title or profession |
| `phone` | String | Optional | Contact phone number |
| `maidenName` | String | Optional | Maiden name for married individuals |
| `notes` | String | Optional | Additional information or family stories |
| `education` | String | Optional | Education level (e.g., "College Degree", "Master's") |

#### Physical Characteristics
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `hairColor` | String | Optional | Hair color (e.g., "Blonde", "Brunette", "Black") |
| `height` | String | Optional | Height category (e.g., "Tall", "Medium", "Short") |

#### Personality & Attributes (from Person Generator)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `attributes` | Array | Optional | Array of positive attributes (e.g., ["funny", "kind", "smart"])<br>• 47 available attributes |
| `personality` | Object | Optional | Big Five OCEAN personality traits<br>• Format: `{"openness": 75, "conscientiousness": 60, ...}`<br>• Values: 0-100 for each trait |

#### Example Complete Entry

```json
{
  "id": "patrick",
  "name": "Patrick Ruff",
  "dob": "1985",
  "dod": "alive",
  "generation": "Millennial",
  "from_pat": 0,
  "home_city": "Philadelphia",
  "home_state": "Pennsylvania",
  "ethnicity": {
    "German": 34,
    "Irish": 32,
    "English": 18,
    "Scottish": 8,
    "Polish": 8
  },
  "health_condition": ["asthma"],
  "heritable_risk": {
    "heart-disease": "moderate",
    "diabetes": "low"
  },
  "heritable_traits": {
    "eye_color": {
      "genotype": "bb",
      "phenotype": "Blue"
    },
    "hair_texture": {
      "genotype": "cc",
      "phenotype": "Straight"
    }
  },
  "occupation": "Developer/Scientist",
  "phone": "555-0123",
  "spouseId": "jenny",
  "parentIds": ["joe_sr", "debbie"],
  "siblingIds": ["joe_jr", "sarah", "phil"],
  "childrenIds": ["patrick_child1", "patrick_child2"]
}
```

#### Utility Scripts for Auto-Calculated Fields

After manually editing the JSON, run these scripts to update auto-calculated fields:

```bash
# Recalculate generation labels and from_pat for all family members
python3 add_generations.py

# Recalculate ethnicity from parents (edit root ethnicities in script first)
python3 add_ethnicity.py

# Recalculate heritable risk from parents' health conditions and causes of death
python3 add_heritable_risk.py

# Recalculate genetic traits from parents' genotypes (edit root genotypes in script first)
python3 add_heritable_traits.py
```

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
