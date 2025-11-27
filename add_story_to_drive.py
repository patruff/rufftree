#!/usr/bin/env python3
"""
Add Story to Google Drive and RAG System

Creates a Google Doc in Google Drive AND uploads to the Gemini File Search
store for RAG indexing.

Uses the Google Docs API to create native Google Docs (not upload .docx files)
which avoids service account storage quota issues.

Usage:
    python add_story_to_drive.py --title "Story Title" --about "Patrick Ruff, Jenny Wang" --story "Story content..."
"""

import os
import sys
import json
import argparse
import tempfile
from datetime import datetime
from pathlib import Path
from io import BytesIO

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Import our existing file search functions
from test_file_search import get_client, get_or_create_store, upload_document


# Configuration
DRIVE_FOLDER_NAME = "rufftree"
# Need drive scope to create files in shared folders
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents'
]


def get_google_services():
    """Initialize Google Drive and Docs API services."""
    creds_json = os.getenv("GOOGLE_DRIVE_CREDENTIALS")

    if not creds_json:
        raise ValueError(
            "GOOGLE_DRIVE_CREDENTIALS environment variable not set. "
            "This should contain your service account JSON credentials."
        )

    try:
        creds_info = json.loads(creds_json)
        service_account_email = creds_info.get('client_email', 'unknown')
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in GOOGLE_DRIVE_CREDENTIALS: {e}")

    credentials = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=SCOPES
    )

    drive_service = build('drive', 'v3', credentials=credentials)
    docs_service = build('docs', 'v1', credentials=credentials)

    print("✅ Connected to Google APIs")
    print(f"   Service Account: {service_account_email}")

    return drive_service, docs_service, service_account_email


def find_folder(service, folder_name: str, service_account_email: str) -> str:
    """Find the rufftree folder that was shared with the service account."""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, owners)',
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()

    files = results.get('files', [])

    if not files:
        print(f"\n❌ ERROR: Folder '{folder_name}' not found!")
        print(f"\n📋 To fix this, you need to:")
        print(f"   1. Go to your Google Drive (drive.google.com)")
        print(f"   2. Create a folder named '{folder_name}'")
        print(f"   3. Right-click the folder → Share")
        print(f"   4. Add this email with 'Editor' access:")
        print(f"      {service_account_email}")
        print(f"   5. Click 'Share'")
        print(f"\n   Then run this workflow again.")
        raise ValueError(f"Folder '{folder_name}' not found. See instructions above.")

    folder_id = files[0]['id']
    print(f"📁 Found folder: {folder_name} (ID: {folder_id})")
    return folder_id


def generate_filename(title: str) -> str:
    """Generate filename: yyyymmdd_patstory_title"""
    date_str = datetime.now().strftime("%Y%m%d")
    safe_title = "".join(c if c.isalnum() or c in ' -_' else '' for c in title)
    safe_title = safe_title.strip().replace(' ', '_').lower()[:50]
    return f"{date_str}_patstory_{safe_title}"


def create_google_doc(drive_service, docs_service, folder_id: str, title: str,
                      about: str, story: str, author: str) -> tuple:
    """Create a Google Doc in the specified folder."""

    doc_title = generate_filename(title)

    # Step 1: Create empty Google Doc in the folder
    file_metadata = {
        'name': doc_title,
        'mimeType': 'application/vnd.google-apps.document',
        'parents': [folder_id]
    }

    doc_file = drive_service.files().create(
        body=file_metadata,
        fields='id, webViewLink',
        supportsAllDrives=True
    ).execute()

    doc_id = doc_file.get('id')
    web_link = doc_file.get('webViewLink', '')

    print(f"   Created Google Doc: {doc_title}")
    print(f"   Doc ID: {doc_id}")

    # Step 2: Populate the document with content
    date_str = datetime.now().strftime("%B %d, %Y")
    word_count = len(story.split())

    # Build the document content using Docs API
    requests = [
        # Title
        {
            'insertText': {
                'location': {'index': 1},
                'text': f"{title}\n\n"
            }
        },
        # Metadata
        {
            'insertText': {
                'location': {'index': 1 + len(title) + 2},
                'text': f"By: {author}\nAbout: {about}\nDate: {date_str}\n\n{'─' * 50}\n\n"
            }
        },
    ]

    # Calculate where to insert story content
    meta_text = f"By: {author}\nAbout: {about}\nDate: {date_str}\n\n{'─' * 50}\n\n"
    story_start = 1 + len(title) + 2 + len(meta_text)

    # Add story content
    requests.append({
        'insertText': {
            'location': {'index': story_start},
            'text': f"{story}\n\n{'─' * 50}\n\nWord Count: {word_count}"
        }
    })

    # Apply formatting - make title larger
    title_end = 1 + len(title)
    requests.append({
        'updateParagraphStyle': {
            'range': {'startIndex': 1, 'endIndex': title_end},
            'paragraphStyle': {
                'namedStyleType': 'HEADING_1',
                'alignment': 'CENTER'
            },
            'fields': 'namedStyleType,alignment'
        }
    })

    # Execute the batch update
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()

    print(f"   ✅ Document content added")
    if web_link:
        print(f"   🔗 Link: {web_link}")

    return doc_id, doc_title, web_link


def create_docx_for_rag(title: str, about: str, story: str, author: str) -> BytesIO:
    """Create a Word document for RAG indexing."""
    doc = Document()

    title_para = doc.add_heading(title, level=0)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()
    meta_para = doc.add_paragraph()
    meta_para.add_run("By: ").bold = True
    meta_para.add_run(author)

    meta_para2 = doc.add_paragraph()
    meta_para2.add_run("About: ").bold = True
    meta_para2.add_run(about)

    meta_para3 = doc.add_paragraph()
    meta_para3.add_run("Date: ").bold = True
    meta_para3.add_run(datetime.now().strftime("%B %d, %Y"))

    doc.add_paragraph("─" * 50)
    doc.add_paragraph()

    story_paragraphs = story.strip().split('\n\n')
    for para_text in story_paragraphs:
        if para_text.strip():
            p = doc.add_paragraph(para_text.strip())
            p.paragraph_format.space_after = Pt(12)

    doc.add_paragraph()
    doc.add_paragraph("─" * 50)
    footer = doc.add_paragraph()
    footer.add_run(f"Word Count: {len(story.split())}").italic = True

    docx_buffer = BytesIO()
    doc.save(docx_buffer)
    docx_buffer.seek(0)

    return docx_buffer


def add_story(title: str, about: str, story: str, author: str = "Patrick Ruff"):
    """Main function to create story in Google Drive AND RAG system."""
    print("📖 Adding Story to Google Drive & RAG System")
    print("=" * 60)
    print(f"Title: {title}")
    print(f"About: {about}")
    print(f"Author: {author}")
    print(f"Word Count: {len(story.split())}")
    print("=" * 60)

    # === Part 1: Create Google Doc in Drive ===
    print("\n📄 STEP 1: Creating Google Doc in Drive...")

    drive_service, docs_service, service_account_email = get_google_services()
    folder_id = find_folder(drive_service, DRIVE_FOLDER_NAME, service_account_email)

    doc_id, doc_title, web_link = create_google_doc(
        drive_service, docs_service, folder_id, title, about, story, author
    )

    # === Part 2: Upload to File Search Store for RAG ===
    print("\n🔍 STEP 2: Adding to RAG File Search store...")

    docx_buffer = create_docx_for_rag(title, about, story, author)
    filename = f"{doc_title}.docx"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / filename
        with open(temp_path, 'wb') as f:
            f.write(docx_buffer.getvalue())

        print("   Connecting to Gemini File Search...")
        client = get_client()
        store_name = get_or_create_store(client)
        upload_document(client, store_name, str(temp_path))

    # === Summary ===
    print("\n" + "=" * 60)
    print("✅ STORY ADDED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📄 Google Doc: {doc_title}")
    if web_link:
        print(f"🔗 View: {web_link}")
    print(f"🔍 RAG: Indexed in File Search store")
    print("=" * 60)

    return doc_id, filename


def main():
    parser = argparse.ArgumentParser(description='Add a family story to Google Drive and RAG')
    parser.add_argument('--title', '-t', help='Story title')
    parser.add_argument('--about', '-a', help='Who the story is about (comma-separated names)')
    parser.add_argument('--story', '-s', help='Story content')
    parser.add_argument('--author', default='Patrick Ruff', help='Story author (default: Patrick Ruff)')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')

    args = parser.parse_args()

    if args.interactive:
        print("📖 Add Family Story")
        print("=" * 60)
        title = input("\nStory Title: ").strip()
        about = input("Who is this story about? (comma-separated): ").strip()
        author = input("Your name (press Enter for 'Patrick Ruff'): ").strip() or "Patrick Ruff"
        print("\nEnter your story (end with two empty lines):")
        lines = []
        empty_count = 0
        while True:
            try:
                line = input()
                if line == "":
                    empty_count += 1
                    if empty_count >= 2:
                        break
                    lines.append(line)
                else:
                    empty_count = 0
                    lines.append(line)
            except EOFError:
                break
        story = "\n".join(lines).strip()
    else:
        if not args.title or not args.about or not args.story:
            parser.error("--title, --about, and --story are required (or use --interactive)")

        title = args.title
        about = args.about
        story = args.story
        author = args.author

    if not title or not about or not story:
        print("❌ Error: Title, about, and story content are required")
        sys.exit(1)

    try:
        add_story(title, about, story, author)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
