#!/usr/bin/env python3
"""
Add Story to RAG System

Creates a .docx document from story text and uploads it directly to the
Gemini File Search store for RAG indexing. This bypasses Google Drive
entirely, avoiding service account storage quota issues.

Usage:
    python add_story_to_drive.py --title "Story Title" --about "Patrick Ruff, Jenny Wang" --story "Story content..."

    Or interactively:
    python add_story_to_drive.py --interactive
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

# Import our existing file search functions
from test_file_search import get_client, get_or_create_store, upload_document


def create_story_docx(title: str, about: str, story: str, author: str = "Patrick Ruff") -> BytesIO:
    """Create a Word document with the story content."""
    doc = Document()

    # Title
    title_para = doc.add_heading(title, level=0)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Metadata section
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


def add_story(title: str, about: str, story: str, author: str = "Patrick Ruff"):
    """Main function to create and upload a story directly to RAG."""
    print("📖 Adding Story to RAG System")
    print("=" * 60)
    print(f"Title: {title}")
    print(f"About: {about}")
    print(f"Author: {author}")
    print(f"Word Count: {len(story.split())}")
    print("=" * 60)

    # Create the document
    print("\n📝 Creating Word document...")
    docx_buffer = create_story_docx(title, about, story, author)

    # Generate filename
    filename = generate_filename(title)
    print(f"   Filename: {filename}")

    # Save to temporary file (required for upload_document)
    print("\n📤 Uploading directly to File Search store...")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / filename
        with open(temp_path, 'wb') as f:
            f.write(docx_buffer.getvalue())

        # Initialize File Search client
        print("   Connecting to Gemini File Search...")
        client = get_client()
        store_name = get_or_create_store(client)

        # Upload to File Search store
        upload_document(client, store_name, str(temp_path))

    print("\n" + "=" * 60)
    print("✅ STORY ADDED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📁 File: {filename}")
    print(f"📦 Store: {store_name}")
    print(f"🔍 The story is now searchable via RAG queries!")
    print("=" * 60)

    return filename


def main():
    parser = argparse.ArgumentParser(description='Add a family story to the RAG system')
    parser.add_argument('--title', '-t', help='Story title')
    parser.add_argument('--about', '-a', help='Who the story is about (comma-separated names)')
    parser.add_argument('--story', '-s', help='Story content')
    parser.add_argument('--author', default='Patrick Ruff', help='Story author (default: Patrick Ruff)')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')

    args = parser.parse_args()

    if args.interactive:
        print("📖 Add Family Story to RAG System")
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
