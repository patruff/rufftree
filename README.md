# Rufftree RAG System

A Retrieval Augmented Generation (RAG) system for Ruff family documents using Google's Gemini File Search API. This system automatically syncs documents from a Google Drive folder and provides AI-powered search and question answering capabilities.

## 🆕 Recent Additions

### Recently Added People
- **Oliver Ruff** - Occupation unknown from Location unknown. Updated on December 10, 2025. _(Issue #75)_
- **Ocean Ruff** - Occupation unknown from Location unknown. Added on December 10, 2025. _(Issue #73)_

> **Total People in Family Tree:** 41

### Recent Family Stories
- **The Time Pat Won 4th In The State 800m** - Patrick Ruff. 2002. _(Issue #62)_
- **Dad built a rope swing** - Joe Ruff Sr.. Summer 1989. _(Issue #25)_

> **Total Stories in RAG:** 10
> **Total Stories in RAG:** 5
> **Total Stories in RAG:** _Pending automation_
> 💡 **Note**: This section automatically updates when new people or stories are added through the website.

## Table of Contents

- [View the Family Tree Online](#-view-the-family-tree-online)
- [Privacy & Repository Settings](#-privacy--repository-settings)
- [How It Works for Family Members](#-how-it-works-for-family-members)
- [Issue Types & Labels](#-issue-types--labels)
- [How Issues Get Resolved](#-how-issues-get-resolved)
- [Features](#features)
  - [Visualization & Exploration](#-visualization--exploration)
  - [Family Data & Tracking](#-family-data--tracking)
  - [Person Management](#️-person-management)
  - [Query & Search System](#-query--search-system)
- [Architecture](#architecture)
- [Setup](#setup)
- [Usage](#usage)
  - [View the Family Tree](#view-the-family-tree)
  - [Adding Family Members](#adding-family-members)
  - [Family Data Model](#family-data-model)
  - [Popular Queries](#popular-queries)
  - [Document Metadata & Filtering](#document-metadata--filtering)
  - [Known Limitations](#known-limitations)
- [GitHub Workflows](#github-workflows)
  - [Deploy Pages](#deploy-pages)
  - [Sync Documents from Google Drive](#sync-documents-from-google-drive)
  - [Query Ruff Documents](#query-ruff-documents)
  - [Add Story to RAG](#add-story-to-rag)
  - [List RAG Documents](#list-rag-documents)
  - [Integrate Generated People](#integrate-generated-people)
  - [Edit Person Information](#edit-person-information)
  - [Generate Person Tree to Drive](#generate-person-tree-to-drive)
  - [Analyze Data Coverage](#analyze-data-coverage)
  - [Process Family Story Issue](#process-family-story-issue)
  - [Process Add Person Issue](#process-add-person-issue)
- [Scripts Reference](#scripts-reference)
  - [Data Calculation Scripts](#data-calculation-scripts)
  - [Family Tree Query Scripts](#family-tree-query-scripts)
  - [RAG & Document Scripts](#rag--document-scripts)
- [File Search Store](#file-search-store)
- [Supported File Types](#supported-file-types)
- [Pricing](#pricing)
- [Troubleshooting](#troubleshooting)

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

## 👥 How It Works for Family Members

This system is designed so that **family members can participate** without needing technical knowledge or repository access.

### What Family Members Can Do

| Action | How | What Happens |
|--------|-----|--------------|
| **View the family tree** | Visit [the website](https://patruff.github.io/rufftree/) | See all family members and relationships |
| **Share a story or memory** | Create a [Story Issue](../../issues/new?template=family-story.yml) | Story is saved to the archive |
| **Ask about family history** | Create a [Query Issue](../../issues/new?template=family-query.yml) | Question is answered using RAG |
| **Request adding someone** | Create an [Add Person Issue](../../issues/new?template=add-person.yml) | Person is added to the tree |
| **Help identify someone** | Comment on a [Missing Person Issue](../../issues?q=label%3Amissing-person) | Help identify unknown people |

### What Only the Repo Owner Can Do

| Action | Description |
|--------|-------------|
| **Process issues** | Review and approve story/person submissions |
| **Kick off workflows** | Run GitHub Actions to modify data |
| **Add stories directly** | Use "Add Story to RAG" workflow for quick story entry |
| **View RAG documents** | Use "List RAG Documents" to see indexed files with dates |
| **Add documents to Google Drive** | Upload family documents for RAG |
| **Modify the family tree** | Make direct changes to `family_tree.json` |
| **Run RAG queries** | Execute queries against the document store |
| **Sync with Google Drive** | Trigger document synchronization (new docs only) |

### The Issue Workflow

```
Family Member                    Repo Owner                     System
     │                               │                             │
     │ Creates Issue                 │                             │
     │──────────────────────────────>│                             │
     │                               │                             │
     │                               │ Reviews & Labels Issue      │
     │                               │────────────────────────────>│
     │                               │                             │
     │                               │     Workflow Processes      │
     │                               │<────────────────────────────│
     │                               │                             │
     │      Issue Closed with        │                             │
     │<─────────Success Comment──────│                             │
     │                               │                             │
     │      See changes on website   │                             │
     │<──────────────────────────────│                             │
```

## 🏷️ Issue Types & Labels

Issues are color-coded by type and status to make the system easier to navigate.

### Issue Types

| Label | Color | Description | Template |
|-------|-------|-------------|----------|
| `family-story` | 🟣 Purple | A family story or memory | [Create Story](../../issues/new?template=family-story.yml) |
| `add-person` | 🔵 Blue | Add new person to tree | [Add Person](../../issues/new?template=add-person.yml) |
| `family-query` | 🟠 Orange | Question about family history | [Ask Question](../../issues/new?template=family-query.yml) |
| `missing-person` | 🔴 Red | Unknown person needs identification | [Identify Person](../../issues/new?template=missing-person.yml) |
| `documentation` | 🟢 Teal | Person needs more RAG documentation | Auto-created |

### Status Labels

| Label | Color | Meaning |
|-------|-------|---------|
| `story:pending` | Light Purple | Story submitted, awaiting processing |
| `story:processed` | Green | Story saved to archive |
| `person:pending` | Light Blue | Person addition awaiting processing |
| `person:added` | Green | Person added to tree |
| `query:pending` | Light Orange | Query awaiting answer |
| `query:answered` | Green | Query answered and saved |
| `needs-info` | Gray | More information needed |
| `awaiting-review` | Yellow | Awaiting repo owner review |

### Setting Up Labels

Labels need to be created in your repository. You can do this manually in **Settings > Labels**, or use the GitHub CLI:

```bash
# Import all labels from the configuration file
gh label import .github/labels.yml
```

## 📋 How Issues Get Resolved

### Stories

There are **two ways** to add stories to the system:

#### Option 1: Family Members Submit via Website (Fully Automatic)

The simplest way for family members to submit stories - just click a button!

1. **User visits** the website → "Submit Story" page
2. **Clicks** "Submit Your Story" button
3. **Fills out form** with title, who the story is about, and the story content
4. **Submits** - a GitHub issue is created with the `family-story` label
5. **Automatic processing** - the workflow triggers immediately, adds story to RAG, and closes the issue

No manual review needed - stories are processed automatically!

#### Option 2: Owner Adds Directly (For Quick Entry)

When the repo owner wants to quickly add a story:

1. Go to **Actions → "Add Story to RAG"**
2. Fill in: title, about, story content, author
3. Click "Run workflow"
4. Story is **immediately** added to:
   - **Google Docs** - Appended to shared "stories" document (human-readable archive)
   - **RAG File Search** - Uploaded as individual .docx file (machine searchable)
5. **Validation** - Workflow verifies the story was indexed correctly

**Where stories are stored:**

| Location | Purpose | Format |
|----------|---------|--------|
| Google Docs "stories" | Human-readable shared document | Google Doc |
| RAG File Search | AI-searchable index | Individual .docx files |

**How the RAG system organizes stories:**
- Each story is a separate file: `yyyymmdd_patstory_title.docx`
- Stories are immediately searchable after upload
- The shared "stories" Google Doc is **excluded** from sync (prevents duplicate indexing)
- Use **"List RAG Documents"** workflow to see all indexed stories

### Adding People to the Tree

When someone requests adding a person:

1. **Submit**: Create an add-person issue with the template
2. **Process**: Repo owner reviews and adds the `add-person` label
3. **Workflow runs**:
   - Person data is extracted from the issue
   - Relationships are set up bidirectionally
   - Person is added to `family_tree.json`
   - Calculation scripts run (generation, ethnicity, completion)
4. **Website updates**: GitHub Pages redeploys with the new person
5. **Close**: Issue is closed with a success summary

### Answering Queries

When someone asks about family history:

1. **Submit**: Create a query issue using the template
2. **Process**: Repo owner runs the RAG query system:
   ```bash
   python answer_query.py --interactive
   ```
3. **Answer saved**: Answer with citations is saved to `stored_queries.json`
4. **Website updates**: Answer appears on [queries.html](https://patruff.github.io/rufftree/queries.html)
5. **Close**: Issue is closed with the answer

### Identifying Unknown People

When a story mentions someone not in the tree:

1. **Auto-created**: The story workflow creates a "Who Is" issue
2. **Community help**: Family members comment with identification info
3. **Identified**: Once identified, create an add-person issue
4. **Close**: Original "Who Is" issue is closed

## Features

### 🎨 Visualization & Exploration

- **Interactive Family Tree** ([index.html](https://patruff.github.io/rufftree/)): Beautiful expandable tree visualization
  - Click to expand/collapse family members and relationships
  - Visual indicators: Green for living, purple for deceased
  - Hover tooltips showing ethnicity breakdown
  - **Ruff Family Summary**: Comprehensive generation breakdown with visual bar charts
    - Shows distribution across all generations (Greatest Generation through Generation Alpha)
    - Highlights final male/female lineages (Y chromosome and mtDNA tracking)
    - Real-time statistics: total members, living, deceased, visible, and genetic lineages

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

- **Genetic Lineage Tracking**: Track Y chromosome and mitochondrial DNA lineages
  - **Y Chromosome (Paternal Line)**: Identifies final males whose Y chromosome lineage ends (no male descendants)
  - **Mitochondrial DNA (Maternal Line)**: Identifies final females whose mtDNA lineage ends (no female descendants)
  - Auto-calculated based on descendant analysis
  - Highlighted in Ruff Family Summary with generation breakdowns
  - Shows which genetic lines are continuing vs. ending

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
- **Auto-calculated** (run scripts): `generation`, `from_pat`, `ethnicity`, `heritable_risk`, `heritable_traits`, `gender`, `y_chromosome_line`, `y_chromosome_final`, `mtdna_line`, `mtdna_final`, `rag_chunks`, `lacks_data`, `completion_percentage`

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
| `gender` | String | Auto | Gender of the person ("male" or "female")<br>• Auto-inferred from name if not specified<br>• Required for lineage calculations |
| `y_chromosome_line` | String | Auto | Y chromosome lineage name traced from root paternal ancestor<br>• Format: "[LastName] Y" (e.g., "Ruff Y", "Miller Y")<br>• Only assigned to males<br>• Allows tracking of unique paternal lines |
| `y_chromosome_final` | Boolean | Auto | True if this male is the last in his specific Y chromosome line<br>• Auto-calculated based on male descendants<br>• Indicates this specific ancestral Y chromosome lineage will end |
| `mtdna_line` | String | Auto | Mitochondrial DNA lineage name traced from root maternal ancestor<br>• Format: "[LastName] mtDNA" (e.g., "Miller mtDNA", "Ruff mtDNA")<br>• Only assigned to females<br>• Allows tracking of unique maternal lines |
| `mtdna_final` | Boolean | Auto | True if this female is the last in her specific mtDNA line<br>• Auto-calculated based on female descendants<br>• Indicates this specific ancestral mitochondrial DNA lineage will end |
| `rag_chunks` | Number | Auto | Number of RAG document chunks that mention this person<br>• Auto-calculated by querying the RAG system<br>• Higher values indicate more documentation available |
| `lacks_data` | Boolean | Auto | True if person has insufficient documentation in RAG system<br>• Auto-calculated: true when `rag_chunks` < 2<br>• Helps identify people needing more documentation |
| `completion_percentage` | Number | Auto | Profile completion percentage (0-100)<br>• Auto-calculated based on filled optional fields<br>• Categories: Excellent (≥80%), Good (60-79%), Fair (40-59%), Minimal (20-39%), Incomplete (<20%)<br>• Helps identify incomplete profiles |

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

# Track specific ancestral lineages - traces Y chromosome and mtDNA lines back to root ancestors
# Assigns line names (e.g., "Ruff Y", "Miller mtDNA") and identifies final carriers
python3 add_final_lineage.py

# Calculate profile completion percentage for each person
# Measures how many optional fields are filled vs total available fields
python3 calculate_completion.py
```

**What completion percentage tracks:**
- Location fields (home & cemetery)
- Contact fields (occupation, phone, maiden name, education)
- Health fields (conditions, cause of death)
- Physical fields (hair color, height)
- Personal fields (notes, attributes, personality)
- Relationships (spouse, parents, siblings, children)

**Categories:**
- Excellent (≥80%) - Well-rounded profile
- Good (60-79%) - Most key information filled
- Fair (40-59%) - Basic information present
- Minimal (20-39%) - Sparse information
- Incomplete (<20%) - Very limited information

#### Family Tree Query & Extraction Scripts

These scripts help you extract and view specific parts of the family tree:

```bash
# Get a person's immediate family tree (parents, siblings, spouse, children)
python3 get_person_tree.py "Patrick Ruff"

# Or run interactively (will prompt for name)
python3 get_person_tree.py

# Examples:
python3 get_person_tree.py "Jenny"        # Searches by partial name
python3 get_person_tree.py "Joe Ruff"     # Full name search
```

**What it does:**
- Searches for a person by name (flexible matching)
- Displays their parents, siblings, spouse, and children
- Shows ages, generations, and locations
- Optionally saves a focused JSON file with just that family subset
- Handles multiple matches by letting you choose

**Example Output:**
```
👤 PERSON:
   Patrick Ruff (1985 - Present (age 39)) - Millennial

👨‍👩 PARENTS (2):
   • Joe Ruff Sr. (1960 - Present (age 64)) - Baby Boomer
   • Debbie Ruff (1962 - Present (age 62)) - Baby Boomer

💑 SPOUSE:
   • Jenny Wang (1986 - Present (age 38)) - Millennial

👥 SIBLINGS (3):
   • Joe Ruff Jr. (1983 - Present (age 41)) - Millennial
   • Sarah Boilon (1987 - Present (age 37)) - Millennial
   • Phil Ruff (1990 - Present (age 34)) - Millennial

👶 CHILDREN (2):
   • Child 1 (name unknown) (2010 - Present (age 14)) - Generation Z
   • Child 2 (name unknown) (2012 - Present (age 12)) - Generation Z
```

#### GitHub Workflow: Edit Person Information

View and edit existing people's information in the family tree using GitHub Actions:

**How to Use:**

1. Go to **Actions** tab in your GitHub repository
2. Select "Edit Person Information" workflow
3. Click "Run workflow"
4. Enter the person's name (required)
5. Fill in any fields you want to update (all optional)
6. Click "Run workflow"

**Available fields:**
- Occupation
- Phone number
- Home city/state
- Date of death (year or "alive")
- Cemetery information (name, city, state)
- Health conditions (comma-separated)
- Notes/stories
- Maiden name
- Education level

**View-only mode:**
- Check "View only" to see all information without making changes
- Useful for reviewing what data exists for a person

**Examples:**

*View someone's information:*
- Person: `Patrick Ruff`
- View only: ✓ (checked)

*Update contact info:*
- Person: `Jenny Wang`
- Occupation: `Software Engineer`
- Phone: `555-1234`
- Home city: `Seattle`
- Home state: `Washington`

*Record a passing:*
- Person: `Joe Ruff Sr.`
- Date of death: `2023`
- Cemetery name: `Oak Hill Cemetery`
- Cemetery city: `Philadelphia`
- Cemetery state: `Pennsylvania`

**What happens:**
1. Script displays current information
2. Applies your updates
3. Commits changes to `family_tree.json`
4. Auto-pushes to repository

**Local usage:**

You can also run the script locally:
```bash
# View information only
python3 edit_person.py "Patrick Ruff" --view-only

# Update specific fields
python3 edit_person.py "Patrick Ruff" --occupation "Engineer" --phone "555-1234"

# Update multiple fields
python3 edit_person.py "Jenny Wang" \
  --home_city "Seattle" \
  --home_state "Washington" \
  --occupation "Software Engineer"

# Remove a field (set to "null")
python3 edit_person.py "Patrick Ruff" --phone "null"
```

#### GitHub Workflow: Generate Person Tree to Drive

Automatically generate a person's immediate family tree and save it to Google Drive using GitHub Actions:

**How to Use:**

1. Go to **Actions** tab in your GitHub repository
2. Select "Generate Person Family Tree to Drive" workflow
3. Click "Run workflow"
4. Enter the person's name (full or partial)
5. Click "Run workflow"

The workflow will:
- Search for the person in your family tree
- Extract their parents, siblings, spouse, and children
- Generate a timestamped JSON file
- Upload it to Google Drive folder: `rufftree_person_trees`

**Example inputs:**
- `Patrick Ruff` - Exact name match
- `Jenny` - Partial name (finds "Jenny Wang")
- `Joe Ruff` - Multiple matches will use the first one

**Output location:** All generated trees are saved to a Google Drive folder named `rufftree_person_trees` with filenames like:
- `patrick_ruff_family_tree_20241126_143022.json`

This is useful for:
- Sharing family connections with relatives
- Creating focused subsets of the tree
- Generating reports for specific people
- Backing up individual family units

#### GitHub Workflow: Analyze Data Coverage

Automatically analyze how well-documented each person is in the RAG system by counting document chunks that mention them:

**How it works:**

1. **Automatic Monthly Analysis** - Runs on the 1st of each month
2. **Manual Trigger** - Run anytime from Actions → "Analyze Family Tree Data Coverage"
3. **What it does:**
   - Queries the RAG system for each person in the family tree
   - Counts how many document chunks mention them
   - Sets `rag_chunks` field with the count
   - Sets `lacks_data` to `true` if count < 2 (threshold)
   - Creates detailed coverage report
   - Commits updated family_tree.json
   - Creates GitHub issue listing people who need more documentation

**Output:**
- **Updated family_tree.json** with `rag_chunks` and `lacks_data` fields
- **Artifact:** `data_coverage_report.json` with detailed statistics
- **GitHub Issue:** Lists people needing documentation (if any found)

**Viewing Results:**

The coverage data is displayed in the family tree visualizations:
- **index.html** - Shows coverage summary in "Ruff Family Summary" section
- **graph.html** - Shows coverage status when clicking on a person
  - ✅ Green = Well documented (2+ chunks)
  - ⚠️  Orange = Insufficient data (1 chunk)
  - ❌ Red = No documentation (0 chunks)

**Local Usage:**

You can also run the analysis locally:
```bash
export GOOGLE_GENAI_API_KEY=your_api_key
python3 analyze_data_coverage.py
```

This helps identify which family members need more stories, photos, or documents added to the `rufftree` Google Drive folder.

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

### Popular Queries

This section documents interesting or frequently asked questions about the family. These serve as examples of what you can ask the RAG system.

| Query | Result | Notes |
|-------|--------|-------|
| "Tell me about Joe and Final Fantasy 7" | Found that Joe enjoyed playing Final Fantasy 7, even playing for around 200 hours | Successfully found relevant story chunks from `20251128_patstory_joe_final_fantasy_7.docx` |
| "When did the Ruff family immigrate to America?" | Found immigration records from early 1900s | Good example of historical family research |
| "What occupations were common in the Ruff family?" | Found records of carpentry, teaching, small business | Shows how RAG aggregates from multiple documents |

**Tips for Good Queries:**
- Ask about specific people by name
- Ask about events, traditions, or memories
- Ask about relationships ("Who were Joe's siblings?")
- Ask about time periods ("What was happening in the 1980s?")

### Document Metadata & Filtering

Documents can include custom metadata that enables precise filtering during RAG queries. This solves attribution problems by allowing you to filter by author or subject before the semantic search even runs.

**Metadata Fields:**
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `author` | string | Who wrote the document | "Patrick Ruff" |
| `subject_of_story` | string | Who the document is about (one per subject) | "Joe Ruff" |
| `content_type` | string | Type of document | "story", "journal", "record" |
| `year` | numeric | Year the document was created | 2024 |

#### Automatic Metadata (Stories)

Stories uploaded through `add_story_to_drive.py` automatically include metadata:
- `author` - from the --author flag (default: Patrick Ruff)
- `subject_of_story` - from the --about flag (one entry per person mentioned)
- `content_type` - set to "story"

#### Configuring Metadata for Existing Documents

For documents synced from Google Drive (like `patrag.pdf`), configure metadata in `document_metadata.json`:

```json
{
  "documents": {
    "patrag.pdf": {
      "author": "Patrick Ruff",
      "content_type": "journal",
      "description": "Patrick's website posts and personal journal entries"
    },
    "family_history.pdf": {
      "author": "Debbie Ruff",
      "subject_of_story": ["Ruff Family", "Miller Family"],
      "content_type": "record"
    }
  }
}
```

When `sync_drive_documents.py` runs, it automatically applies this metadata to matching documents.

#### Re-uploading Documents with Metadata

For documents already in the File Search store without metadata, use the re-upload utility:

```bash
# Re-upload patrag.pdf using metadata from document_metadata.json
python reupload_with_metadata.py patrag.pdf

# Re-upload with explicit metadata
python reupload_with_metadata.py patrag.pdf --author "Patrick Ruff" --content-type journal

# Dry run (see what would happen)
python reupload_with_metadata.py patrag.pdf --dry-run

# List all documents in store
python reupload_with_metadata.py --list
```

This deletes the existing document and re-uploads it from Google Drive with the specified metadata.

#### Filtering Queries

Pre-filter documents before RAG search using the `metadata_filter` parameter:

```python
from test_file_search import query_documents

# Only search Patrick's writings (excludes stories ABOUT Patrick written by others)
query_documents(client, store_name, "What games did I play?",
                metadata_filter="author='Patrick Ruff'")

# Only search stories about Joe (excludes Patrick's journal entries)
query_documents(client, store_name, "What are Joe's favorite games?",
                metadata_filter="subject_of_story='Joe Ruff'")

# Combine filters (AND logic)
query_documents(client, store_name, "Tell me about Joe",
                metadata_filter="author='Patrick Ruff' AND subject_of_story='Joe Ruff'")

# Filter by content type
query_documents(client, store_name, "What did Patrick write about gaming?",
                metadata_filter="content_type='journal'")
```

**Filter Syntax:** Uses [AIP-160](https://google.aip.dev/160) list filter syntax.

#### Example: Solving the FF Tactics Attribution Problem

**Problem:** Query "Tell me about Joe and Final Fantasy" incorrectly attributed Patrick's journal entry about FF Tactics to Joe.

**Solution:** `patrag.pdf` is now configured with `author: "Patrick Ruff"` and `content_type: "journal"`. When querying:

```python
# To search only stories ABOUT Joe (excludes Patrick's unrelated journal entries)
query_documents(client, store_name, "Tell me about Joe and Final Fantasy",
                metadata_filter="subject_of_story='Joe Ruff'")
```

The journal entry about FF Tactics is excluded because it has no `subject_of_story` metadata - it's Patrick's personal journal, not a story about someone else.

### Known Limitations

#### Attribution in RAG Chunks (Mitigated)

**Issue:** RAG chunks are pure text extracts. When the model retrieves chunks, it may confuse who wrote what vs. who the story is about.

**Example Problem:**
- Query: "Tell me about Joe and Final Fantasy 7"
- RAG finds a story *about* Joe playing FF7 (correct)
- RAG also finds a journal entry *by* Patrick about Final Fantasy Tactics
- Response incorrectly attributes Patrick's words to Joe

**Solution - Metadata Filtering:**

Stories now include `author` and `subject_of_story` metadata. To avoid misattribution:

1. **Filter by subject**: `metadata_filter="subject_of_story='Joe Ruff'"` - only searches documents about Joe
2. **Filter by author**: `metadata_filter="author='Patrick Ruff'"` - only searches Patrick's writings
3. **Combine both**: Filter to Patrick's stories about Joe specifically

**Additional Best Practices:**
- Use third-person narrative: "Patrick recalls..." instead of "I..."
- Keep stories about different people in separate documents
- The metadata filter is applied *before* RAG search, so irrelevant documents are excluded entirely

**Note:** For more sophisticated entity tracking, consider GraphRAG or LightRAG which build knowledge graphs linking entities to their source contexts.

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

## GitHub Workflows

All GitHub Actions workflows can be found in `.github/workflows/`. Below is a summary of each workflow:

### Deploy Pages

**File:** `deploy-pages.yml`

Automatically deploys the family tree website to GitHub Pages whenever you push changes to the `main` branch.

**Triggers:**
- Push to `main` branch (changes to HTML, CSS, JS, or JSON files)

**What it does:**
- Builds and deploys `index.html`, `graph.html`, `queries.html`, `person_generator.html`
- Serves `family_tree.json` and `stored_queries.json`

### Sync Documents from Google Drive

**File:** `sync-drive-documents.yml`

Automatically syncs **NEW documents only** from your Google Drive "rufftree" folder to the RAG system.

**Triggers:**
- Scheduled: Every 6 hours
- Manual: Actions → "Sync Documents from Google Drive" → Run workflow

**Required Secrets:**
- `GOOGLE_GENAI_API_KEY` - Gemini API key
- `GOOGLE_DRIVE_CREDENTIALS` - Service account JSON

**What it does:**
- Connects to Google Drive
- Finds the "rufftree" folder
- **Only syncs NEW documents** - modified documents are NOT re-uploaded
- Tracks files by ID to prevent duplicates
- **Excludes "stories" document** - managed separately by Add Story workflow

**Important Notes:**
- The "stories" Google Doc is explicitly excluded (it's for human reading, not RAG)
- Individual stories are uploaded as separate .docx files via the Add Story workflow
- Modified documents keep the same file ID, so they won't be re-synced
- This prevents duplicate/conflicting versions in the RAG system

### Query Ruff Documents

**File:** `query-documents.yml`

Run RAG queries directly from GitHub Actions - useful for testing or quick lookups without local setup.

**Triggers:**
- Manual only: Actions → "Query Ruff Documents" → Run workflow

**Inputs:**
- **query** (required): Question to ask about Ruff family documents
- **model** (optional): Choose between `gemini-2.5-flash` (default) or `gemini-2.5-pro`

**Required Secrets:**
- `GOOGLE_GENAI_API_KEY` - Gemini API key

**Example:**
1. Go to Actions → "Query Ruff Documents"
2. Click "Run workflow"
3. Enter: "When did the Ruff family immigrate to America?"
4. Select model (default: gemini-2.5-flash)
5. View answer in workflow run output

### Add Story to RAG

**File:** `add-story-to-drive.yml`

**(Repo Owner Only)** Quickly add a story directly to the RAG File Search store with automatic validation.

**Triggers:**
- Manual only: Actions → "Add Story to RAG" → Run workflow

**Inputs:**
- **title** (required): Story title
- **about** (required): Who the story is about (comma-separated names)
- **story** (required): The story content (use `\n` for line breaks)
- **author** (optional): Author name (default: Patrick Ruff)

**Required Secrets:**
- `GOOGLE_GENAI_API_KEY` - Gemini API key
- `GOOGLE_DRIVE_CREDENTIALS` - Service account JSON (for Google Docs append)

**What it does:**
1. **Appends to Google Docs** - Story is added to the shared "stories" document in Google Drive (human-readable archive)
2. **Uploads to File Search** - Creates a Word document (.docx) named `yyyymmdd_patstory_title.docx` and uploads to RAG
3. **Validates indexing** - Waits 10 seconds then verifies:
   - ✅ Document appears in store listing
   - ✅ Story is searchable via test query
4. **Reports results** - Shows validation status in workflow summary

**Example:**
1. Go to Actions → "Add Story to RAG"
2. Click "Run workflow"
3. Fill in:
   - Title: `The Christmas Cookie Tradition`
   - About: `Debbie Ruff, Sarah Boilon`
   - Story: `Every Christmas Eve, Debbie would bake...\n\nThe recipe had been passed down...`
4. Run workflow
5. Check summary for validation results!

This is the fastest way for the repo owner to add stories directly to the RAG system - bypasses Google Drive sync entirely.

### List RAG Documents

**File:** `list-rag-documents.yml`

**(Repo Owner Only)** View all documents currently indexed in the File Search store.

**Triggers:**
- Manual only: Actions → "List RAG Documents" → Run workflow

**Inputs:**
- **show_details** (optional): Show detailed info like size, state, and document ID (default: true)

**What it does:**
- Lists all indexed documents sorted by upload date (newest first)
- Shows document name, upload date/time, and size
- Calculates total storage and estimated token count
- Creates a summary table in the workflow output

**Use this to:**
- See what documents are in the RAG system
- Verify a new story was indexed after upload
- Check when documents were added
- Monitor the size of your document index

### Integrate Generated People

**File:** `integrate-people.yml`

Automatically integrates new people from the `generated_people/` folder into the family tree.

**Triggers:**
- Push to `main` branch with changes in `generated_people/*.json`
- Manual: Actions → "Integrate Generated People" → Run workflow

**What it does:**
- Scans `generated_people/` folder for JSON files
- Adds each person to `family_tree.json`
- Moves processed files to `generated_people/processed/`
- Commits and pushes the updated family tree

**Workflow:**
1. Use the Person Generator to create a family member
2. Download the JSON file
3. Add it to `generated_people/` folder
4. Push to repository (or run workflow manually)
5. Person is automatically added to the family tree

### Edit Person Information

**File:** `edit-person.yml`

View and edit existing people's information in the family tree.

**Triggers:**
- Manual: Actions → "Edit Person Information" → Run workflow

**Inputs:**
- **person** (required): Name of the person to edit
- **view_only**: Check to view information without making changes
- **occupation**, **phone**, **home_city**, **home_state**, etc.: Fields to update

**Examples:**

*View someone's information:*
- Person: `Patrick Ruff`
- View only: ✓

*Update contact info:*
- Person: `Jenny Wang`
- Occupation: `Software Engineer`
- Home city: `Seattle`

### Generate Person Tree to Drive

**File:** `generate-person-tree.yml`

Generate a person's immediate family tree and save it to Google Drive.

**Triggers:**
- Manual: Actions → "Generate Person Family Tree to Drive" → Run workflow

**Inputs:**
- **person_name** (required): Full or partial name

**What it does:**
- Extracts parents, siblings, spouse, and children
- Generates timestamped JSON file
- Uploads to Google Drive folder: `rufftree_person_trees`

### Analyze Data Coverage

**File:** `analyze-data-coverage.yml`

Analyze how well-documented each person is in the RAG system.

**Triggers:**
- Scheduled: 1st of each month
- Manual: Actions → "Analyze Family Tree Data Coverage" → Run workflow

**What it does:**
- Queries RAG system for each person
- Counts document chunks mentioning them
- Sets `rag_chunks` and `lacks_data` fields
- Creates coverage report artifact
- Opens GitHub issue listing people needing documentation

### Process Family Story Issue

**File:** `process-story-issue.yml`

Automatically processes family story submissions from GitHub Issues.

**Triggers:**
- When the `family-story` label is added to an issue

**What it does:**
1. Extracts story content and metadata from the issue
2. Checks mentioned people against the family tree
3. Creates "Who Is" issues for unknown people
4. Saves story to `family_stories/` folder
5. Updates the stories index
6. Updates labels (`story:pending` → `story:processed`)
7. Closes issue with success comment

**Labels Used:**
- `family-story` - Triggers the workflow
- `story:pending` - Initial status (from template)
- `story:processed` - Set when complete
- `missing-person` - Created for unknown people

**Output:**
- `family_stories/{title}_{date}.txt` - The story file
- `family_stories/index.json` - Updated index with metadata

### Process Add Person Issue

**File:** `process-person-issue.yml`

Automatically adds new people to the family tree from GitHub Issues.

**Triggers:**
- When the `add-person` label is added to an issue

**What it does:**
1. Extracts person data from issue (form fields or JSON block)
2. Generates unique ID if not provided
3. Sets up bidirectional relationships
4. Adds person to `family_tree.json`
5. Runs calculation scripts (generation, ethnicity, completion)
6. Updates labels (`person:pending` → `person:added`)
7. Closes issue with success comment

**Labels Used:**
- `add-person` - Triggers the workflow
- `person:pending` - Initial status (from template)
- `person:added` - Set when complete

**Supported Input Formats:**
1. **Form Fields**: Fill out the issue template form
2. **JSON Block**: Paste person JSON from Person Generator

**Automatic Relationship Setup:**
- "Child of" - Sets parentIds, updates parent's childrenIds
- "Parent of" - Sets childrenIds, updates child's parentIds
- "Spouse of" - Sets spouseId bidirectionally, copies children
- "Sibling of" - Sets siblingIds, copies parentIds, updates all siblings

## Scripts Reference

### Data Calculation Scripts

These scripts update auto-calculated fields in `family_tree.json`:

| Script | Description |
|--------|-------------|
| `add_generations.py` | Calculate generation labels (Baby Boomer, Gen X, Millennial, etc.) and `from_pat` distance |
| `add_ethnicity.py` | Calculate ethnicity from parents (50% each). Edit root ethnicities in script first |
| `add_heritable_risk.py` | Calculate genetic health risk from parents' conditions and causes of death |
| `add_heritable_traits.py` | Calculate Mendelian traits (eye color, etc.) from parents' genotypes |
| `add_final_lineage.py` | Track Y chromosome and mtDNA lineages, identify final carriers |
| `calculate_completion.py` | Calculate profile completion percentage for each person |

**Usage:**
```bash
python3 add_generations.py        # Run after adding new people
python3 add_ethnicity.py          # Run after updating parent relationships
python3 add_heritable_risk.py     # Run after updating health conditions
python3 add_heritable_traits.py   # Run after updating root genotypes
python3 add_final_lineage.py      # Run after updating family structure
python3 calculate_completion.py   # Run to update completion stats
```

### Family Tree Query Scripts

| Script | Description |
|--------|-------------|
| `get_person_tree.py` | Extract a person's immediate family (parents, siblings, spouse, children) |
| `edit_person.py` | View or update a person's information |
| `generate_person_tree_to_drive.py` | Generate family tree JSON and upload to Google Drive |

**Usage:**
```bash
# Get someone's family tree
python3 get_person_tree.py "Patrick Ruff"

# View person info
python3 edit_person.py "Patrick Ruff" --view-only

# Edit person info
python3 edit_person.py "Patrick Ruff" --occupation "Engineer" --phone "555-1234"
```

### RAG & Document Scripts

| Script | Description |
|--------|-------------|
| `mcp_server.py` | MCP server for Claude Desktop integration |
| `sync_drive_documents.py` | Sync **new** documents from Google Drive to RAG with metadata |
| `add_story_to_drive.py` | Add stories to Google Docs AND RAG File Search with metadata |
| `reupload_with_metadata.py` | Re-upload existing documents with new metadata |
| `test_file_search.py` | Test uploads, queries (with metadata filter), and list documents |
| `answer_query.py` | Answer family questions using RAG with citations |
| `analyze_data_coverage.py` | Analyze RAG coverage for each family member |
| `document_metadata.json` | Configuration file for document metadata (author, subject, etc.) |

**Usage:**
```bash
# Sync NEW documents from Google Drive with metadata
python3 sync_drive_documents.py

# Add a story directly to Google Docs + RAG (auto-adds metadata)
python3 add_story_to_drive.py --title "Story Title" --about "Person Name" --story "Story content..."

# Re-upload a document with metadata (for existing docs)
python3 reupload_with_metadata.py patrag.pdf

# List all indexed documents in RAG
python3 test_file_search.py  # Shows documents in output

# Test a RAG query with metadata filter
export QUERY="What did Patrick write about gaming?"
python3 test_file_search.py

# Answer a question and save to stored_queries.json
python3 answer_query.py --interactive

# Analyze data coverage
python3 analyze_data_coverage.py
```

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
