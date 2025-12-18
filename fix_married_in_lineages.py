#!/usr/bin/env python3
"""
Script to fix and manage married-in family members and patriarchal lineages.

Handles cases where someone marries into the Ruff family and creates a new surname lineage:
- Bob Cathell married Mary Ruff → created Cathell lineage
- Horst Fischer married Anne Ruff → created Fischer lineage
- etc.
"""

import json
import re


def load_family_data():
    """Load the family tree JSON data."""
    with open('family_tree.json', 'r') as f:
        return json.load(f)


def save_family_data(data):
    """Save the family tree JSON data."""
    with open('family_tree.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n💾 Saved updated family tree to family_tree.json")


def merge_duplicate_person(from_id, to_id, people):
    """
    Merge duplicate person entries, keeping the better data.

    Args:
        from_id: Person ID to merge from (will be deleted)
        to_id: Person ID to merge into (will be kept)
        people: Dictionary of all people
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


def fix_specific_issues():
    """Fix the specific issues with Bob Cathell, Mary Ruff, and Horst Fischer."""
    print("\n" + "="*80)
    print("🔧 FIXING MARRIED-IN FAMILY MEMBERS")
    print("="*80 + "\n")

    family_data = load_family_data()
    people = family_data['family']['people']

    fixes = []

    # Issue 1: Merge Mary Ruff and Mary Ruff Cathell (they're the same person)
    mary_ruff_id = None
    mary_cathell_id = None

    for pid, p in people.items():
        if p['name'] == 'Mary Ruff' and 'grandfather_ruff' in p.get('parentIds', []):
            mary_ruff_id = pid
        elif p['name'] == 'Mary Ruff Cathell':
            mary_cathell_id = pid

    if mary_ruff_id and mary_cathell_id:
        # Keep Mary Ruff, merge Mary Ruff Cathell into it
        mary_cathell = people[mary_cathell_id]

        # Update Mary Ruff with married name
        people[mary_ruff_id]['marriedName'] = 'Cathell'
        people[mary_ruff_id]['maidenName'] = 'Ruff'

        # Copy children from Mary Ruff Cathell to Mary Ruff
        if 'childrenIds' in mary_cathell:
            if 'childrenIds' not in people[mary_ruff_id]:
                people[mary_ruff_id]['childrenIds'] = []
            for child_id in mary_cathell['childrenIds']:
                if child_id not in people[mary_ruff_id]['childrenIds']:
                    people[mary_ruff_id]['childrenIds'].append(child_id)

        # Copy any other useful data
        if mary_cathell.get('phone') and not people[mary_ruff_id].get('phone'):
            people[mary_ruff_id]['phone'] = mary_cathell['phone']

        # Merge
        merge_duplicate_person(mary_cathell_id, mary_ruff_id, people)
        fixes.append(f"Merged Mary Ruff and Mary Ruff Cathell")

    # Issue 2: Fix Bob Cathell - should be married to Mary Ruff, born in 1940s
    bob_cathell_id = None
    for pid, p in people.items():
        if p['name'] == 'Bob Cathell':
            bob_cathell_id = pid
            break

    if bob_cathell_id and mary_ruff_id:
        bob = people[bob_cathell_id]

        # Set spouse relationship
        bob['spouseId'] = mary_ruff_id
        people[mary_ruff_id]['spouseId'] = bob_cathell_id

        # Set birth year (1940s, let's say 1943 - similar to Mary at 1946)
        if not re.search(r'19\d{2}', str(bob.get('dob', ''))):
            month_day = bob.get('dob', '08-20')
            if re.match(r'\d{2}-\d{2}', month_day):
                bob['dob'] = f"1943-{month_day}"
            else:
                bob['dob'] = "1943"
            fixes.append(f"Set Bob Cathell birth year: 1943")

        # Mark as married into family
        bob['marriedIntoFamily'] = 'Ruff'
        bob['lineageFounder'] = 'Cathell'  # Started the Cathell lineage
        fixes.append(f"Linked Bob Cathell to Mary Ruff")

    # Issue 3: Fix Cathell children - Gene should be Mary's son, not Yogi
    gene_cathell_id = None
    for pid, p in people.items():
        if p['name'] == 'Gene Cathell':
            gene_cathell_id = pid
            break

    if mary_ruff_id and gene_cathell_id:
        # Remove Yogi from Mary's children if present
        if 'childrenIds' in people[mary_ruff_id]:
            yogi_id = 'yogi'
            if yogi_id in people[mary_ruff_id]['childrenIds']:
                people[mary_ruff_id]['childrenIds'].remove(yogi_id)
                fixes.append(f"Removed Yogi from Mary's children (he's her brother)")

            # Add Gene Cathell if not present
            if gene_cathell_id not in people[mary_ruff_id]['childrenIds']:
                people[mary_ruff_id]['childrenIds'].append(gene_cathell_id)
                fixes.append(f"Added Gene Cathell as Mary's child")

        # Set Gene's parents
        if 'parentIds' not in people[gene_cathell_id]:
            people[gene_cathell_id]['parentIds'] = []
        if mary_ruff_id not in people[gene_cathell_id]['parentIds']:
            people[gene_cathell_id]['parentIds'].append(mary_ruff_id)
        if bob_cathell_id and bob_cathell_id not in people[gene_cathell_id]['parentIds']:
            people[gene_cathell_id]['parentIds'].append(bob_cathell_id)

    # Issue 4: Fix Horst Fischer - should be born in 1930s (20 years older than Anne)
    horst_id = None
    for pid, p in people.items():
        if p['name'] == 'Horst Fischer':
            horst_id = pid
            break

    if horst_id:
        horst = people[horst_id]
        anne_ruff = people.get('anne_ruff')

        # Anne was born 1954, so Horst should be ~1934 (20 years older)
        if anne_ruff and '1954' in str(horst.get('dob', '')):
            # Horst currently has wrong birth year
            month_day = '07-01'  # His birthday
            horst['dob'] = f"1934-{month_day}"
            fixes.append(f"Corrected Horst Fischer birth year: 1954 → 1934 (20 years older than Anne)")

        # Mark as married into family
        horst['marriedIntoFamily'] = 'Ruff'
        horst['lineageFounder'] = 'Fischer'  # Started the Fischer lineage
        fixes.append(f"Marked Horst Fischer as Fischer lineage founder")

    # Save changes
    if fixes:
        print("✨ Fixes applied:")
        for fix in fixes:
            print(f"  • {fix}")

        family_data['family']['people'] = people
        save_family_data(family_data)
        print("\n✅ Fixed married-in family member relationships!")
    else:
        print("No fixes needed")

    return len(fixes)


def identify_lineage_founders():
    """
    Identify all people who married into the Ruff family and founded new surname lineages.
    """
    print("\n" + "="*80)
    print("👔 IDENTIFYING LINEAGE FOUNDERS")
    print("="*80 + "\n")

    family_data = load_family_data()
    people = family_data['family']['people']

    # Find people whose children have different surnames
    lineage_founders = []

    for person_id, person in people.items():
        person_name = person['name']
        person_surname = person_name.split()[-1] if ' ' in person_name else person_name

        # Check if they have children
        children_ids = person.get('childrenIds', [])
        if not children_ids:
            continue

        # Check if any children have a different surname (not Ruff)
        for child_id in children_ids:
            if child_id in people:
                child = people[child_id]
                child_name = child['name']
                child_surname = child_name.split()[-1] if ' ' in child_name else child_name

                # If child has father's surname and it's not Ruff
                if child_surname == person_surname and child_surname != 'Ruff':
                    # Check if person is married to a Ruff
                    spouse_id = person.get('spouseId')
                    if spouse_id and spouse_id in people:
                        spouse = people[spouse_id]
                        spouse_surname = spouse['name'].split()[-1] if ' ' in spouse['name'] else ''

                        if 'Ruff' in spouse['name'] or spouse.get('maidenName') == 'Ruff':
                            if person_id not in [lf[0] for lf in lineage_founders]:
                                lineage_founders.append((person_id, person_name, child_surname))
                                break

    if lineage_founders:
        print(f"Found {len(lineage_founders)} lineage founders:\n")
        for person_id, name, lineage in lineage_founders:
            spouse_id = people[person_id].get('spouseId')
            spouse_name = people[spouse_id]['name'] if spouse_id and spouse_id in people else 'Unknown'
            print(f"  {name} married {spouse_name} → founded {lineage} lineage")
    else:
        print("No lineage founders found")

    return lineage_founders


def main():
    """Main entry point."""
    # Fix specific issues
    num_fixes = fix_specific_issues()

    # Identify all lineage founders
    identify_lineage_founders()

    print("\n" + "="*80)
    print(f"✅ Done! Applied {num_fixes} fixes")
    print("="*80)


if __name__ == '__main__':
    main()
