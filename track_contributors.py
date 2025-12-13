#!/usr/bin/env python3
"""
Track story contributors from metadata.

This script maintains a contributor tracking file that records:
- Who submitted each story
- When it was submitted
- What the story was about

This can be called from workflows to update contributor counts in real-time.
"""

import json
from pathlib import Path
from datetime import datetime


CONTRIBUTORS_FILE = Path('contributors.json')


def initialize_contributors_file():
    """Initialize the contributors.json file if it doesn't exist."""
    if CONTRIBUTORS_FILE.exists():
        return

    initial_data = {
        "_description": "Tracks all contributions to the Ruff family archive",
        "contributors": {},
        "stories": [],
        "people_added": [],
        "queries": []
    }

    with open(CONTRIBUTORS_FILE, 'w') as f:
        json.dump(initial_data, f, indent=2)

    print(f"✅ Created {CONTRIBUTORS_FILE}")


def load_contributors():
    """Load the contributors data."""
    if not CONTRIBUTORS_FILE.exists():
        initialize_contributors_file()

    with open(CONTRIBUTORS_FILE) as f:
        return json.load(f)


def save_contributors(data):
    """Save the contributors data."""
    with open(CONTRIBUTORS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def add_story_contribution(author, title, about, date=None):
    """
    Record a story contribution.

    Args:
        author: Name of the person who wrote/shared the story (or "Anonymous")
        title: Title of the story
        about: Who the story is about (string or list)
        date: ISO date string (defaults to today)
    """
    data = load_contributors()

    if date is None:
        date = datetime.now().isoformat().split('T')[0]

    # Ensure author is not empty
    if not author or author.strip() == '':
        author = 'Anonymous'

    # Add to stories list
    story_entry = {
        'author': author,
        'title': title,
        'about': about if isinstance(about, list) else [about],
        'date': date,
        'type': 'story'
    }
    data['stories'].append(story_entry)

    # Update contributor count
    if author not in data['contributors']:
        data['contributors'][author] = {
            'stories': 0,
            'people_added': 0,
            'queries': 0,
            'total': 0
        }

    data['contributors'][author]['stories'] += 1
    data['contributors'][author]['total'] += 1

    save_contributors(data)
    print(f"✅ Added story contribution: '{title}' by {author}")


def add_person_contribution(contributor, person_name, date=None):
    """
    Record a person addition contribution.

    Args:
        contributor: Name of the person who added this family member
        person_name: Name of the family member added
        date: ISO date string (defaults to today)
    """
    data = load_contributors()

    if date is None:
        date = datetime.now().isoformat().split('T')[0]

    if not contributor or contributor.strip() == '':
        contributor = 'Anonymous'

    # Add to people_added list
    person_entry = {
        'contributor': contributor,
        'person_name': person_name,
        'date': date,
        'type': 'person_added'
    }
    data['people_added'].append(person_entry)

    # Update contributor count
    if contributor not in data['contributors']:
        data['contributors'][contributor] = {
            'stories': 0,
            'people_added': 0,
            'queries': 0,
            'total': 0
        }

    data['contributors'][contributor]['people_added'] += 1
    data['contributors'][contributor]['total'] += 1

    save_contributors(data)
    print(f"✅ Added person contribution: {person_name} by {contributor}")


def add_query_contribution(contributor, question, date=None):
    """
    Record a query contribution.

    Args:
        contributor: Name of the person who asked the question
        question: The question asked
        date: ISO date string (defaults to today)
    """
    data = load_contributors()

    if date is None:
        date = datetime.now().isoformat().split('T')[0]

    if not contributor or contributor.strip() == '':
        contributor = 'Anonymous'

    # Add to queries list
    query_entry = {
        'contributor': contributor,
        'question': question,
        'date': date,
        'type': 'query'
    }
    data['queries'].append(query_entry)

    # Update contributor count
    if contributor not in data['contributors']:
        data['contributors'][contributor] = {
            'stories': 0,
            'people_added': 0,
            'queries': 0,
            'total': 0
        }

    data['contributors'][contributor]['queries'] += 1
    data['contributors'][contributor]['total'] += 1

    save_contributors(data)
    print(f"✅ Added query contribution by {contributor}")


def get_leaderboard():
    """Get the contributor leaderboard sorted by total contributions."""
    data = load_contributors()

    # Sort contributors by total contributions
    sorted_contributors = sorted(
        data['contributors'].items(),
        key=lambda x: x[1]['total'],
        reverse=True
    )

    return sorted_contributors


def generate_leaderboard_markdown():
    """Generate markdown for the contributor leaderboard."""
    leaderboard = get_leaderboard()

    markdown = []
    markdown.append("## 🏆 Top Contributors\n")
    markdown.append("Thank you to everyone who has contributed to preserving our family history!\n")
    markdown.append("| Rank | Contributor | Stories | People Added | Questions | Total |")
    markdown.append("|------|------------|---------|--------------|-----------|-------|")

    for rank, (name, stats) in enumerate(leaderboard, 1):
        # Add medal emojis for top 3
        medal = ""
        if rank == 1:
            medal = "🥇 "
        elif rank == 2:
            medal = "🥈 "
        elif rank == 3:
            medal = "🥉 "

        markdown.append(
            f"| {rank} | {medal}{name} | {stats['stories']} | {stats['people_added']} | "
            f"{stats['queries']} | **{stats['total']}** |"
        )

    markdown.append("")
    markdown.append("*Leaderboard updated automatically. Contribute by [sharing a story]"
                   "(../../issues/new?template=family-story.yml) or "
                   "[adding a family member](../../issues/new?template=add-person.yml)!*")

    return '\n'.join(markdown)


def update_readme_with_leaderboard():
    """Update README.md with the contributor leaderboard."""
    readme_path = Path('README.md')

    if not readme_path.exists():
        print("❌ README.md not found")
        return False

    print("\n📝 Updating README.md with leaderboard...")

    with open(readme_path) as f:
        content = f.read()

    leaderboard_markdown = generate_leaderboard_markdown()

    # Find the leaderboard section
    leaderboard_marker = "## 🏆 Top Contributors"

    if leaderboard_marker in content:
        # Replace existing leaderboard
        print("   ✅ Found existing leaderboard, updating...")

        start_idx = content.find(leaderboard_marker)
        next_section_idx = content.find('\n## ', start_idx + 1)
        if next_section_idx == -1:
            next_section_idx = len(content)

        new_content = (
            content[:start_idx] +
            leaderboard_markdown + '\n\n' +
            content[next_section_idx:]
        )
    else:
        # Add leaderboard before Resources section
        print("   ✅ Adding new leaderboard section...")

        resources_idx = content.find('## Resources')
        if resources_idx != -1:
            new_content = (
                content[:resources_idx] +
                leaderboard_markdown + '\n\n' +
                content[resources_idx:]
            )
        else:
            new_content = content + '\n\n' + leaderboard_markdown + '\n'

    with open(readme_path, 'w') as f:
        f.write(new_content)

    print("   ✅ README.md updated successfully!")
    return True


def main():
    """Main CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Track contributions to the family archive")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Add story contribution
    story_parser = subparsers.add_parser('add-story', help='Add a story contribution')
    story_parser.add_argument('--author', required=True, help='Story author (or "Anonymous")')
    story_parser.add_argument('--title', required=True, help='Story title')
    story_parser.add_argument('--about', required=True, help='Who the story is about')
    story_parser.add_argument('--date', help='Date (YYYY-MM-DD, defaults to today)')

    # Add person contribution
    person_parser = subparsers.add_parser('add-person', help='Add a person contribution')
    person_parser.add_argument('--contributor', required=True, help='Who added this person')
    person_parser.add_argument('--name', required=True, help='Name of person added')
    person_parser.add_argument('--date', help='Date (YYYY-MM-DD, defaults to today)')

    # Add query contribution
    query_parser = subparsers.add_parser('add-query', help='Add a query contribution')
    query_parser.add_argument('--contributor', required=True, help='Who asked the question')
    query_parser.add_argument('--question', required=True, help='The question')
    query_parser.add_argument('--date', help='Date (YYYY-MM-DD, defaults to today)')

    # Update leaderboard
    subparsers.add_parser('update-leaderboard', help='Update the README leaderboard')

    # Show leaderboard
    subparsers.add_parser('show', help='Show current leaderboard')

    args = parser.parse_args()

    if args.command == 'add-story':
        add_story_contribution(args.author, args.title, args.about, args.date)
    elif args.command == 'add-person':
        add_person_contribution(args.contributor, args.name, args.date)
    elif args.command == 'add-query':
        add_query_contribution(args.contributor, args.question, args.date)
    elif args.command == 'update-leaderboard':
        update_readme_with_leaderboard()
    elif args.command == 'show':
        leaderboard = get_leaderboard()
        print("\n" + "="*80)
        print("🏆 CONTRIBUTOR LEADERBOARD")
        print("="*80)
        for rank, (name, stats) in enumerate(leaderboard, 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            print(f"{medal} {rank}. {name}: {stats['total']} total "
                  f"({stats['stories']} stories, {stats['people_added']} people, {stats['queries']} queries)")
        print("="*80)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
