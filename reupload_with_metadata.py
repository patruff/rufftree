#!/usr/bin/env python3
"""
Re-upload Document with Metadata

This utility deletes an existing document from the File Search store and re-uploads
it with custom metadata. This is useful for adding metadata to documents that were
uploaded before metadata support was added.

Usage:
    # Re-upload patrag.pdf with metadata from document_metadata.json
    python reupload_with_metadata.py patrag.pdf

    # Re-upload with explicit metadata
    python reupload_with_metadata.py patrag.pdf --author "Patrick Ruff" --content-type journal

    # List all documents in store (to see what can be re-uploaded)
    python reupload_with_metadata.py --list

    # Dry run (show what would happen without making changes)
    python reupload_with_metadata.py patrag.pdf --dry-run
"""

import os
import sys
import json
import argparse
from pathlib import Path

from test_file_search import get_client, get_or_create_store, upload_document, list_documents
from sync_drive_documents import load_metadata_config, get_document_metadata, get_drive_service, find_folder, download_file, DRIVE_FOLDER_NAME


def find_document_in_store(client, store_name, doc_name):
    """Find a document in the store by display name (case-insensitive)."""
    try:
        docs = list(client.file_search_stores.documents.list(parent=store_name))
        doc_name_lower = doc_name.lower()

        for doc in docs:
            display_name = getattr(doc, 'display_name', '') or ''
            if display_name.lower() == doc_name_lower:
                return doc
        return None
    except Exception as e:
        print(f"❌ Error searching for document: {e}")
        return None


def delete_document(client, doc_name):
    """Delete a document from the File Search store by its resource name."""
    try:
        client.file_search_stores.documents.delete(name=doc_name)
        print(f"🗑️  Deleted document: {doc_name}")
        return True
    except Exception as e:
        print(f"❌ Error deleting document: {e}")
        return False


def find_file_in_drive(drive_service, folder_id, filename):
    """Find a file in the Google Drive folder by name."""
    query = f"'{folder_id}' in parents and name='{filename}' and trashed=false"

    results = drive_service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType, size)'
    ).execute()

    files = results.get('files', [])
    return files[0] if files else None


def reupload_document(doc_name, custom_metadata=None, dry_run=False):
    """
    Re-upload a document with metadata.

    1. Find the document in File Search store
    2. Delete it from the store
    3. Download from Google Drive
    4. Re-upload with metadata
    """
    print(f"🔄 Re-uploading document: {doc_name}")
    print("=" * 60)

    # Initialize clients
    print("\n📦 Initializing File Search...")
    fs_client = get_client()
    store_name = get_or_create_store(fs_client)

    # Find document in store
    print(f"\n🔍 Searching for '{doc_name}' in File Search store...")
    existing_doc = find_document_in_store(fs_client, store_name, doc_name)

    if not existing_doc:
        print(f"❌ Document '{doc_name}' not found in File Search store")
        print("\nAvailable documents:")
        list_documents(fs_client, store_name)
        return False

    print(f"✅ Found document: {existing_doc.name}")
    display_name = getattr(existing_doc, 'display_name', doc_name)

    # Load metadata if not provided
    if custom_metadata is None:
        print("\n📋 Loading metadata from document_metadata.json...")
        config = load_metadata_config()
        custom_metadata = get_document_metadata(config, display_name)

        if custom_metadata:
            print(f"✅ Found metadata configuration for '{display_name}'")
        else:
            print(f"⚠️  No metadata configured for '{display_name}'")
            print("   Add it to document_metadata.json or provide --author/--content-type flags")

    if custom_metadata:
        print(f"\n📋 Metadata to apply:")
        for meta in custom_metadata:
            key = meta.get('key', 'unknown')
            value = meta.get('string_value') or meta.get('numeric_value', 'unknown')
            print(f"   - {key}: {value}")

    if dry_run:
        print("\n🔍 DRY RUN - No changes will be made")
        return True

    # Initialize Google Drive to get the file
    print("\n📡 Connecting to Google Drive...")
    try:
        drive_service = get_drive_service()
        folder_id = find_folder(drive_service, DRIVE_FOLDER_NAME)
    except Exception as e:
        print(f"❌ Error connecting to Google Drive: {e}")
        print("   Make sure GOOGLE_DRIVE_CREDENTIALS is set")
        return False

    # Find the file in Drive
    print(f"\n🔍 Looking for '{doc_name}' in Google Drive...")
    # Try exact name first
    drive_file = find_file_in_drive(drive_service, folder_id, doc_name)

    # If not found and name ends with .pdf, try without extension (for Google Docs)
    if not drive_file and doc_name.endswith('.pdf'):
        base_name = doc_name[:-4]
        drive_file = find_file_in_drive(drive_service, folder_id, base_name)

    if not drive_file:
        print(f"❌ File '{doc_name}' not found in Google Drive folder '{DRIVE_FOLDER_NAME}'")
        return False

    print(f"✅ Found in Drive: {drive_file['name']} (ID: {drive_file['id']})")

    # Delete from File Search store
    print(f"\n🗑️  Deleting '{display_name}' from File Search store...")
    if not delete_document(fs_client, existing_doc.name):
        return False

    # Download from Drive
    print(f"\n📥 Downloading from Google Drive...")
    temp_dir = Path("/tmp/rufftree_reupload")
    temp_dir.mkdir(exist_ok=True)

    temp_path = download_file(
        drive_service,
        drive_file['id'],
        drive_file['name'],
        drive_file['mimeType'],
        temp_dir
    )

    # Re-upload with metadata
    print(f"\n📤 Re-uploading to File Search with metadata...")
    try:
        upload_document(fs_client, store_name, str(temp_path), custom_metadata=custom_metadata)
        print(f"\n✅ Successfully re-uploaded '{display_name}' with metadata!")
    except Exception as e:
        print(f"❌ Error re-uploading: {e}")
        return False
    finally:
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Re-upload a document to File Search with custom metadata'
    )
    parser.add_argument('document', nargs='?', help='Document name to re-upload (e.g., patrag.pdf)')
    parser.add_argument('--list', action='store_true', help='List all documents in the store')
    parser.add_argument('--dry-run', action='store_true', help='Show what would happen without making changes')
    parser.add_argument('--author', help='Set author metadata')
    parser.add_argument('--content-type', help='Set content type metadata (e.g., journal, story, record)')
    parser.add_argument('--subject', action='append', help='Add subject_of_story metadata (can be repeated)')

    args = parser.parse_args()

    if args.list:
        print("📚 Listing documents in File Search store...\n")
        client = get_client()
        store_name = get_or_create_store(client)
        list_documents(client, store_name)
        return

    if not args.document:
        parser.error("Please specify a document name or use --list")

    # Build custom metadata from command line args
    custom_metadata = None
    if args.author or args.content_type or args.subject:
        custom_metadata = []
        if args.author:
            custom_metadata.append({"key": "author", "string_value": args.author})
        if args.content_type:
            custom_metadata.append({"key": "content_type", "string_value": args.content_type})
        if args.subject:
            for subj in args.subject:
                custom_metadata.append({"key": "subject_of_story", "string_value": subj})

    success = reupload_document(args.document, custom_metadata, dry_run=args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
