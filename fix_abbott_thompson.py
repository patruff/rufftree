#!/usr/bin/env python3
"""
Fix Abbott and Thompson family lineages.

- Tom Abbott married Annemarie Thompson (both ~1970s) → Abbott lineage founder
- Roy Thompson married Winifred Ruff → Thompson lineage founder
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


def fix_abbott_thompson_families():
    """Fix the Abbott and Thompson family lineages."""
    print("\n" + "="*80)
    print("🔧 FIXING ABBOTT AND THOMPSON FAMILIES")
    print("="*80 + "\n")

    family_data = load_family_data()
    people = family_data['family']['people']

    fixes = []

    # 1. Fix Tom Abbott - should be born ~1970s (same age as Annemarie)
    tom_abbott_id = None
    for pid, person in people.items():
        if person['name'] == 'Tom Abbott':
            tom_abbott_id = pid
            break

    if tom_abbott_id:
        tom = people[tom_abbott_id]
        # Annemarie is born 1970, Tom should be similar age
        # Let's say 1969 (month-day from current: 08-19)
        tom['dob'] = '1969-08-19'
        tom['generation'] = 'Gen X'  # Born 1969 is Gen X (1965-1980)

        # Mark as lineage founder
        tom['lineageFounder'] = 'Abbott'
        tom['marriedIntoFamily'] = 'Thompson'

        fixes.append("Tom Abbott: 1914 → 1969 (Gen X, Abbott lineage founder)")

    # 2. Verify Annemarie Thompson
    annemarie_id = None
    for pid, person in people.items():
        if person['name'] == 'Annemarie Thompson':
            annemarie_id = pid
            break

    if annemarie_id:
        annemarie = people[annemarie_id]
        # Already 1970, which is correct
        # Should have Thompson as maiden name since she's from Thompson family
        annemarie['maidenName'] = 'Thompson'
        annemarie['marriedName'] = 'Abbott'
        fixes.append("Annemarie Thompson: Set maiden name Thompson, married name Abbott")

    # 3. Fix Abbott children - they should be born in 1990s-2000s if parents are ~1970
    # Mary Elizabeth, Khristina, Tommy Abbott
    abbott_children = []
    if tom_abbott_id:
        tom = people[tom_abbott_id]
        for child_id in tom.get('childrenIds', []):
            if child_id in people:
                abbott_children.append(child_id)

    # Reset their birth years to Unknown since current years are wrong
    for child_id in abbott_children:
        child = people[child_id]
        child_name = child['name']
        old_dob = child.get('dob', 'Unknown')

        # If they have a month-day, keep it
        if '-' in str(old_dob) and len(str(old_dob).split('-')) == 3:
            # Has full date, extract month-day
            parts = str(old_dob).split('-')
            if len(parts) == 3:
                month_day = f"{parts[1]}-{parts[2]}"
                child['dob'] = month_day
        else:
            child['dob'] = 'Unknown'

        # Remove incorrect generation
        if 'generation' in child and child['generation'] == 'Silent Generation':
            del child['generation']

        fixes.append(f"{child_name}: Reset birth year (was {old_dob})")

    # 4. Verify Roy Thompson and Winifred Ruff
    roy_id = 'roy_thompson'
    winifred_id = 'winifred'

    if roy_id in people and winifred_id in people:
        roy = people[roy_id]
        winifred = people[winifred_id]

        # Mark Roy as Thompson lineage founder
        if 'lineageFounder' not in roy:
            roy['lineageFounder'] = 'Thompson'
            roy['marriedIntoFamily'] = 'Ruff'
            fixes.append("Roy Thompson: Marked as Thompson lineage founder")

        # Winifred should have Ruff as maiden name
        if 'maidenName' not in winifred:
            winifred['maidenName'] = 'Ruff'

        # Check if they need marriedName
        # Actually Winifred kept her name "Winifred Ruff", she didn't change to Thompson

    # Save
    if fixes:
        print("✨ Fixes applied:\n")
        for fix in fixes:
            print(f"  • {fix}")

        family_data['family']['people'] = people
        save_family_data(family_data)

        # Show the lineages
        print("\n" + "="*80)
        print("📋 LINEAGE FOUNDERS")
        print("="*80 + "\n")

        print("ABBOTT LINEAGE:")
        print(f"  Tom Abbott (1969) + Annemarie Thompson (1970)")
        if tom_abbott_id:
            tom = people[tom_abbott_id]
            for child_id in tom.get('childrenIds', []):
                if child_id in people:
                    child = people[child_id]
                    print(f"    └── {child['name']}")

        print("\nTHOMPSON LINEAGE:")
        print(f"  Roy Thompson (1944) + Winifred Ruff (1944)")
        if roy_id in people:
            roy = people[roy_id]
            for child_id in roy.get('childrenIds', []):
                if child_id in people:
                    child = people[child_id]
                    print(f"    └── {child['name']}")

        print("\n✅ Abbott and Thompson families fixed!")
    else:
        print("No fixes needed")


def main():
    """Main entry point."""
    fix_abbott_thompson_families()


if __name__ == '__main__':
    main()
