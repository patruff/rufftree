#!/usr/bin/env python3
"""
Script to handle Sr/Jr/III naming conventions and add missing family members.
"""

import json


def load_family_data():
    """Load the family tree JSON data."""
    with open('family_tree.json', 'r') as f:
        return json.load(f)


def save_family_data(data):
    """Save the family tree JSON data."""
    with open('family_tree.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n💾 Saved updated family tree to family_tree.json")


def add_bobby_cathell_jr():
    """Add Bobby Cathell Jr as a child of Bob Sr and Mary Ruff."""
    print("\n" + "="*80)
    print("👨‍👦 ADDING SR/JR RELATIONSHIPS")
    print("="*80 + "\n")

    family_data = load_family_data()
    people = family_data['family']['people']

    changes = []

    # 1. Update Bob Cathell to Bob Cathell Sr
    bob_sr_id = 'bob_cathell'
    if bob_sr_id in people:
        bob_sr = people[bob_sr_id]
        if 'Sr' not in bob_sr['name'] and 'Senior' not in bob_sr['name']:
            bob_sr['name'] = 'Bob Cathell Sr'
            bob_sr['suffix'] = 'Sr'
            changes.append("Renamed Bob Cathell → Bob Cathell Sr")

    # 2. Create Bobby Cathell Jr if not exists
    bobby_jr_id = 'bobby_cathell_jr'

    if bobby_jr_id not in people:
        bobby_jr = {
            'id': bobby_jr_id,
            'name': 'Bobby Cathell Jr',
            'suffix': 'Jr',
            'dob': 'Unknown',
            'dod': 'alive',
            'parentIds': ['mary_ruff', 'bob_cathell'],
            'childrenIds': [],
            'siblingIds': ['gene_cathell', 'scott_cathell', 'curtis_cathell']
        }
        people[bobby_jr_id] = bobby_jr
        changes.append("Created Bobby Cathell Jr")

        # 3. Add Bobby Jr to Mary's children
        if 'mary_ruff' in people:
            mary = people['mary_ruff']
            if 'childrenIds' not in mary:
                mary['childrenIds'] = []
            if bobby_jr_id not in mary['childrenIds']:
                mary['childrenIds'].append(bobby_jr_id)
                changes.append("Added Bobby Jr to Mary Ruff's children")

        # 4. Add Bobby Jr to Bob Sr's children
        if bob_sr_id in people:
            bob_sr = people[bob_sr_id]
            if 'childrenIds' not in bob_sr:
                bob_sr['childrenIds'] = []
            if bobby_jr_id not in bob_sr['childrenIds']:
                bob_sr['childrenIds'].append(bobby_jr_id)
                changes.append("Added Bobby Jr to Bob Sr's children")

        # 5. Add Bobby Jr to siblings' sibling lists
        for sibling_id in ['gene_cathell', 'scott_cathell', 'curtis_cathell']:
            if sibling_id in people:
                sibling = people[sibling_id]
                if 'siblingIds' not in sibling:
                    sibling['siblingIds'] = []
                if bobby_jr_id not in sibling['siblingIds']:
                    sibling['siblingIds'].append(bobby_jr_id)

    # 6. Check for Bobby III (grandson) and link to Bobby Jr
    # Bobby III would be mentioned in the notes
    bobby_iii_id = None

    # Check if there's a person with Bobby III in notes or name
    for person_id, person in people.items():
        if 'Bobby III' in person.get('notes', '') or 'III' in person.get('name', ''):
            if 'cathell' in person.get('name', '').lower():
                bobby_iii_id = person_id
                break

    # If Bobby III doesn't exist but is mentioned, create entry
    if not bobby_iii_id and 'Bobby III UD medicine' in people[bob_sr_id].get('notes', ''):
        bobby_iii_id = 'bobby_cathell_iii'
        bobby_iii = {
            'id': bobby_iii_id,
            'name': 'Bobby Cathell III',
            'suffix': 'III',
            'dob': 'Unknown',
            'dod': 'alive',
            'occupation': 'Medical Student (UD)',
            'parentIds': [bobby_jr_id],
            'childrenIds': [],
            'siblingIds': []
        }
        people[bobby_iii_id] = bobby_iii
        changes.append("Created Bobby Cathell III (grandson, UD medicine student)")

        # Add Bobby III to Bobby Jr's children
        if bobby_jr_id in people:
            if 'childrenIds' not in people[bobby_jr_id]:
                people[bobby_jr_id]['childrenIds'] = []
            people[bobby_jr_id]['childrenIds'].append(bobby_iii_id)

    # 7. Handle Paddi H (mentioned in Bob Sr's notes)
    paddi_id = 'paddi_h'
    if paddi_id in people and bobby_jr_id in people:
        paddi = people[paddi_id]
        # Paddi is likely Bobby Jr's wife
        paddi['name'] = 'Paddi Haley Cathell'
        paddi['maidenName'] = 'Haley'
        paddi['spouseId'] = bobby_jr_id
        people[bobby_jr_id]['spouseId'] = paddi_id
        changes.append("Linked Paddi Haley to Bobby Cathell Jr as spouse")

    # Save
    if changes:
        print("✨ Changes made:")
        for change in changes:
            print(f"  • {change}")

        family_data['family']['people'] = people
        save_family_data(family_data)

        # Show the Cathell family tree
        print("\n" + "="*80)
        print("👨‍👩‍👧‍👦 CATHELL FAMILY STRUCTURE")
        print("="*80)
        print("\nBob Cathell Sr + Mary Ruff")
        print("├── Bobby Cathell Jr + Paddi Haley")
        if bobby_iii_id:
            print("│   └── Bobby Cathell III (UD medicine)")
        print("├── Gene Cathell")
        print("├── Scott Cathell")
        print("└── Curtis Cathell")

        print("\n✅ Sr/Jr/III relationships established!")
    else:
        print("No changes needed")

    return len(changes)


def main():
    """Main entry point."""
    add_bobby_cathell_jr()


if __name__ == '__main__':
    main()
