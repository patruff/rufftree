#!/usr/bin/env python3
"""
Script to extract a person's immediate family tree.
Input a person's name and get their parents, siblings, and children.
"""

import json
import sys
from typing import Optional, Dict, List


def load_family_data():
    """Load the family tree JSON data."""
    with open('family_tree.json', 'r') as f:
        return json.load(f)


def search_person(name: str, people: Dict) -> Optional[tuple]:
    """
    Search for a person by name (flexible matching).

    Args:
        name: Full name or partial name to search for
        people: Dictionary of all people

    Returns:
        Tuple of (person_id, person_data) if found, None otherwise
    """
    name_lower = name.lower()

    # First try exact match
    for person_id, person in people.items():
        if person['name'].lower() == name_lower:
            return (person_id, person)

    # Then try partial match
    matches = []
    for person_id, person in people.items():
        if name_lower in person['name'].lower():
            matches.append((person_id, person))

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(f"\nMultiple matches found for '{name}':")
        for i, (pid, p) in enumerate(matches, 1):
            dod_text = p['dod'] if p['dod'] != 'alive' else 'Present'
            print(f"  {i}. {p['name']} ({p['dob']} - {dod_text})")

        try:
            choice = int(input("\nEnter number to select: "))
            if 1 <= choice <= len(matches):
                return matches[choice - 1]
        except (ValueError, IndexError):
            pass

    return None


def format_person_info(person: Dict, person_id: str) -> str:
    """Format a person's basic info for display."""
    name = person['name']
    dob = person['dob']
    dod = person['dod'] if person['dod'] != 'alive' else 'Present'

    age_info = ""
    if person['dod'] == 'alive':
        try:
            current_year = 2024
            age = current_year - int(dob)
            age_info = f" (age {age})"
        except:
            pass
    else:
        try:
            years_lived = int(person['dod']) - int(dob)
            age_info = f" (lived {years_lived} years)"
        except:
            pass

    # Add generation if available
    gen_info = ""
    if 'generation' in person:
        gen_info = f" - {person['generation']}"

    # Add location if available
    location_info = ""
    if person.get('home_city') or person.get('home_state'):
        location = ', '.join(filter(None, [person.get('home_city'), person.get('home_state')]))
        location_info = f" - {location}"

    return f"{name} ({dob} - {dod}{age_info}){gen_info}{location_info}"


def get_immediate_family(person_id: str, person: Dict, people: Dict) -> Dict:
    """
    Extract immediate family tree for a person.

    Returns:
        Dictionary with parents, siblings, spouse, and children
    """
    family_tree = {
        'person': {
            'id': person_id,
            'info': format_person_info(person, person_id),
            'data': person
        },
        'parents': [],
        'siblings': [],
        'spouse': None,
        'children': []
    }

    # Get parents
    for parent_id in person.get('parentIds', []):
        if parent_id in people:
            parent = people[parent_id]
            family_tree['parents'].append({
                'id': parent_id,
                'info': format_person_info(parent, parent_id),
                'data': parent
            })

    # Get siblings
    for sibling_id in person.get('siblingIds', []):
        if sibling_id in people:
            sibling = people[sibling_id]
            family_tree['siblings'].append({
                'id': sibling_id,
                'info': format_person_info(sibling, sibling_id),
                'data': sibling
            })

    # Get spouse
    spouse_id = person.get('spouseId')
    if spouse_id and spouse_id in people:
        spouse = people[spouse_id]
        family_tree['spouse'] = {
            'id': spouse_id,
            'info': format_person_info(spouse, spouse_id),
            'data': spouse
        }

    # Get children
    for child_id in person.get('childrenIds', []):
        if child_id in people:
            child = people[child_id]
            family_tree['children'].append({
                'id': child_id,
                'info': format_person_info(child, child_id),
                'data': child
            })

    return family_tree


def display_family_tree(family_tree: Dict):
    """Display the family tree in a readable format."""
    print("\n" + "=" * 80)
    print("IMMEDIATE FAMILY TREE")
    print("=" * 80)

    # Main person
    print(f"\n👤 PERSON:")
    print(f"   {family_tree['person']['info']}")

    # Parents
    if family_tree['parents']:
        print(f"\n👨‍👩 PARENTS ({len(family_tree['parents'])}):")
        for parent in family_tree['parents']:
            print(f"   • {parent['info']}")
    else:
        print(f"\n👨‍👩 PARENTS: None recorded")

    # Spouse
    if family_tree['spouse']:
        print(f"\n💑 SPOUSE:")
        print(f"   • {family_tree['spouse']['info']}")
    else:
        print(f"\n💑 SPOUSE: None recorded")

    # Siblings
    if family_tree['siblings']:
        print(f"\n👥 SIBLINGS ({len(family_tree['siblings'])}):")
        for sibling in family_tree['siblings']:
            print(f"   • {sibling['info']}")
    else:
        print(f"\n👥 SIBLINGS: None recorded")

    # Children
    if family_tree['children']:
        print(f"\n👶 CHILDREN ({len(family_tree['children'])}):")
        for child in family_tree['children']:
            print(f"   • {child['info']}")
    else:
        print(f"\n👶 CHILDREN: None recorded")

    print("\n" + "=" * 80)


def create_focused_json(family_tree: Dict, output_file: str):
    """Create a focused JSON file with just this person's immediate family."""
    focused_data = {
        'person': family_tree['person']['data'],
        'parents': [p['data'] for p in family_tree['parents']],
        'siblings': [s['data'] for s in family_tree['siblings']],
        'spouse': family_tree['spouse']['data'] if family_tree['spouse'] else None,
        'children': [c['data'] for c in family_tree['children']]
    }

    with open(output_file, 'w') as f:
        json.dump(focused_data, f, indent=2)

    print(f"\n✅ Focused family tree saved to: {output_file}")


def main():
    """Main function to run the immediate family tree extraction."""
    # Load data
    print("Loading family tree data...")
    data = load_family_data()
    people = data['family']['people']
    print(f"Loaded {len(people)} family members.")

    # Get name input
    if len(sys.argv) > 1:
        # Name provided as command-line argument
        search_name = ' '.join(sys.argv[1:])
    else:
        # Prompt for name
        search_name = input("\nEnter person's name (first and last, or partial): ").strip()

    if not search_name:
        print("Error: No name provided.")
        sys.exit(1)

    # Search for person
    print(f"\nSearching for '{search_name}'...")
    result = search_person(search_name, people)

    if not result:
        print(f"\n❌ No match found for '{search_name}'")
        print("\nTip: Try searching by first name only, or check spelling.")
        sys.exit(1)

    person_id, person = result
    print(f"✅ Found: {person['name']}")

    # Get immediate family
    family_tree = get_immediate_family(person_id, person, people)

    # Display results
    display_family_tree(family_tree)

    # Ask if user wants to save to file
    save_choice = input("\nSave this family tree to a JSON file? (y/n): ").strip().lower()
    if save_choice == 'y':
        # Create safe filename from person's name
        safe_name = person['name'].lower().replace(' ', '_').replace("'", "")
        output_file = f"{safe_name}_family_tree.json"
        create_focused_json(family_tree, output_file)


if __name__ == '__main__':
    main()
