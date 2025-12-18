#!/usr/bin/env python3
"""
Script to establish parent-child relationships by parsing children names from notes.

This script:
1. Finds people with "Children:" in their notes
2. Parses the children names
3. Attempts to match them to people in the tree
4. Establishes bidirectional parent-child relationships
"""

import json
import re
from typing import List, Tuple, Optional, Dict


def load_family_data():
    """Load the family tree JSON data."""
    with open('family_tree.json', 'r') as f:
        return json.load(f)


def save_family_data(data):
    """Save the family tree JSON data."""
    with open('family_tree.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n💾 Saved updated family tree to family_tree.json")


def parse_children_from_notes(notes: str) -> List[str]:
    """
    Parse children names from notes field.

    Args:
        notes: Notes string containing "Children: name1, name2, ..."

    Returns:
        List of child names
    """
    if not notes or 'Children:' not in notes:
        return []

    # Extract the children portion
    children_match = re.search(r'Children:\s*([^;]+)', notes)
    if not children_match:
        return []

    children_str = children_match.group(1).strip()

    # Split by comma and clean
    children = []
    for child in children_str.split(','):
        child = child.strip()

        # Skip if it's not a name (contains email, phone, etc.)
        if '@' in child or 'email' in child.lower():
            continue

        # Remove extra info in parentheses or after dashes
        child = re.sub(r'\([^)]*\)', '', child)
        child = re.sub(r'\s*-.*$', '', child)
        child = child.strip()

        # Skip empty or very short names
        if child and len(child) > 2:
            children.append(child)

    return children


def find_person_by_name(name: str, people: Dict) -> Optional[str]:
    """
    Find a person ID by name (flexible matching).

    Args:
        name: Name to search for
        people: Dictionary of all people

    Returns:
        Person ID if found, None otherwise
    """
    name_lower = name.lower().strip()

    # Try exact match first
    for person_id, person in people.items():
        if person['name'].lower() == name_lower:
            return person_id

    # Try first name match
    first_name = name_lower.split()[0] if ' ' in name_lower else name_lower
    matches = []

    for person_id, person in people.items():
        person_name_lower = person['name'].lower()
        person_first = person_name_lower.split()[0] if ' ' in person_name_lower else person_name_lower

        # Match if first names match
        if person_first == first_name:
            matches.append(person_id)
        # Or if the search name is contained in the person name
        elif first_name in person_name_lower or name_lower in person_name_lower:
            matches.append(person_id)

    # Return first match if only one found
    if len(matches) == 1:
        return matches[0]

    # If multiple matches, try to find the best one
    if len(matches) > 1:
        # Prefer matches where full name contains the search term
        for person_id in matches:
            if name_lower in people[person_id]['name'].lower():
                return person_id
        # Otherwise return first match
        return matches[0]

    return None


def establish_parent_child_relationship(parent_id: str, child_id: str, people: Dict) -> bool:
    """
    Establish bidirectional parent-child relationship.

    Args:
        parent_id: Parent's person ID
        child_id: Child's person ID
        people: Dictionary of all people

    Returns:
        True if relationship was newly established
    """
    parent = people[parent_id]
    child = people[child_id]

    changed = False

    # Add child to parent's childrenIds
    if 'childrenIds' not in parent:
        parent['childrenIds'] = []
    if child_id not in parent['childrenIds']:
        parent['childrenIds'].append(child_id)
        changed = True

    # Add parent to child's parentIds
    if 'parentIds' not in child:
        child['parentIds'] = []
    if parent_id not in child['parentIds']:
        child['parentIds'].append(parent_id)
        changed = True

    return changed


def establish_relationships(dry_run: bool = False):
    """
    Establish parent-child relationships from notes.

    Args:
        dry_run: If True, show what would be changed without saving
    """
    print("\n" + "="*80)
    print("👨‍👩‍👧‍👦 ESTABLISH RELATIONSHIPS FROM NOTES")
    print("="*80 + "\n")

    # Load family tree
    family_data = load_family_data()
    people = family_data['family']['people']

    print(f"📊 Total people: {len(people)}\n")

    # Find all people with children in notes
    people_with_children_notes = []

    for person_id, person in people.items():
        notes = person.get('notes', '')
        if 'Children:' in notes:
            children = parse_children_from_notes(notes)
            if children:
                people_with_children_notes.append((person_id, person['name'], children))

    print(f"👤 People with children in notes: {len(people_with_children_notes)}\n")

    # Try to match children and establish relationships
    relationships_added = []
    children_not_found = []

    for parent_id, parent_name, child_names in people_with_children_notes:
        for child_name in child_names:
            child_id = find_person_by_name(child_name, people)

            if child_id:
                # Check if relationship already exists
                parent = people[parent_id]
                existing = child_id in parent.get('childrenIds', [])

                if not existing:
                    if not dry_run:
                        changed = establish_parent_child_relationship(parent_id, child_id, people)
                        if changed:
                            relationships_added.append((parent_name, people[child_id]['name']))
                    else:
                        relationships_added.append((parent_name, people[child_id]['name']))
            else:
                children_not_found.append((parent_name, child_name))

    # Summary
    print("="*80)
    print("📊 SUMMARY")
    print("="*80 + "\n")

    if relationships_added:
        print(f"✨ Relationships established: {len(relationships_added)}\n")

        # Group by parent
        by_parent = {}
        for parent_name, child_name in relationships_added:
            if parent_name not in by_parent:
                by_parent[parent_name] = []
            by_parent[parent_name].append(child_name)

        for parent_name, children in sorted(by_parent.items()):
            print(f"{parent_name}:")
            for child_name in children:
                print(f"  → {child_name}")
    else:
        print("No new relationships to establish")

    if children_not_found:
        print(f"\n❓ Children not found in tree: {len(children_not_found)}")
        # Show first 10
        for parent_name, child_name in children_not_found[:10]:
            print(f"  {parent_name} → {child_name}")
        if len(children_not_found) > 10:
            print(f"  ... and {len(children_not_found) - 10} more")

    if dry_run:
        print("\n🔍 DRY RUN - No changes saved")
        print("Run without --dry-run to save changes")
    else:
        if relationships_added:
            family_data['family']['people'] = people
            save_family_data(family_data)
            print("\n✅ Relationships established successfully!")
        else:
            print("\n✅ No changes needed")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Establish parent-child relationships from notes'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )

    args = parser.parse_args()

    establish_relationships(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
