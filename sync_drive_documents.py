#!/usr/bin/env python3
"""
Sync Documents from Google Drive to File Search Store

Automatically checks the "rufftree" Google Drive folder for NEW documents only
(PDFs, Google Docs, DOCX, TXT) and uploads them to the Google File Search RAG system.

IMPORTANT: This script only syncs NEW documents, never modified ones.
- Documents are tracked by file_id, so modifications don't trigger re-upload
- The "stories" doc is excluded (managed separately by add_story_to_drive.py)
- Individual stories are uploaded as separate DOCX files to File Search
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Set, Dict, List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Import our existing file search functions
from test_file_search import get_client, get_or_create_store, upload_document, list_documents


# Configuration
DRIVE_FOLDER_NAME = "rufftree"
STATE_FILE = Path.home() / ".rufftree_mcp" / "synced_files.json"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Documents to exclude from sync (managed separately)
# The "stories" doc is appended to by add_story_to_drive.py and individual stories
# are uploaded to File Search separately - we don't want to re-sync the whole doc
EXCLUDED_DOCUMENTS = {
    'stories',  # Managed by add_story_to_drive.py
}

# Supported file types
SUPPORTED_MIME_TYPES = {
    'application/pdf': '.pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'application/msword': '.doc',
    'text/plain': '.txt',
    'text/markdown': '.md',
    # Google Docs will be exported as PDF
    'application/vnd.google-apps.document': '.pdf',
}


def get_drive_service():
    """Initialize Google Drive API service using service account credentials."""
    creds_json = os.getenv("GOOGLE_DRIVE_CREDENTIALS")

    if not creds_json:
        raise ValueError(
            "GOOGLE_DRIVE_CREDENTIALS environment variable not set. "
            "This should contain your service account JSON credentials."
        )

    # Parse credentials from JSON string
    try:
        creds_info = json.loads(creds_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in GOOGLE_DRIVE_CREDENTIALS: {e}")

    # Create credentials from service account info
    credentials = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=SCOPES
    )

    # Build Drive API service
    service = build('drive', 'v3', credentials=credentials)
    print("✅ Connected to Google Drive API")

    return service


def find_folder(service, folder_name: str) -> str:
    """Find a folder by name and return its ID."""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)'
    ).execute()

    files = results.get('files', [])

    if not files:
        raise ValueError(f"Folder '{folder_name}' not found in Google Drive")

    if len(files) > 1:
        print(f"⚠️  Warning: Multiple folders named '{folder_name}' found. Using the first one.")

    folder_id = files[0]['id']
    print(f"📁 Found folder: {folder_name} (ID: {folder_id})")

    return folder_id


def list_documents_in_folder(service, folder_id: str) -> List[Dict[str, str]]:
    """List all supported document files in a Google Drive folder."""
    # Build query for all supported MIME types
    mime_conditions = " or ".join([f"mimeType='{mime}'" for mime in SUPPORTED_MIME_TYPES.keys()])
    query = f"'{folder_id}' in parents and ({mime_conditions}) and trashed=false"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType, size, modifiedTime)',
        orderBy='modifiedTime desc'
    ).execute()

    files = results.get('files', [])

    print(f"📄 Found {len(files)} document(s) in Google Drive folder")

    return files


def download_file(service, file_id: str, file_name: str, mime_type: str, temp_dir: Path) -> Path:
    """
    Download a file from Google Drive to a temporary directory.
    For Google Docs, export as PDF.
    """
    # Determine the file extension
    extension = SUPPORTED_MIME_TYPES.get(mime_type, '.pdf')

    # Clean filename and add extension if needed
    if not file_name.endswith(extension):
        # If it's a Google Doc, strip the original name and add .pdf
        if mime_type == 'application/vnd.google-apps.document':
            temp_path = temp_dir / f"{file_name}{extension}"
        else:
            temp_path = temp_dir / file_name
    else:
        temp_path = temp_dir / file_name

    # For Google Docs, use export instead of get_media
    if mime_type == 'application/vnd.google-apps.document':
        request = service.files().export_media(
            fileId=file_id,
            mimeType='application/pdf'
        )
        print(f"  📄 Exporting Google Doc as PDF...")
    else:
        request = service.files().get_media(fileId=file_id)

    with io.FileIO(str(temp_path), 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"  📥 Downloading: {progress}%", end='\r')

    print(f"  ✅ Downloaded: {temp_path.name}")
    return temp_path


def load_synced_files() -> Dict[str, str]:
    """Load the record of already synced files."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load synced files state: {e}")
            return {}
    return {}


def save_synced_files(synced_files: Dict[str, str]):
    """Save the record of synced files."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(synced_files, f, indent=2)
    print(f"💾 Saved sync state to {STATE_FILE}")


def get_indexed_document_names(client, store_name):
    """Get list of document display names already indexed in File Search store."""
    try:
        docs = list(client.file_search_stores.documents.list(parent=store_name))
        names = set()
        print(f"   Indexed documents in store:")
        for doc in docs:
            doc_display = getattr(doc, 'display_name', '') or ''
            if doc_display:
                # Store both with and without extension for matching
                names.add(doc_display.lower())
                # Also add without extension
                if doc_display.endswith('.pdf'):
                    names.add(doc_display[:-4].lower())
                print(f"      - {doc_display}")
        return names
    except Exception as e:
        print(f"⚠️  Could not list indexed documents: {e}")
        import traceback
        traceback.print_exc()
        return set()


def sync_documents():
    """Main sync function - check Drive folder and upload new documents."""
    print("🔄 Starting Google Drive → File Search sync...")
    print("=" * 80)

    # Initialize Google Drive service
    print("\n📡 Connecting to Google Drive...")
    drive_service = get_drive_service()

    # Find the rufftree folder
    folder_id = find_folder(drive_service, DRIVE_FOLDER_NAME)

    # List documents in the folder
    drive_docs = list_documents_in_folder(drive_service, folder_id)

    if not drive_docs:
        print("\nℹ️  No documents found in Google Drive folder")
        return

    # Initialize File Search client early to check what's already indexed
    print("\n📦 Initializing File Search...")
    fs_client = get_client()
    store_name = get_or_create_store(fs_client)

    # Get documents already indexed in File Search store
    print("\n🔍 Checking documents already indexed in File Search store...")
    indexed_names = get_indexed_document_names(fs_client, store_name)
    print(f"   Found {len(indexed_names)} document(s) already indexed")

    # Load previously synced files (local state)
    synced_files = load_synced_files()
    print(f"📋 Local sync state: {len(synced_files)} file(s)")

    # Identify NEW files only - we never re-upload modified documents
    # Modified documents keep the same file_id, so they'll be skipped
    new_files = []
    skipped_already_synced = []
    skipped_already_indexed = []
    skipped_excluded = []

    for doc in drive_docs:
        file_id = doc['id']
        doc_name = doc['name']
        doc_name_lower = doc_name.lower()

        # Skip excluded documents (e.g., "stories" which is managed separately)
        if doc_name_lower in EXCLUDED_DOCUMENTS or doc_name in EXCLUDED_DOCUMENTS:
            skipped_excluded.append(doc_name)
            continue

        # Skip if already in local sync state (includes previously synced docs that may have been modified)
        if file_id in synced_files:
            skipped_already_synced.append(doc_name)
            continue

        # Skip if already indexed in File Search store (prevents re-upload after state loss)
        if doc_name_lower in indexed_names:
            skipped_already_indexed.append(doc_name)
            # Update local state to reflect it's synced
            synced_files[file_id] = {
                'name': doc_name,
                'mime_type': doc['mimeType'],
                'synced_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'size': doc.get('size', 0),
                'note': 'Already indexed in File Search store'
            }
            continue

        new_files.append(doc)

    # Log what we're skipping
    if skipped_excluded:
        print(f"\n🚫 Excluding {len(skipped_excluded)} document(s) (managed separately):")
        for name in skipped_excluded:
            print(f"   - {name}")

    if skipped_already_synced:
        print(f"\n⏭️  Skipping {len(skipped_already_synced)} previously synced document(s) (won't re-upload modified docs)")

    if skipped_already_indexed:
        print(f"\n⏭️  Skipping {len(skipped_already_indexed)} document(s) already in File Search store:")
        for name in skipped_already_indexed:
            print(f"   - {name}")

    if not new_files:
        print("\n✅ All documents are already synced. Nothing to do!")
        if skipped_already_indexed:
            # Save updated sync state
            save_synced_files(synced_files)
        return

    print(f"\n🆕 Found {len(new_files)} new document(s) to upload:")
    for doc in new_files:
        size_mb = int(doc.get('size', 0)) / (1024 * 1024) if doc.get('size') else 0
        doc_type = "Google Doc" if doc['mimeType'] == 'application/vnd.google-apps.document' else doc['mimeType'].split('/')[-1].upper()
        print(f"  - {doc['name']} ({doc_type}, {size_mb:.2f} MB)" if size_mb > 0 else f"  - {doc['name']} ({doc_type})")

    # Create temp directory for downloads
    temp_dir = Path("/tmp/rufftree_sync")
    temp_dir.mkdir(exist_ok=True)

    # Process each new file
    print(f"\n🚀 Uploading {len(new_files)} new document(s) to File Search...")
    print("=" * 80)

    success_count = 0
    for i, doc in enumerate(new_files, 1):
        file_id = doc['id']
        file_name = doc['name']
        mime_type = doc['mimeType']

        print(f"\n[{i}/{len(new_files)}] Processing: {file_name}")

        try:
            # Download from Drive (or export if Google Doc)
            temp_path = download_file(drive_service, file_id, file_name, mime_type, temp_dir)

            # Upload to File Search
            print(f"  📤 Uploading to File Search...")
            upload_document(fs_client, store_name, str(temp_path))

            # Mark as synced
            synced_files[file_id] = {
                'name': file_name,
                'mime_type': mime_type,
                'synced_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'size': doc.get('size', 0)
            }

            # Clean up temp file
            temp_path.unlink()

            success_count += 1
            print(f"  ✅ Successfully synced: {file_name}")

        except Exception as e:
            print(f"  ❌ Error syncing {file_name}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Save updated sync state
    save_synced_files(synced_files)

    # Summary
    print("\n" + "=" * 80)
    print("📊 SYNC SUMMARY")
    print("=" * 80)
    print(f"✅ Successfully synced: {success_count}/{len(new_files)} document(s)")
    print(f"📦 File Search Store: {store_name}")
    print(f"📁 Google Drive Folder: {DRIVE_FOLDER_NAME}")
    print(f"💾 Sync State File: {STATE_FILE}")
    print("=" * 80)

    if success_count > 0:
        print("\n🎉 New documents are now available for querying!")

    return success_count


def main():
    """Entry point for the sync script."""
    try:
        sync_documents()
    except Exception as e:
        print(f"\n❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
