#!/usr/bin/env python3
"""
Generate contributor statistics for the Rufftree project.

This script analyzes:
- Story contributions (from RAG File Search documents)
- Person additions (from family_tree.json and git history)
- Query contributions (from stored_queries.json)

Outputs a leaderboard showing top contributors.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from collections import defaultdict

# Try to import google-genai, but make it optional
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("⚠️  google-genai not available, skipping RAG document analysis")


def get_client():
    """Initialize Google GenAI client."""
    if not GENAI_AVAILABLE:
        return None

    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        print("⚠️  GOOGLE_GENAI_API_KEY not set, skipping RAG document analysis")
        return None
    return genai.Client(api_key=api_key)


def get_store(client):
    """Get the rufftree File Search store."""
    if not client:
        return None

    try:
        stores = list(client.file_search_stores.list())
        for store in stores:
            store_display = getattr(store, 'display_name', None) or ''
            store_name_lower = store.name.lower() if store.name else ''
            if ('rufftree' in store_display.lower()) or ('rufftree' in store_name_lower):
                return store.name
    except Exception as e:
        print(f"⚠️  Could not access File Search store: {e}")

    return None


def count_story_contributions(client, store_name):
    """
    Count story contributions from RAG documents.

    Story files are named: YYYYMMDD_<author>story_<title>.docx
    E.g., 20251213_patstory_title.docx -> Patrick Ruff
    """
    contributions = defaultdict(int)

    if not client or not store_name:
        print("⚠️  Skipping story contribution counting (no RAG access)")
        return contributions

    print("📚 Counting story contributions from RAG documents...")

    try:
        docs = list(client.file_search_stores.documents.list(parent=store_name))

        for doc in docs:
            display_name = getattr(doc, 'display_name', '')

            # Look for story pattern: YYYYMMDD_<author>story_<title>.docx
            if 'story' in display_name.lower() and display_name.endswith('.docx'):
                # Extract author from filename
                parts = display_name.split('_')
                if len(parts) >= 2:
                    # Second part should be like "patstory"
                    author_part = parts[1]
                    if 'story' in author_part.lower():
                        # Extract author name (everything before 'story')
                        author_prefix = author_part.lower().replace('story', '').strip()

                        # Map author prefixes to full names
                        author_map = {
                            'pat': 'Patrick Ruff',
                            'patrick': 'Patrick Ruff',
                            'joe': 'Joe Ruff',
                            'jenny': 'Jenny Wang',
                            'sarah': 'Sarah Boilon',
                            'debbie': 'Debbie Ruff',
                        }

                        author = author_map.get(author_prefix, author_prefix.title())
                        contributions[author] += 1

        print(f"   ✅ Found {sum(contributions.values())} story contributions")

    except Exception as e:
        print(f"   ⚠️  Error counting stories: {e}")

    return contributions


def count_person_additions():
    """
    Count person additions from git commit history.

    Looks for commits with messages like "Process add-person issue" or "Add person".
    """
    contributions = defaultdict(int)

    print("\n👥 Counting person additions from git history...")

    try:
        # Get git log for commits that added people
        result = subprocess.run(
            ['git', 'log', '--all', '--grep=Process add-person', '--grep=Add person',
             '--grep=person:added', '--oneline'],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            commits = result.stdout.strip().split('\n')
            commits = [c for c in commits if c]  # Remove empty lines

            # For now, attribute to repo owner (Patrick Ruff)
            # In the future, could parse issue numbers and look up who submitted
            if commits:
                contributions['Patrick Ruff'] += len(commits)

            print(f"   ✅ Found {len(commits)} person addition commits")
        else:
            print(f"   ⚠️  Could not read git history")

    except Exception as e:
        print(f"   ⚠️  Error counting person additions: {e}")

    return contributions


def count_query_contributions():
    """Count query contributions from stored_queries.json."""
    contributions = defaultdict(int)

    print("\n💬 Counting query contributions...")

    try:
        queries_file = Path('stored_queries.json')
        if not queries_file.exists():
            print("   ⚠️  stored_queries.json not found")
            return contributions

        with open(queries_file) as f:
            data = json.load(f)

        queries = data.get('queries', [])

        for query in queries:
            asked_by = query.get('askedBy', 'Unknown')
            contributions[asked_by] += 1

        print(f"   ✅ Found {len(queries)} query contributions")

    except Exception as e:
        print(f"   ⚠️  Error counting queries: {e}")

    return contributions


def merge_contributions(story_contribs, person_contribs, query_contribs):
    """Merge all contribution types into a single leaderboard."""
    leaderboard = defaultdict(lambda: {'stories': 0, 'people': 0, 'queries': 0, 'total': 0})

    for author, count in story_contribs.items():
        leaderboard[author]['stories'] = count
        leaderboard[author]['total'] += count

    for author, count in person_contribs.items():
        leaderboard[author]['people'] = count
        leaderboard[author]['total'] += count

    for author, count in query_contribs.items():
        leaderboard[author]['queries'] = count
        leaderboard[author]['total'] += count

    return leaderboard


def generate_leaderboard_markdown(leaderboard):
    """Generate markdown for the contributor leaderboard."""
    # Sort by total contributions (descending)
    sorted_contributors = sorted(
        leaderboard.items(),
        key=lambda x: x[1]['total'],
        reverse=True
    )

    markdown = []
    markdown.append("## 🏆 Top Contributors\n")
    markdown.append("Thank you to everyone who has contributed to preserving our family history!\n")
    markdown.append("| Rank | Contributor | Stories | People Added | Questions | Total |")
    markdown.append("|------|------------|---------|--------------|-----------|-------|")

    for rank, (name, stats) in enumerate(sorted_contributors, 1):
        # Add medal emojis for top 3
        medal = ""
        if rank == 1:
            medal = "🥇 "
        elif rank == 2:
            medal = "🥈 "
        elif rank == 3:
            medal = "🥉 "

        markdown.append(
            f"| {rank} | {medal}{name} | {stats['stories']} | {stats['people']} | "
            f"{stats['queries']} | **{stats['total']}** |"
        )

    markdown.append("")
    markdown.append("*Leaderboard updated automatically. Contribute by [sharing a story]"
                   "(../../issues/new?template=family-story.yml) or "
                   "[adding a family member](../../issues/new?template=add-person.yml)!*")

    return '\n'.join(markdown)


def update_readme_with_leaderboard(leaderboard_markdown):
    """Update README.md with the contributor leaderboard."""
    readme_path = Path('README.md')

    if not readme_path.exists():
        print("❌ README.md not found")
        return False

    print("\n📝 Updating README.md with leaderboard...")

    with open(readme_path) as f:
        content = f.read()

    # Find the leaderboard section (or create it at the end)
    leaderboard_marker = "## 🏆 Top Contributors"

    if leaderboard_marker in content:
        # Replace existing leaderboard
        print("   ✅ Found existing leaderboard, updating...")

        # Find the start of the leaderboard section
        start_idx = content.find(leaderboard_marker)

        # Find the next ## heading or end of file
        next_section_idx = content.find('\n## ', start_idx + 1)
        if next_section_idx == -1:
            next_section_idx = len(content)

        # Replace the section
        new_content = (
            content[:start_idx] +
            leaderboard_markdown + '\n\n' +
            content[next_section_idx:]
        )
    else:
        # Add leaderboard before the "Resources" section or at the end
        print("   ✅ Adding new leaderboard section...")

        resources_idx = content.find('## Resources')
        if resources_idx != -1:
            # Insert before Resources
            new_content = (
                content[:resources_idx] +
                leaderboard_markdown + '\n\n' +
                content[resources_idx:]
            )
        else:
            # Add at the end
            new_content = content + '\n\n' + leaderboard_markdown + '\n'

    with open(readme_path, 'w') as f:
        f.write(new_content)

    print("   ✅ README.md updated successfully!")
    return True


def save_stats_json(leaderboard):
    """Save contributor statistics to JSON file."""
    stats_file = Path('contributor_stats.json')

    stats = {
        'contributors': dict(leaderboard),
        'total_contributors': len(leaderboard),
        'total_contributions': sum(c['total'] for c in leaderboard.values())
    }

    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"\n💾 Statistics saved to {stats_file}")


def main():
    """Main workflow."""
    print("🏆 Generating Contributor Statistics")
    print("="*80 + "\n")

    # Get client and store
    client = get_client()
    store_name = get_store(client) if client else None

    # Count contributions
    story_contribs = count_story_contributions(client, store_name)
    person_contribs = count_person_additions()
    query_contribs = count_query_contributions()

    # Merge contributions
    leaderboard = merge_contributions(story_contribs, person_contribs, query_contribs)

    if not leaderboard:
        print("\n⚠️  No contributions found")
        return

    # Generate leaderboard markdown
    leaderboard_markdown = generate_leaderboard_markdown(leaderboard)

    print("\n" + "="*80)
    print("LEADERBOARD PREVIEW")
    print("="*80)
    print(leaderboard_markdown)
    print("="*80)

    # Update README
    update_readme_with_leaderboard(leaderboard_markdown)

    # Save stats JSON
    save_stats_json(leaderboard)

    print("\n✅ Contributor statistics generated successfully!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
