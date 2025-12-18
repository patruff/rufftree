#!/usr/bin/env python3
"""
Script to deduplicate women who appear twice (maiden name and married name).

System:
- Use maiden name as primary "name" field (e.g., "Debbie Miller")
- Store married name in "marriedName" field (e.g., "Ruff")
- This shows their birth identity while preserving married name info
"""

import json
from typing import Dict, List, Tuple


def load_family_data():
    """Load the family tree JSON data."""
    with open('family_tree.json', 'r') as f:
        return json.load(f)


def save_family_data(data):
    """Save the family tree JSON data."""
    with open('family_tree.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n💾 Saved updated family tree to family_tree.json")


def merge_duplicate_person(from_id: str, to_id: str, people: Dict) -> bool:
    """
    Merge duplicate person entries.

    Args:
        from_id: Person ID to merge from (will be deleted)
        to_id: Person ID to merge into (will be kept)
        people: Dictionary of all people

    Returns:
        True if merge was successful
    """
    if from_id not in people or to_id not in people:
        return False

    from_person = people[from_id]
    to_person = people[to_id]

    # Merge data - prefer non-empty values
    for key, value in from_person.items():
        if key == 'id':
            continue
        if value and value not in ['Unknown', 'unknown', '']:
            if key not in to_person or to_person[key] in ['Unknown', 'unknown', '']:
                to_person[key] = value
            elif key in ['childrenIds', 'parentIds', 'siblingIds']:
                # Merge lists
                if key not in to_person:
                    to_person[key] = []
                for item in value:
                    if item not in to_person[key]:
                        to_person[key].append(item)

    # Update all references to from_id
    for person_id, person in people.items():
        # Update spouse references
        if person.get('spouseId') == from_id:
            person['spouseId'] = to_id

        # Update parent references
        if 'parentIds' in person:
            person['parentIds'] = [to_id if pid == from_id else pid for pid in person['parentIds']]

        # Update children references
        if 'childrenIds' in person:
            person['childrenIds'] = [to_id if cid == from_id else cid for cid in person['childrenIds']]

        # Update sibling references
        if 'siblingIds' in person:
            person['siblingIds'] = [to_id if sid == from_id else sid for sid in person['siblingIds']]

    # Delete the duplicate
    del people[from_id]

    return True


def deduplicate_women():
    """Deduplicate women who appear with both maiden and married names."""
    print("\n" + "="*80)
    print("👰 DEDUPLICATING WOMEN WITH MAIDEN NAMES")
    print("="*80 + "\n")

    family_data = load_family_data()
    people = family_data['family']['people']

    deduplication_plan = [
        # (maiden_id, married_id, maiden_name, married_surname)
        ('debbie_miller', 'debbie', 'Debbie Miller', 'Ruff'),
    ]

    fixes = []

    for maiden_id, married_id, correct_name, married_surname in deduplication_plan:
        if maiden_id in people and married_id in people:
            maiden_person = people[maiden_id]
            married_person = people[married_id]

            # Keep the entry with more data (usually the married one has children)
            if len(married_person.get('childrenIds', [])) > 0:
                # Keep married entry, but update to use maiden name
                married_person['name'] = correct_name
                married_person['maidenName'] = correct_name.split()[-1]
                married_person['marriedName'] = married_surname

                # Merge any data from maiden entry
                if maiden_person.get('dob') and married_person.get('dob') == 'Unknown':
                    married_person['dob'] = maiden_person['dob']

                # Merge spouse if needed
                if maiden_person.get('spouseId') and not married_person.get('spouseId'):
                    married_person['spouseId'] = maiden_person['spouseId']

                # Delete the maiden duplicate
                merge_duplicate_person(maiden_id, married_id, people)

                fixes.append(f"Merged {maiden_id} into {married_id}: now '{correct_name}' (married: {married_surname})")
            else:
                # Keep maiden entry, merge married data into it
                maiden_person['name'] = correct_name
                maiden_person['maidenName'] = correct_name.split()[-1]
                maiden_person['marriedName'] = married_surname

                # Merge data from married entry
                for key, value in married_person.items():
                    if key != 'id' and value and key not in maiden_person:
                        maiden_person[key] = value

                merge_duplicate_person(married_id, maiden_id, people)

                fixes.append(f"Merged {married_id} into {maiden_id}: now '{correct_name}' (married: {married_surname})")

    # Fix Beth Miller Bradley
    beth_id = 'beth_bradley'
    if beth_id in people:
        beth = people[beth_id]
        beth['name'] = 'Beth Miller'
        beth['maidenName'] = 'Miller'
        beth['marriedName'] = 'Bradley'
        fixes.append("Fixed Beth Miller Bradley → Beth Miller (married: Bradley)")

    # Look for other women who might need fixing
    # Women with "maidenName" that's actually a full name instead of just surname
    for person_id, person in people.items():
        maiden = person.get('maidenName', '')
        if maiden and ' ' in maiden:
            # Extract just the surname
            surname = maiden.split()[-1]
            person['maidenName'] = surname
            fixes.append(f"Fixed maidenName for {person['name']}: '{maiden}' → '{surname}'")

    # Save
    if fixes:
        print("✨ Fixes applied:\n")
        for fix in fixes:
            print(f"  • {fix}")

        family_data['family']['people'] = people
        save_family_data(family_data)

        # Show examples
        print("\n" + "="*80)
        print("📋 EXAMPLE WOMEN WITH MAIDEN NAMES")
        print("="*80 + "\n")

        examples = [
            ('debbie', 'Debbie Miller'),
            ('beth_bradley', 'Beth Miller'),
            ('mary_ruff', 'Mary Ruff'),
            ('anne_ruff', 'Anne Ruff'),
        ]

        for person_id, expected_name in examples:
            if person_id in people:
                person = people[person_id]
                maiden = person.get('maidenName', 'None')
                married = person.get('marriedName', 'None')
                spouse_id = person.get('spouseId', '')
                spouse_name = people[spouse_id]['name'] if spouse_id in people else 'None'

                print(f"{person['name']:25} married {spouse_name:25}")
                print(f"  Maiden: {maiden:15} Married: {married:15}")
                print()

        print("✅ Women now use maiden names as primary identity!")
    else:
        print("No fixes needed")


def find_miller_lineage():
    """Find and document the Miller lineage."""
    print("\n" + "="*80)
    print("👨‍👩‍👧‍👦 MILLER FAMILY LINEAGE")
    print("="*80 + "\n")

    family_data = load_family_data()
    people = family_data['family']['people']

    # Find all Millers
    millers = []
    for person_id, person in people.items():
        name = person['name']
        maiden = person.get('maidenName', '')

        if 'miller' in name.lower() or maiden.lower() == 'miller':
            millers.append((person_id, person))

    if millers:
        print(f"Found {len(millers)} Miller family members:\n")

        for person_id, person in sorted(millers, key=lambda x: x[1].get('dob', 'ZZZ')):
            name = person['name']
            dob = person.get('dob', 'Unknown')
            spouse_id = person.get('spouseId', '')
            spouse_name = people[spouse_id]['name'] if spouse_id in people else 'None'
            married_name = person.get('marriedName', '')

            if married_name:
                print(f"{name:25} (née Miller, now {married_name})")
            else:
                print(f"{name:25}")
            print(f"  Born: {dob:15} Married to: {spouse_name}")
            print()


def main():
    """Main entry point."""
    deduplicate_women()
    find_miller_lineage()


if __name__ == '__main__':
    main()
