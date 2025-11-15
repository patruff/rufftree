#!/usr/bin/env python3
"""
Helper script to answer family queries using RAG and store the results.

Usage:
    python answer_query.py "What do we know about the Ruff family immigration?"
    python answer_query.py --interactive
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from test_file_search import get_client, get_or_create_store, query_documents


QUERIES_FILE = Path(__file__).parent / "stored_queries.json"


def load_queries():
    """Load existing queries from JSON file."""
    if not QUERIES_FILE.exists():
        return {"queries": [], "_instructions": {}}

    with open(QUERIES_FILE, 'r') as f:
        return json.load(f)


def save_queries(data):
    """Save queries to JSON file."""
    with open(QUERIES_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n✅ Saved to {QUERIES_FILE}")


def get_next_id(queries_data):
    """Get the next available ID."""
    existing_ids = [int(q.get('id', 0)) for q in queries_data.get('queries', [])]
    return str(max(existing_ids, default=0) + 1)


def answer_query_interactive():
    """Interactive mode - ask for question and details."""
    print("="*80)
    print("🤖 Ruff Family Archive - Interactive Query Answerer")
    print("="*80)
    print()

    # Get question
    question = input("Enter the question: ").strip()
    if not question:
        print("❌ Error: Question cannot be empty")
        return

    # Get optional details
    asked_by = input("Asked by (optional, press Enter to skip): ").strip()

    # Initialize RAG client
    print("\n📦 Initializing RAG system...")
    client = get_client()
    store_name = get_or_create_store(client)

    # Query the RAG system
    print(f"\n🔍 Querying RAG system with: {question}")
    print("="*80)

    answer, citations = query_documents(client, store_name, question)

    # Format citations
    citation_list = list(set([c['title'] for c in citations])) if citations else []

    # Load existing queries
    queries_data = load_queries()

    # Create new query entry
    new_query = {
        "id": get_next_id(queries_data),
        "question": question,
        "answer": answer,
        "citations": citation_list,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "answeredBy": "RAG System"
    }

    if asked_by:
        new_query["askedBy"] = asked_by

    # Add to beginning of queries array
    queries_data.setdefault('queries', []).insert(0, new_query)

    # Save
    save_queries(queries_data)

    print("\n" + "="*80)
    print("✅ Query answered and saved!")
    print("="*80)
    print(f"View it at: queries.html")


def answer_query_direct(question, asked_by=None):
    """Answer a query directly from command line."""
    print(f"\n🔍 Question: {question}")
    print("="*80)

    # Initialize RAG client
    client = get_client()
    store_name = get_or_create_store(client)

    # Query the RAG system
    answer, citations = query_documents(client, store_name, question)

    # Format citations
    citation_list = list(set([c['title'] for c in citations])) if citations else []

    # Load existing queries
    queries_data = load_queries()

    # Create new query entry
    new_query = {
        "id": get_next_id(queries_data),
        "question": question,
        "answer": answer,
        "citations": citation_list,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "answeredBy": "RAG System"
    }

    if asked_by:
        new_query["askedBy"] = asked_by

    # Add to beginning of queries array
    queries_data.setdefault('queries', []).insert(0, new_query)

    # Save
    save_queries(queries_data)

    print("\n" + "="*80)
    print("✅ Query answered and saved!")
    print("="*80)


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-i', '--interactive']:
            answer_query_interactive()
        elif sys.argv[1] in ['-h', '--help']:
            print("Usage:")
            print("  python answer_query.py 'Your question here'")
            print("  python answer_query.py --interactive")
            print("  python answer_query.py --help")
        else:
            # Treat all arguments as the question
            question = ' '.join(sys.argv[1:])
            answer_query_direct(question)
    else:
        # No arguments, run interactive mode
        answer_query_interactive()


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
