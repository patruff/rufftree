#!/usr/bin/env python3
"""
Standalone script to test Google File Search with Ruff family documents.
Can be run in CI/CD or locally to upload documents and run queries.
"""

import os
import sys
import time
import json
from pathlib import Path
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


def get_or_create_store(client):
    """Get or create the file search store for Ruff family documents."""
    # First, try to find existing store by listing all stores
    print("🔍 Searching for existing Ruff family store...")
    try:
        stores = list(client.file_search_stores.list())
        print(f"   Found {len(stores)} total store(s)")

        # Look for store with 'rufftree' in display name OR in store name
        for store in stores:
            store_display = getattr(store, 'display_name', None) or ''
            store_name_lower = store.name.lower() if store.name else ''
            print(f"   - Store: {store.name}")
            print(f"     Display name: {store_display}")

            # Check both display name and store name for 'rufftree'
            if ('rufftree' in store_display.lower()) or ('rufftree' in store_name_lower):
                print(f"📦 Found existing Ruff family store: {store.name}")
                # Verify it has documents
                try:
                    docs = list(client.file_search_stores.documents.list(parent=store.name))
                    print(f"   ✅ Store contains {len(docs)} document(s)")
                except Exception as doc_err:
                    print(f"   ⚠️  Could not list documents: {doc_err}")
                return store.name
        print(f"   None of the stores match 'rufftree'")
    except Exception as e:
        print(f"⚠️  Could not list stores: {e}")
        import traceback
        traceback.print_exc()

    # Fall back to config files for backwards compatibility
    repo_config_path = Path(__file__).parent / ".rufftree_store.json"
    home_config_path = Path.home() / ".rufftree_mcp" / "store_config.json"

    store_name = None

    # Check repository-level config
    if repo_config_path.exists():
        try:
            with open(repo_config_path) as f:
                config = json.load(f)
                store_name = config.get("store_name")
                if store_name:
                    print(f"📦 Using store from repo config: {store_name}")
                    return store_name
        except Exception as e:
            print(f"⚠️  Could not load repo store config: {e}")

    # Check home directory config
    if home_config_path.exists():
        try:
            with open(home_config_path) as f:
                config = json.load(f)
                store_name = config.get("store_name")
                if store_name:
                    print(f"📦 Using store from home config: {store_name}")
                    return store_name
        except Exception as e:
            print(f"⚠️  Could not load home store config: {e}")

    # Create new store if none found
    print("📦 Creating new file search store for Ruff family documents...")
    store = client.file_search_stores.create(
        config={'display_name': 'rufftree'}
    )
    store_name = store.name
    print(f"✅ Created new store: {store_name}")
    print(f"   Display name: rufftree")

    # Save to config files for reference
    home_config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(home_config_path, 'w') as f:
        json.dump({"store_name": store_name}, f)
    print(f"💾 Saved store config to {home_config_path}")

    with open(repo_config_path, 'w') as f:
        json.dump({"store_name": store_name, "created_at": time.strftime('%Y-%m-%d %H:%M:%S')}, f, indent=2)
    print(f"💾 Saved store config to {repo_config_path}")

    return store_name


def upload_document(client, store_name, file_path):
    """Upload a document to the file search store with verification."""
    file_path = Path(file_path).resolve()

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Support multiple document types
    supported_extensions = {'.pdf', '.docx', '.doc', '.txt', '.md'}
    if file_path.suffix.lower() not in supported_extensions:
        raise ValueError(f"File must be one of {supported_extensions}, got: {file_path.suffix}")

    print(f"\n📤 Uploading {file_path.name}...")

    # Check for duplicate before uploading
    print("   Checking for duplicates...")
    try:
        existing_docs = list(client.file_search_stores.documents.list(parent=store_name))
        for doc in existing_docs:
            doc_display = getattr(doc, 'display_name', '') or ''
            if doc_display.lower() == file_path.name.lower():
                print(f"   ⚠️  Document '{file_path.name}' already exists in store, skipping upload")
                return None
    except Exception as e:
        print(f"   ⚠️  Could not check for duplicates: {e}")

    # Upload file to the file search store
    operation = client.file_search_stores.upload_to_file_search_store(
        file_search_store_name=store_name,
        file=str(file_path),
        config={
            'display_name': file_path.name,
        }
    )

    # Wait for upload to complete
    print("⏳ Waiting for upload and indexing...")
    max_wait = 300  # 5 minutes max
    start_time = time.time()

    while not operation.done:
        if time.time() - start_time > max_wait:
            raise TimeoutError("Upload timed out after 5 minutes")
        time.sleep(5)
        operation = client.operations.get(operation)
        elapsed = int(time.time() - start_time)
        print(f"  ⏱️  {elapsed}s elapsed...", end='\r')

    print(f"\n✅ Upload operation completed for: {file_path.name}")

    # Verify upload was successful
    print("\n🔍 Verifying upload...")
    upload_verified = False
    try:
        # Check operation response for document name
        if hasattr(operation, 'response') and operation.response:
            if hasattr(operation.response, 'document_name'):
                print(f"   ✅ Document created: {operation.response.document_name}")
                upload_verified = True

        # Also verify by listing documents
        docs = list(client.file_search_stores.documents.list(parent=store_name))
        found_doc = None
        for doc in docs:
            doc_display = getattr(doc, 'display_name', '') or ''
            if doc_display.lower() == file_path.name.lower():
                found_doc = doc
                break

        if found_doc:
            state = getattr(found_doc, 'state', 'unknown')
            print(f"   ✅ Document verified in store: {found_doc.name}")
            print(f"   📊 State: {state}")
            upload_verified = True
        else:
            print(f"   ⚠️  Document not found in store listing after upload")

    except Exception as e:
        print(f"   ❌ Error verifying upload: {e}")

    if upload_verified:
        print(f"✅ Successfully uploaded and verified: {file_path.name}")
    else:
        print(f"⚠️  Upload completed but verification uncertain for: {file_path.name}")

    return operation


def query_documents(client, store_name, query, model="gemini-2.5-flash"):
    """Query the documents using RAG with citations."""
    print(f"\n🔍 Query: {query}")
    print(f"   Model: {model}")
    print(f"   Store: {store_name}")

    # Debug: Check documents before query
    print("\n🔍 DEBUG - Checking documents before query:")
    try:
        pre_query_docs = client.file_search_stores.documents.list(parent=store_name)
        doc_list = list(pre_query_docs)
        if doc_list:
            print(f"   ✅ Found {len(doc_list)} document(s)")
            for doc in doc_list:
                state = doc.state if hasattr(doc, 'state') else 'unknown'
                print(f"      - {doc.name}: {state}")
        else:
            print("   ⚠️  No documents found before query")
            return "No documents available to query.", []
    except Exception as e:
        print(f"   ❌ Error checking documents: {e}")
        return f"Error checking documents: {e}", []

    # Debug: Show tool configuration
    print("\n🔍 DEBUG - Tool configuration:")
    print(f"   file_search_store_names: [{store_name}]")

    # Use the file search store as a tool in generation call
    print("\n🔍 DEBUG - Making generate_content call...")
    try:
        response = client.models.generate_content(
            model=model,
            contents=query,
            config={
                'tools': [{
                    'file_search': {
                        'file_search_store_names': [store_name]
                    }
                }]
            }
        )
        print("   ✅ generate_content call succeeded")
    except Exception as e:
        print(f"   ❌ generate_content call failed: {e}")
        import traceback
        traceback.print_exc()
        return f"Query failed: {e}", []

    # Debug: Print response structure
    print("\n🔍 DEBUG - Response structure:")
    print(f"   Has candidates: {hasattr(response, 'candidates') and response.candidates}")
    if hasattr(response, 'candidates') and response.candidates:
        print(f"   Number of candidates: {len(response.candidates)}")
        for i, candidate in enumerate(response.candidates):
            print(f"   Candidate {i}:")
            print(f"      - Has content: {hasattr(candidate, 'content')}")
            print(f"      - Has grounding_metadata: {hasattr(candidate, 'grounding_metadata')}")
            if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                gm = candidate.grounding_metadata
                print(f"      - Has grounding_chunks: {hasattr(gm, 'grounding_chunks')}")
                if hasattr(gm, 'grounding_chunks') and gm.grounding_chunks:
                    print(f"      - Number of grounding_chunks: {len(gm.grounding_chunks)}")

    # Extract answer
    answer = response.text
    print(f"\n🔍 DEBUG - Extracted answer length: {len(answer)} characters")

    # Extract citations from grounding metadata
    citations = []
    if response.candidates and len(response.candidates) > 0:
        grounding = response.candidates[0].grounding_metadata
        if grounding and grounding.grounding_chunks:
            print(f"\n🔍 DEBUG - Processing {len(grounding.grounding_chunks)} grounding chunks")
            for i, chunk in enumerate(grounding.grounding_chunks):
                print(f"   Chunk {i}:")
                print(f"      - Has retrieved_context: {hasattr(chunk, 'retrieved_context')}")
                if chunk.retrieved_context:
                    print(f"      - Title: {chunk.retrieved_context.title if hasattr(chunk.retrieved_context, 'title') else 'N/A'}")
                    citations.append({
                        "title": chunk.retrieved_context.title,
                        "uri": getattr(chunk.retrieved_context, 'uri', 'N/A')
                    })
        else:
            print("\n🔍 DEBUG - No grounding metadata found")

    # Print formatted response
    print("\n" + "="*80)
    print("📝 ANSWER")
    print("="*80)
    print(answer)
    print()

    if citations:
        print("="*80)
        print("📚 CITATIONS")
        print("="*80)
        unique_sources = {c['title'] for c in citations}
        for i, source in enumerate(unique_sources, 1):
            print(f"{i}. {source}")
    else:
        print("ℹ️  No citations found in this response")

    print("="*80 + "\n")

    return answer, citations


def list_documents(client, store_name):
    """List all indexed documents in the store."""
    print("\n📚 Listing indexed documents...")
    print(f"   Store: {store_name}")

    try:
        # Debug: Show what we're calling
        print("\n🔍 DEBUG - Calling documents.list:")
        print(f"   parent={store_name}")

        # List documents in the store using the documents API
        response = client.file_search_stores.documents.list(parent=store_name)

        # Debug: Print response type
        print(f"\n🔍 DEBUG - Response type: {type(response)}")

        # Pager is an iterator - convert to list directly
        try:
            doc_list = list(response)
            print(f"   ✅ Successfully converted Pager to list: {len(doc_list)} document(s)")
        except Exception as e:
            print(f"   ❌ Error converting Pager to list: {e}")
            return []

        if not doc_list:
            print("ℹ️  No documents indexed yet")
            return []

        print(f"\n🔍 DEBUG - Successfully retrieved {len(doc_list)} document(s)")

        # Calculate stats
        total_bytes = sum(int(getattr(doc, 'size_bytes', 0)) for doc in doc_list)
        total_mb = total_bytes / (1024 * 1024)

        # Estimate tokens (roughly 1 token per 4 characters)
        estimated_tokens = total_bytes // 4
        estimated_cost = (estimated_tokens / 1_000_000) * 0.15

        print(f"\n📊 Found {len(doc_list)} indexed document(s):\n")
        for i, doc in enumerate(doc_list, 1):
            display_name = getattr(doc, 'display_name', 'Unknown')
            size_bytes = int(getattr(doc, 'size_bytes', 0))
            size_mb = size_bytes / (1024 * 1024)

            print(f"{i}. {display_name}")
            print(f"   ID: {doc.name}")
            print(f"   Size: {size_mb:.2f} MB ({size_bytes:,} bytes)")
            if hasattr(doc, 'state'):
                print(f"   State: {doc.state}")
            if hasattr(doc, 'create_time'):
                print(f"   Uploaded: {doc.create_time}")
            print()

        # Print summary stats
        print("="*80)
        print("📈 INDEXING STATISTICS")
        print("="*80)
        print(f"📄 Total Documents: {len(doc_list)}")
        print(f"📦 Total Size: {total_mb:.2f} MB ({total_bytes:,} bytes)")
        print(f"🔤 Estimated Tokens: ~{estimated_tokens:,}")
        print(f"💰 Estimated Indexing Cost: ~${estimated_cost:.4f}")
        print("="*80)

        return doc_list

    except Exception as e:
        print(f"⚠️  Could not list documents: {e}")
        print(f"   Store: {store_name}")

        # Debug: show available methods
        print(f"\n🔍 Debug - Available file_search_stores methods:")
        for attr in dir(client.file_search_stores):
            if not attr.startswith('_'):
                print(f"   - {attr}")

        if hasattr(client.file_search_stores, 'documents'):
            print(f"\n🔍 Debug - Available documents methods:")
            for attr in dir(client.file_search_stores.documents):
                if not attr.startswith('_'):
                    print(f"   - {attr}")

        return []


def main():
    """Main workflow."""
    print("👨‍👩‍👧‍👦 Rufftree - Google File Search Test")
    print("="*80 + "\n")

    # Initialize client
    print("🔑 Initializing Google GenAI client...")
    client = get_client()
    print("✅ Client initialized\n")

    # Get or create store
    store_name = get_or_create_store(client)

    # Upload document if specified
    doc_path = os.getenv("DOCUMENT_PATH")
    if doc_path and Path(doc_path).exists():
        upload_document(client, store_name, doc_path)
    else:
        if doc_path:
            print(f"⚠️  Document not found: {doc_path}")
        else:
            print("ℹ️  No DOCUMENT_PATH specified, skipping upload")

    # List documents
    list_documents(client, store_name)

    # Run example queries if there are documents
    print("\n🎯 Example queries available. Set query via QUERY env var or modify script.\n")

    # Allow single query from environment
    query = os.getenv("QUERY")
    if query:
        print(f"\n{'='*80}")
        print(f"RUNNING QUERY")
        print(f"{'='*80}")
        try:
            query_documents(client, store_name, query)
        except Exception as e:
            print(f"❌ Error running query: {e}")

    print("\n✅ Test completed successfully!")
    print(f"📦 Store: {store_name}")
    print("\nYou can now use this store in the MCP server by ensuring the")
    print("store config is present at ~/.rufftree_mcp/store_config.json")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
