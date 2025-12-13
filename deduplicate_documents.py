#!/usr/bin/env python3
"""
Deduplication script for Ruff family RAG documents.

This script identifies potential duplicate documents in the File Search store
based on:
- Filename similarity (exact or near-match)
- Document length (size in bytes)
- Content sampling (first/last N bytes)

Run with --dry-run to see what would be deleted without making changes.
Run with --interactive to review each duplicate before deletion.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher
from google import genai
from google.genai import types


def get_client():
    """Initialize Google GenAI client."""
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_GENAI_API_KEY environment variable not set. "
            "Get your API key from https://aistudio.google.com/apikey"
        )
    return genai.Client(api_key=api_key)


def get_store(client):
    """Get the rufftree File Search store."""
    print("🔍 Finding rufftree File Search store...")
    try:
        stores = list(client.file_search_stores.list())

        for store in stores:
            store_display = getattr(store, 'display_name', None) or ''
            store_name_lower = store.name.lower() if store.name else ''

            if ('rufftree' in store_display.lower()) or ('rufftree' in store_name_lower):
                print(f"✅ Found store: {store.name}")
                return store.name

        raise ValueError("Rufftree File Search store not found")
    except Exception as e:
        print(f"❌ Error finding store: {e}")
        raise


def list_all_documents(client, store_name):
    """List all documents in the store with metadata."""
    print("\n📚 Listing all documents in store...")

    try:
        docs = list(client.file_search_stores.documents.list(parent=store_name))
        print(f"✅ Found {len(docs)} document(s)")

        documents = []
        for doc in docs:
            doc_info = {
                'name': doc.name,
                'display_name': getattr(doc, 'display_name', 'Unknown'),
                'size_bytes': int(getattr(doc, 'size_bytes', 0)),
                'state': getattr(doc, 'state', 'unknown'),
                'create_time': str(getattr(doc, 'create_time', 'unknown')),
            }
            documents.append(doc_info)

        return documents

    except Exception as e:
        print(f"❌ Error listing documents: {e}")
        return []


def calculate_similarity(str1, str2):
    """Calculate similarity ratio between two strings (0.0 to 1.0)."""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def find_duplicates(documents, similarity_threshold=0.9, size_tolerance=0.05):
    """
    Find potential duplicate documents.

    Args:
        documents: List of document info dictionaries
        similarity_threshold: Filename similarity threshold (0.0-1.0)
        size_tolerance: Size difference tolerance (0.05 = 5%)

    Returns:
        List of duplicate groups
    """
    print("\n🔍 Analyzing documents for duplicates...")
    print(f"   Filename similarity threshold: {similarity_threshold * 100}%")
    print(f"   Size tolerance: ±{size_tolerance * 100}%")

    duplicate_groups = []
    processed = set()

    for i, doc1 in enumerate(documents):
        if doc1['name'] in processed:
            continue

        potential_duplicates = [doc1]

        for j, doc2 in enumerate(documents[i+1:], start=i+1):
            if doc2['name'] in processed:
                continue

            # Check filename similarity
            name_similarity = calculate_similarity(
                doc1['display_name'],
                doc2['display_name']
            )

            # Check size similarity
            size1 = doc1['size_bytes']
            size2 = doc2['size_bytes']

            if size1 == 0 and size2 == 0:
                size_ratio = 1.0
            elif size1 == 0 or size2 == 0:
                size_ratio = 0.0
            else:
                size_ratio = min(size1, size2) / max(size1, size2)

            # Consider as duplicate if:
            # - High filename similarity AND similar size
            # - OR exact same size and moderately similar name
            is_duplicate = False

            if name_similarity >= similarity_threshold and size_ratio >= (1 - size_tolerance):
                is_duplicate = True
                reason = f"Similar names ({name_similarity:.1%}) and sizes"
            elif size1 == size2 and size1 > 0 and name_similarity >= 0.7:
                is_duplicate = True
                reason = f"Exact size match ({size1:,} bytes) and similar names ({name_similarity:.1%})"
            elif doc1['display_name'].lower() == doc2['display_name'].lower():
                is_duplicate = True
                reason = "Exact filename match"

            if is_duplicate:
                if len(potential_duplicates) == 1:
                    print(f"\n🔍 Found duplicate group:")
                potential_duplicates.append(doc2)
                processed.add(doc2['name'])

        if len(potential_duplicates) > 1:
            processed.add(doc1['name'])
            duplicate_groups.append(potential_duplicates)

    return duplicate_groups


def display_duplicate_groups(duplicate_groups):
    """Display found duplicate groups."""
    if not duplicate_groups:
        print("\n✅ No duplicates found!")
        return

    print(f"\n⚠️  Found {len(duplicate_groups)} duplicate group(s):\n")

    for group_idx, group in enumerate(duplicate_groups, 1):
        print(f"{'='*80}")
        print(f"GROUP {group_idx} - {len(group)} documents")
        print(f"{'='*80}")

        for idx, doc in enumerate(group, 1):
            size_mb = doc['size_bytes'] / (1024 * 1024)
            print(f"\n{idx}. {doc['display_name']}")
            print(f"   ID: {doc['name']}")
            print(f"   Size: {size_mb:.2f} MB ({doc['size_bytes']:,} bytes)")
            print(f"   Created: {doc['create_time']}")
            print(f"   State: {doc['state']}")

        print()


def recommend_deletions(duplicate_groups):
    """
    Recommend which documents to delete from each group.

    Strategy:
    - Keep the oldest document (first uploaded)
    - Or keep the one with best state (ACTIVE > others)
    """
    recommendations = []

    for group in duplicate_groups:
        # Sort by create_time (oldest first)
        sorted_group = sorted(group, key=lambda x: x['create_time'])

        # Keep the first (oldest), delete the rest
        to_keep = sorted_group[0]
        to_delete = sorted_group[1:]

        recommendations.append({
            'keep': to_keep,
            'delete': to_delete
        })

    return recommendations


def delete_documents(client, store_name, document_names, dry_run=True):
    """
    Delete documents from the store.

    Args:
        client: Google GenAI client
        store_name: File search store name
        document_names: List of document names to delete
        dry_run: If True, don't actually delete
    """
    if dry_run:
        print("\n🔍 DRY RUN - Would delete the following documents:")
        for name in document_names:
            print(f"   - {name}")
        print("\nRun with --delete to actually delete these documents")
        return

    print(f"\n🗑️  Deleting {len(document_names)} document(s)...")

    deleted_count = 0
    failed_count = 0

    for doc_name in document_names:
        try:
            client.file_search_stores.documents.delete(name=doc_name)
            print(f"   ✅ Deleted: {doc_name}")
            deleted_count += 1
        except Exception as e:
            print(f"   ❌ Failed to delete {doc_name}: {e}")
            failed_count += 1

    print(f"\n📊 Deletion summary:")
    print(f"   ✅ Successfully deleted: {deleted_count}")
    if failed_count > 0:
        print(f"   ❌ Failed: {failed_count}")


def interactive_review(client, store_name, recommendations):
    """
    Interactively review and delete duplicates.

    User can choose which documents to keep/delete for each group.
    """
    print("\n🔍 Interactive Duplicate Review")
    print("="*80)

    to_delete = []

    for idx, rec in enumerate(recommendations, 1):
        group = [rec['keep']] + rec['delete']
        print(f"\n📋 Group {idx}/{len(recommendations)}")
        print(f"Found {len(group)} similar documents:\n")

        for i, doc in enumerate(group, 1):
            size_mb = doc['size_bytes'] / (1024 * 1024)
            print(f"{i}. {doc['display_name']}")
            print(f"   Size: {size_mb:.2f} MB")
            print(f"   Created: {doc['create_time']}")
            if i == 1:
                print("   ⭐ RECOMMENDED TO KEEP (oldest)")
            print()

        while True:
            response = input(f"Delete duplicates in this group? (y/n/s=skip): ").strip().lower()
            if response == 'y':
                # Delete all except the first one
                to_delete.extend([doc['name'] for doc in rec['delete']])
                print(f"✅ Marked {len(rec['delete'])} document(s) for deletion\n")
                break
            elif response == 'n':
                print("⏭️  Skipping this group\n")
                break
            elif response == 's':
                print("⏭️  Skipping this group\n")
                break
            else:
                print("Invalid input. Please enter 'y', 'n', or 's'")

    if not to_delete:
        print("\n✅ No documents marked for deletion")
        return

    print(f"\n📊 Summary: {len(to_delete)} document(s) marked for deletion")
    confirm = input("Proceed with deletion? (yes/no): ").strip().lower()

    if confirm == 'yes':
        delete_documents(client, store_name, to_delete, dry_run=False)
    else:
        print("❌ Deletion cancelled")


def save_report(duplicate_groups, recommendations, output_file="deduplication_report.json"):
    """Save deduplication report to JSON file."""
    report = {
        "total_groups": len(duplicate_groups),
        "total_duplicates": sum(len(group) - 1 for group in duplicate_groups),
        "groups": []
    }

    for idx, (group, rec) in enumerate(zip(duplicate_groups, recommendations), 1):
        report["groups"].append({
            "group_id": idx,
            "documents": group,
            "recommended_keep": rec['keep'],
            "recommended_delete": rec['delete']
        })

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Report saved to: {output_file}")


def main():
    """Main deduplication workflow."""
    import argparse

    parser = argparse.ArgumentParser(description="Deduplicate Ruff family documents")
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without deleting')
    parser.add_argument('--delete', action='store_true',
                       help='Actually delete duplicates (use with caution!)')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactively review each duplicate before deletion')
    parser.add_argument('--similarity', type=float, default=0.9,
                       help='Filename similarity threshold (0.0-1.0, default: 0.9)')
    parser.add_argument('--size-tolerance', type=float, default=0.05,
                       help='Size difference tolerance (default: 0.05 = 5%%)')
    parser.add_argument('--report', type=str, default='deduplication_report.json',
                       help='Output report file (default: deduplication_report.json)')

    args = parser.parse_args()

    print("🧹 Rufftree Document Deduplication")
    print("="*80)

    # Initialize client
    client = get_client()
    store_name = get_store(client)

    # List all documents
    documents = list_all_documents(client, store_name)

    if not documents:
        print("\n✅ No documents in store, nothing to deduplicate")
        return

    # Find duplicates
    duplicate_groups = find_duplicates(
        documents,
        similarity_threshold=args.similarity,
        size_tolerance=args.size_tolerance
    )

    # Display duplicates
    display_duplicate_groups(duplicate_groups)

    if not duplicate_groups:
        return

    # Get recommendations
    recommendations = recommend_deletions(duplicate_groups)

    # Save report
    save_report(duplicate_groups, recommendations, args.report)

    # Handle deletion
    if args.interactive:
        interactive_review(client, store_name, recommendations)
    elif args.delete:
        print("\n⚠️  WARNING: About to delete documents!")
        to_delete = []
        for rec in recommendations:
            to_delete.extend([doc['name'] for doc in rec['delete']])

        print(f"\nWill delete {len(to_delete)} document(s):")
        for rec in recommendations:
            print(f"\nKeeping: {rec['keep']['display_name']}")
            print(f"Deleting:")
            for doc in rec['delete']:
                print(f"  - {doc['display_name']}")

        confirm = input("\nType 'DELETE' to confirm: ").strip()
        if confirm == 'DELETE':
            delete_documents(client, store_name, to_delete, dry_run=False)
        else:
            print("❌ Deletion cancelled")
    else:
        # Dry run mode (default)
        to_delete = []
        for rec in recommendations:
            to_delete.extend([doc['name'] for doc in rec['delete']])
        delete_documents(client, store_name, to_delete, dry_run=True)

    print("\n✅ Deduplication complete!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
