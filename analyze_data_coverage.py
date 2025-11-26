#!/usr/bin/env python3
"""
Analyze data coverage for each person in the family tree by querying the RAG system.
Counts how many document chunks mention each person and flags those with insufficient data.
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, Tuple
from test_file_search import get_client, get_or_create_store


# Configuration
CHUNKS_THRESHOLD = 2  # People with < this many chunks get lacks_data flag
QUERY_DELAY = 1.0  # Seconds to wait between queries to avoid rate limits


def load_family_data():
    """Load the family tree JSON data."""
    with open('family_tree.json', 'r') as f:
        return json.load(f)


def save_family_data(data):
    """Save the family tree JSON data."""
    with open('family_tree.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n💾 Saved updated family tree to family_tree.json")


def query_person_chunks(client, store_name: str, person_name: str, model="gemini-2.0-flash-001") -> Tuple[int, list]:
    """
    Query the RAG system for a person and return the number of grounding chunks.

    Args:
        client: Google GenAI client
        store_name: File search store name
        person_name: Name of the person to search for
        model: Model to use for the query

    Returns:
        Tuple of (chunk_count, chunk_titles)
    """
    query = f"What do we know about {person_name}? Tell me about their life, family, and any stories."

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

        # Extract grounding chunks
        chunks = []
        chunk_titles = []

        if response.candidates and len(response.candidates) > 0:
            grounding = response.candidates[0].grounding_metadata
            if grounding and grounding.grounding_chunks:
                for chunk in grounding.grounding_chunks:
                    if chunk.retrieved_context:
                        title = getattr(chunk.retrieved_context, 'title', 'Unknown')
                        chunks.append(chunk)
                        chunk_titles.append(title)

        return len(chunks), chunk_titles

    except Exception as e:
        print(f"      ❌ Error querying for {person_name}: {e}")
        return 0, []


def analyze_data_coverage():
    """Main function to analyze data coverage for all people."""
    print("\n" + "="*80)
    print("📊 FAMILY TREE DATA COVERAGE ANALYSIS")
    print("="*80)
    print(f"\nThis will query the RAG system for each person and count document chunks.")
    print(f"Threshold: {CHUNKS_THRESHOLD} chunks (below this = lacks_data flag)")
    print("="*80 + "\n")

    # Load family data
    print("📂 Loading family tree...")
    data = load_family_data()
    people = data['family']['people']
    print(f"   ✅ Loaded {len(people)} family members\n")

    # Initialize RAG client
    print("🔧 Initializing RAG system...")
    client = get_client()
    store_name = get_or_create_store(client)
    print()

    # Analyze each person
    print("🔍 Analyzing data coverage for each person...")
    print("="*80 + "\n")

    results = {
        'total': len(people),
        'with_data': 0,
        'lacks_data': 0,
        'no_chunks': 0,
        'details': []
    }

    for i, (person_id, person) in enumerate(people.items(), 1):
        person_name = person.get('name', 'Unknown')
        print(f"[{i}/{len(people)}] Checking: {person_name}")

        # Query RAG for this person
        chunk_count, chunk_titles = query_person_chunks(client, store_name, person_name)

        # Update person data
        person['rag_chunks'] = chunk_count
        person['lacks_data'] = chunk_count < CHUNKS_THRESHOLD

        # Collect statistics
        if chunk_count == 0:
            results['no_chunks'] += 1
            status = "❌ NO DATA"
        elif chunk_count < CHUNKS_THRESHOLD:
            results['lacks_data'] += 1
            status = f"⚠️  INSUFFICIENT ({chunk_count} chunk{'s' if chunk_count != 1 else ''})"
        else:
            results['with_data'] += 1
            status = f"✅ OK ({chunk_count} chunks)"

        print(f"   {status}")

        # Show chunk sources for those with data
        if chunk_count > 0 and chunk_titles:
            unique_titles = list(set(chunk_titles))
            if len(unique_titles) <= 3:
                print(f"   Sources: {', '.join(unique_titles)}")
            else:
                print(f"   Sources: {', '.join(unique_titles[:3])}... (+{len(unique_titles)-3} more)")

        # Store detailed results
        results['details'].append({
            'name': person_name,
            'id': person_id,
            'chunks': chunk_count,
            'lacks_data': person['lacks_data'],
            'sources': list(set(chunk_titles))
        })

        print()

        # Rate limiting delay
        if i < len(people):
            time.sleep(QUERY_DELAY)

    # Save updated data
    print("="*80)
    print("💾 Saving updated family tree with coverage data...")
    save_family_data(data)

    # Print summary
    print("\n" + "="*80)
    print("📊 DATA COVERAGE SUMMARY")
    print("="*80)
    print(f"✅ Sufficient Data: {results['with_data']} people ({results['with_data']/results['total']*100:.1f}%)")
    print(f"⚠️  Insufficient Data: {results['lacks_data']} people ({results['lacks_data']/results['total']*100:.1f}%)")
    print(f"❌ No Data: {results['no_chunks']} people ({results['no_chunks']/results['total']*100:.1f}%)")
    print("="*80)

    # List people who lack data
    lacks_data_list = [d for d in results['details'] if d['lacks_data']]
    if lacks_data_list:
        print(f"\n⚠️  PEOPLE NEEDING MORE DOCUMENTATION ({len(lacks_data_list)}):")
        print("="*80)
        for person in sorted(lacks_data_list, key=lambda x: x['chunks']):
            chunk_info = f"{person['chunks']} chunk{'s' if person['chunks'] != 1 else ''}" if person['chunks'] > 0 else "NO DATA"
            print(f"   • {person['name']:<30} ({chunk_info})")
    else:
        print("\n🎉 All family members have sufficient documentation!")

    print("\n" + "="*80)

    # Create a report file
    report_file = Path('data_coverage_report.json')
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"📄 Detailed report saved to: {report_file}")
    print("="*80 + "\n")

    return results


def main():
    """Entry point for the script."""
    try:
        analyze_data_coverage()
    except KeyboardInterrupt:
        print("\n\n❌ Analysis cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
