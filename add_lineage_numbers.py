#!/usr/bin/env python3
"""
Script to add integer-based lineage tracking for families with same names across generations.

The lineage field is an integer that tracks which generation of the same name a person is:
- Joseph Ruff Sr. = lineage 1 (first generation of that name)
- Joe Ruff Jr. = lineage 2 (second generation)
- Any future Joe Ruff III = lineage 3 (third generation)

This is cleaner than string suffixes and makes it easy to query and calculate relationships.
"""

import json
import re
from typing import Dict, List, Tuple, Optional


def load_family_data():
    """Load the family tree JSON data."""
    with open('family_tree.json', 'r') as f:
        return json.load(f)


def save_family_data(data):
    """Save the family tree JSON data."""
    with open('family_tree.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n💾 Saved updated family tree to family_tree.json")


def get_base_name(full_name: str) -> Tuple[str, str]:
    """
    Extract base first name and surname, removing suffixes.

    Args:
        full_name: Full name like "Joe Ruff Sr." or "Bobby Cathell III"

    Returns:
        Tuple of (base_first_name, surname)

    Examples:
        "Joe Ruff Sr." -> ("Joe", "Ruff")
        "Bobby Cathell Jr" -> ("Bobby", "Cathell")
        "Patrick Ruff" -> ("Patrick", "Ruff")
    """
    # Remove suffixes
    name_clean = re.sub(r'\s+(Sr\.?|Jr\.?|III|IV|V|Senior|Junior)$', '', full_name, flags=re.IGNORECASE)

    # Split into parts
    parts = name_clean.split()

    if len(parts) >= 2:
        surname = parts[-1]
        first_name = parts[0]
        return (first_name, surname)
    elif len(parts) == 1:
        return (parts[0], '')
    else:
        return ('', '')


def calculate_lineage_numbers():
    """
    Calculate lineage numbers for people with the same name across generations.
    """
    print("\n" + "="*80)
    print("🔢 CALCULATING LINEAGE NUMBERS")
    print("="*80 + "\n")

    family_data = load_family_data()
    people = family_data['family']['people']

    # Group people by base name and surname
    name_groups: Dict[Tuple[str, str], List[str]] = {}

    for person_id, person in people.items():
        full_name = person['name']
        base_first, surname = get_base_name(full_name)

        if base_first and surname:
            key = (base_first.lower(), surname.lower())
            if key not in name_groups:
                name_groups[key] = []
            name_groups[key].append(person_id)

    # Process groups with multiple people (same name across generations)
    lineage_assignments = []

    for (first_name, surname), person_ids in name_groups.items():
        if len(person_ids) < 2:
            continue  # Skip single-person names

        # Sort by generation (oldest first)
        # Use parent relationships to determine order
        ordered_ids = []
        remaining_ids = set(person_ids)

        # Find the root (person with no parents who match this name pattern)
        for person_id in person_ids:
            person = people[person_id]
            parent_ids = person.get('parentIds', [])

            # Check if any parent has the same base name
            has_parent_with_same_name = False
            for parent_id in parent_ids:
                if parent_id in people:
                    parent = people[parent_id]
                    parent_first, parent_surname = get_base_name(parent['name'])
                    if parent_first.lower() == first_name and parent_surname.lower() == surname:
                        has_parent_with_same_name = True
                        break

            if not has_parent_with_same_name:
                ordered_ids.append(person_id)
                remaining_ids.remove(person_id)

        # Now add children recursively
        def add_children_recursive(parent_id):
            """Add children who have the same base name."""
            parent = people[parent_id]
            for child_id in parent.get('childrenIds', []):
                if child_id in remaining_ids:
                    child = people[child_id]
                    child_first, child_surname = get_base_name(child['name'])
                    if child_first.lower() == first_name and child_surname.lower() == surname:
                        ordered_ids.append(child_id)
                        remaining_ids.remove(child_id)
                        add_children_recursive(child_id)

        for person_id in list(ordered_ids):
            add_children_recursive(person_id)

        # Add any remaining (couldn't determine order, use birth year)
        if remaining_ids:
            # Sort remaining by birth year
            remaining_sorted = sorted(
                remaining_ids,
                key=lambda pid: people[pid].get('dob', 'Unknown')
            )
            ordered_ids.extend(remaining_sorted)

        # Assign lineage numbers
        for lineage_num, person_id in enumerate(ordered_ids, start=1):
            person = people[person_id]
            person['lineage'] = lineage_num

            # Update suffix to match lineage
            if lineage_num == 1:
                suffix = 'Sr'
            elif lineage_num == 2:
                suffix = 'Jr'
            elif lineage_num == 3:
                suffix = 'III'
            elif lineage_num == 4:
                suffix = 'IV'
            elif lineage_num == 5:
                suffix = 'V'
            else:
                suffix = f'{lineage_num}th'

            person['suffix'] = suffix

            lineage_assignments.append((
                person['name'],
                f"{first_name.title()} {surname.title()}",
                lineage_num,
                suffix
            ))

    # Display results
    if lineage_assignments:
        print("✨ Lineage numbers assigned:\n")

        # Group by base name for display
        from collections import defaultdict
        by_base_name = defaultdict(list)

        for full_name, base_name, lineage, suffix in lineage_assignments:
            by_base_name[base_name].append((full_name, lineage, suffix))

        for base_name, entries in sorted(by_base_name.items()):
            print(f"{base_name} lineage:")
            for full_name, lineage, suffix in sorted(entries, key=lambda x: x[1]):
                print(f"  {lineage} ({suffix}): {full_name}")
            print()

        print(f"Total lineages assigned: {len(lineage_assignments)}")

        # Save
        family_data['family']['people'] = people
        save_family_data(family_data)
        print("\n✅ Lineage numbers calculated and saved!")
    else:
        print("No multi-generation same-name families found")


def show_lineage_examples():
    """Show some example lineages."""
    family_data = load_family_data()
    people = family_data['family']['people']

    print("\n" + "="*80)
    print("📋 EXAMPLE LINEAGES")
    print("="*80 + "\n")

    # Find some examples
    examples = []

    for person_id, person in people.items():
        if person.get('lineage'):
            lineage = person['lineage']
            suffix = person.get('suffix', '')
            dob = person.get('dob', 'Unknown')
            examples.append((lineage, person['name'], dob, suffix))

    if examples:
        # Group by base name
        from collections import defaultdict
        by_lineage_name = defaultdict(list)

        for lineage, name, dob, suffix in examples:
            base_name = re.sub(r'\s+(Sr\.?|Jr\.?|III|IV|V)$', '', name, flags=re.IGNORECASE)
            by_lineage_name[base_name].append((lineage, name, dob, suffix))

        for base_name, entries in sorted(by_lineage_name.items()):
            if len(entries) >= 2:  # Only show multi-generation families
                print(f"{base_name}:")
                for lineage, name, dob, suffix in sorted(entries):
                    print(f"  lineage={lineage} ({suffix}): {name} (born {dob})")
                print()


def main():
    """Main entry point."""
    calculate_lineage_numbers()
    show_lineage_examples()


if __name__ == '__main__':
    main()
