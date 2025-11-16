#!/usr/bin/env python3
"""
Cleanup script to delete empty or unused File Search stores.

Deletes stores that:
1. Have no display name set
2. Have no documents indexed
3. Are not the active rufftree store

Usage:
    python cleanup_stores.py
"""

import os
import sys
from google import genai


def get_client():
    """Initialize Google GenAI client."""
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_GENAI_API_KEY environment variable not set. "
            "Get your API key from https://aistudio.google.com/apikey"
        )
    return genai.Client(api_key=api_key)


def cleanup_stores():
    """Delete empty/unnamed File Search stores."""
    print("🧹 File Search Store Cleanup")
    print("=" * 80)

    client = get_client()

    # List all stores
    print("📋 Listing all File Search stores...")
    stores = list(client.file_search_stores.list())
    print(f"   Found {len(stores)} total store(s)\n")

    # Categorize stores
    to_keep = []
    to_delete = []

    for store in stores:
        store_display = getattr(store, 'display_name', None) or ''
        store_name_lower = store.name.lower() if store.name else ''

        # Check if this is a rufftree store
        is_rufftree = ('rufftree' in store_display.lower()) or ('rufftree' in store_name_lower)

        # Check document count
        doc_count = 0
        try:
            docs = list(client.file_search_stores.documents.list(parent=store.name))
            doc_count = len(docs)
        except Exception:
            pass

        # Decide whether to keep or delete
        if is_rufftree and doc_count > 0:
            # Keep active rufftree stores with documents
            to_keep.append({
                'name': store.name,
                'display': store_display,
                'docs': doc_count,
                'reason': 'Active rufftree store with documents'
            })
        elif doc_count > 0:
            # Keep any store with documents
            to_keep.append({
                'name': store.name,
                'display': store_display,
                'docs': doc_count,
                'reason': 'Has documents'
            })
        elif is_rufftree:
            # Empty rufftree store - delete
            to_delete.append({
                'name': store.name,
                'display': store_display,
                'docs': doc_count,
                'reason': 'Empty rufftree store'
            })
        else:
            # No display name and no documents - delete
            to_delete.append({
                'name': store.name,
                'display': store_display,
                'docs': doc_count,
                'reason': 'No display name and empty'
            })

    # Report what we'll keep
    print("✅ STORES TO KEEP:")
    print("-" * 80)
    if to_keep:
        for store in to_keep:
            print(f"   📦 {store['name']}")
            print(f"      Display: {store['display'] or '(none)'}")
            print(f"      Documents: {store['docs']}")
            print(f"      Reason: {store['reason']}")
            print()
    else:
        print("   (none)\n")

    # Report what we'll delete
    print("🗑️  STORES TO DELETE:")
    print("-" * 80)
    if to_delete:
        for store in to_delete:
            print(f"   🗑️  {store['name']}")
            print(f"      Display: {store['display'] or '(none)'}")
            print(f"      Reason: {store['reason']}")
            print()
    else:
        print("   (none)\n")

    # Summary
    print("=" * 80)
    print(f"📊 SUMMARY")
    print(f"   Total stores: {len(stores)}")
    print(f"   Keeping: {len(to_keep)}")
    print(f"   Deleting: {len(to_delete)}")
    print("=" * 80)

    if not to_delete:
        print("\n✅ No stores to delete. All clean!")
        return

    # Delete stores
    print(f"\n🗑️  Deleting {len(to_delete)} store(s)...")
    success_count = 0
    fail_count = 0

    for store in to_delete:
        try:
            print(f"   Deleting {store['name']}...", end=' ')
            client.file_search_stores.delete(name=store['name'], config={'force': True})
            print("✅")
            success_count += 1
        except Exception as e:
            print(f"❌ {e}")
            fail_count += 1

    print(f"\n✅ Successfully deleted: {success_count}/{len(to_delete)} store(s)")
    if fail_count > 0:
        print(f"❌ Failed to delete: {fail_count} store(s)")


def main():
    """Main entry point."""
    cleanup_stores()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
