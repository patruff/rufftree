#!/usr/bin/env python3
"""
Add Story to Google Drive

Creates a .docx document from story text and uploads it to the rufftree
Google Drive folder for RAG indexing.

Usage:
    python add_story_to_drive.py --title "Story Title" --about "Patrick Ruff, Jenny Wang" --story "Story content..."

    Or interactively:
    python add_story_to_drive.py --interactive
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from io import BytesIO

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


# Configuration
DRIVE_FOLDER_NAME = "rufftree"
SCOPES = ['https://www.googleapis.com/auth/drive.file']  # Write access to files created by the app


def get_drive_service():
    """Initialize Google Drive API service with write access."""
    creds_json = os.getenv("GOOGLE_DRIVE_CREDENTIALS")

    if not creds_json:
        raise ValueError(
            "GOOGLE_DRIVE_CREDENTIALS environment variable not set. "
            "This should contain your service account JSON credentials."
        )

    try:
        creds_info = json.loads(creds_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in GOOGLE_DRIVE_CREDENTIALS: {e}")

    credentials = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=SCOPES
    )

    service = build('drive', 'v3', credentials=credentials)
    print("✅ Connected to Google Drive API")

    return service


def find_or_create_folder(service, folder_name: str) -> str:
    """Find the rufftree folder or create it if it doesn't exist."""
    # Search for existing folder
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)'
    ).execute()

    files = results.get('files', [])

    if files:
        folder_id = files[0]['id']
        print(f"📁 Found folder: {folder_name} (ID: {folder_id})")
        return folder_id

    # Create the folder if it doesn't exist
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    folder = service.files().create(
        body=file_metadata,
        fields='id'
    ).execute()

    folder_id = folder.get('id')
    print(f"📁 Created folder: {folder_name} (ID: {folder_id})")

    return folder_id


def create_story_docx(title: str, about: str, story: str, author: str = "Patrick Ruff") -> BytesIO:
    """Create a Word document with the story content."""
    doc = Document()

    # Title
    title_para = doc.add_heading(title, level=0)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Metadata section
    doc.add_paragraph()
    meta_para = doc.add_paragraph()
    meta_para.add_run(f"By: ").bold = True
    meta_para.add_run(author)

    meta_para2 = doc.add_paragraph()
    meta_para2.add_run(f"About: ").bold = True
    meta_para2.add_run(about)

    meta_para3 = doc.add_paragraph()
    meta_para3.add_run(f"Date: ").bold = True
    meta_para3.add_run(datetime.now().strftime("%B %d, %Y"))

    # Separator
    doc.add_paragraph("─" * 50)

    # Story content
    doc.add_paragraph()
    story_paragraphs = story.strip().split('\n\n')
    for para_text in story_paragraphs:
        if para_text.strip():
            p = doc.add_paragraph(para_text.strip())
            p.paragraph_format.space_after = Pt(12)

    # Footer
    doc.add_paragraph()
    doc.add_paragraph("─" * 50)
    footer = doc.add_paragraph()
    footer.add_run(f"Word Count: {len(story.split())}").italic = True

    # Save to BytesIO
    docx_buffer = BytesIO()
    doc.save(docx_buffer)
    docx_buffer.seek(0)

    return docx_buffer


def generate_filename(title: str) -> str:
    """Generate filename: yyyymmdd_patstory_title.docx"""
    date_str = datetime.now().strftime("%Y%m%d")
    # Clean title for filename
    safe_title = "".join(c if c.isalnum() or c in ' -_' else '' for c in title)
    safe_title = safe_title.strip().replace(' ', '_').lower()[:50]

    return f"{date_str}_patstory_{safe_title}.docx"


def upload_to_drive(service, folder_id: str, filename: str, docx_buffer: BytesIO) -> str:
    """Upload the .docx file to Google Drive."""
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }

    media = MediaIoBaseUpload(
        docx_buffer,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        resumable=True
    )

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    file_id = file.get('id')
    web_link = file.get('webViewLink', '')

    print(f"✅ Uploaded: {filename}")
    print(f"   File ID: {file_id}")
    if web_link:
        print(f"   Link: {web_link}")

    return file_id


def add_story(title: str, about: str, story: str, author: str = "Patrick Ruff"):
    """Main function to create and upload a story to Google Drive."""
    print("📖 Adding Story to Google Drive")
    print("=" * 60)
    print(f"Title: {title}")
    print(f"About: {about}")
    print(f"Author: {author}")
    print(f"Word Count: {len(story.split())}")
    print("=" * 60)

    # Connect to Google Drive
    print("\n📡 Connecting to Google Drive...")
    service = get_drive_service()

    # Find or create the rufftree folder
    folder_id = find_or_create_folder(service, DRIVE_FOLDER_NAME)

    # Create the document
    print("\n📝 Creating Word document...")
    docx_buffer = create_story_docx(title, about, story, author)

    # Generate filename
    filename = generate_filename(title)
    print(f"   Filename: {filename}")

    # Upload to Drive
    print("\n📤 Uploading to Google Drive...")
    file_id = upload_to_drive(service, folder_id, filename, docx_buffer)

    print("\n" + "=" * 60)
    print("✅ STORY ADDED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📁 Location: Google Drive / {DRIVE_FOLDER_NAME} / {filename}")
    print(f"🔄 The story will be indexed on the next sync (every 6 hours)")
    print(f"   Or manually trigger: Actions → 'Sync Documents from Google Drive'")
    print("=" * 60)

    return file_id, filename


def main():
    parser = argparse.ArgumentParser(description='Add a family story to Google Drive')
    parser.add_argument('--title', '-t', help='Story title')
    parser.add_argument('--about', '-a', help='Who the story is about (comma-separated names)')
    parser.add_argument('--story', '-s', help='Story content')
    parser.add_argument('--author', default='Patrick Ruff', help='Story author (default: Patrick Ruff)')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')

    args = parser.parse_args()

    if args.interactive:
        print("📖 Add Family Story to Google Drive")
        print("=" * 60)
        title = input("\nStory Title: ").strip()
        about = input("Who is this story about? (comma-separated): ").strip()
        author = input("Your name (press Enter for 'Patrick Ruff'): ").strip() or "Patrick Ruff"
        print("\nEnter your story (end with an empty line):")
        lines = []
        while True:
            try:
                line = input()
                if line == "":
                    if lines and lines[-1] == "":
                        break  # Two empty lines = done
                    lines.append(line)
                else:
                    lines.append(line)
            except EOFError:
                break
        story = "\n".join(lines).strip()
    else:
        # Check required args
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
