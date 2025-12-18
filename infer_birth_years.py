#!/usr/bin/env python3
"""
Script to infer birth years for people based on family relationships.

Inference rules:
1. From parents: Children are typically 20-40 years younger than parents
2. From spouses: Spouses are typically within ±5 years of each other
3. From siblings: Siblings are typically within ±15 years of each other
4. From children: Parents are typically 20-40 years older than children

The script processes in multiple passes until no more inferences can be made.
"""

import json
import re
from typing import Optional, Dict, List, Tuple


def load_family_data():
    """Load the family tree JSON data."""
    with open('family_tree.json', 'r') as f:
        return json.load(f)


def save_family_data(data):
    """Save the family tree JSON data."""
    with open('family_tree.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n💾 Saved updated family tree to family_tree.json")


def extract_year(dob: str) -> Optional[int]:
    """
    Extract birth year from various DOB formats.

    Args:
        dob: Date of birth string (e.g., "1985", "08-19", "1985-03-08")

    Returns:
        Birth year as integer, or None if not found
    """
    if not dob or dob in ['Unknown', 'unknown', 'alive']:
        return None

    # Try to extract 4-digit year
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', str(dob))
    if year_match:
        return int(year_match.group(1))

    # Check if it's just a year
    if dob.isdigit() and len(dob) == 4:
        return int(dob)

    return None


def has_month_day(dob: str) -> bool:
    """Check if DOB has month and day but no year (e.g., '08-19')."""
    if not dob or dob in ['Unknown', 'unknown']:
        return False

    # Pattern like "08-19" or "MM-DD"
    if re.match(r'^\d{2}-\d{2}$', str(dob)):
        return True

    return False


def update_dob_with_year(dob: str, year: int) -> str:
    """
    Update DOB string with inferred year.

    Args:
        dob: Current DOB (e.g., "08-19" or "Unknown")
        year: Inferred year

    Returns:
        Updated DOB string
    """
    if has_month_day(dob):
        # Already has month-day, prepend year
        return f"{year}-{dob}"
    else:
        # Just set the year
        return str(year)


def infer_from_parents(person_id: str, person: Dict, people: Dict) -> Optional[int]:
    """
    Infer birth year from parents (children are 20-40 years younger).

    Returns:
        Inferred year or None
    """
    parent_ids = person.get('parentIds', [])
    if not parent_ids:
        return None

    parent_years = []
    for parent_id in parent_ids:
        if parent_id in people:
            parent = people[parent_id]
            parent_year = extract_year(parent.get('dob'))
            if parent_year:
                parent_years.append(parent_year)

    if parent_years:
        # Use average of parents + typical age of 25-30 when having children
        avg_parent_year = sum(parent_years) // len(parent_years)
        return avg_parent_year + 28  # Midpoint between 20-40

    return None


def infer_from_spouse(person_id: str, person: Dict, people: Dict) -> Optional[int]:
    """
    Infer birth year from spouse (typically within ±5 years).

    Returns:
        Inferred year or None
    """
    spouse_id = person.get('spouseId')
    if not spouse_id or spouse_id not in people:
        return None

    spouse = people[spouse_id]
    spouse_year = extract_year(spouse.get('dob'))

    if spouse_year:
        # Assume same age (could be ±5 years, but we use same for simplicity)
        return spouse_year

    return None


def infer_from_children(person_id: str, person: Dict, people: Dict) -> Optional[int]:
    """
    Infer birth year from children (parents are 20-40 years older).

    Returns:
        Inferred year or None
    """
    children_ids = person.get('childrenIds', [])
    if not children_ids:
        return None

    children_years = []
    for child_id in children_ids:
        if child_id in people:
            child = people[child_id]
            child_year = extract_year(child.get('dob'))
            if child_year:
                children_years.append(child_year)

    if children_years:
        # Use youngest child (max year) - 28 years
        youngest_year = max(children_years)
        return youngest_year - 28

    return None


def infer_from_siblings(person_id: str, person: Dict, people: Dict) -> Optional[int]:
    """
    Infer birth year from siblings (typically within ±15 years).

    Returns:
        Inferred year or None
    """
    sibling_ids = person.get('siblingIds', [])
    if not sibling_ids:
        return None

    sibling_years = []
    for sibling_id in sibling_ids:
        if sibling_id in people:
            sibling = people[sibling_id]
            sibling_year = extract_year(sibling.get('dob'))
            if sibling_year:
                sibling_years.append(sibling_year)

    if sibling_years:
        # Use average of siblings
        avg_sibling_year = sum(sibling_years) // len(sibling_years)
        return avg_sibling_year

    return None


def infer_birth_years(dry_run: bool = False):
    """
    Infer birth years for people with missing years.

    Args:
        dry_run: If True, show what would be changed without saving
    """
    print("\n" + "="*80)
    print("📅 BIRTH YEAR INFERENCE")
    print("="*80 + "\n")

    # Load family tree
    family_data = load_family_data()
    people = family_data['family']['people']

    print(f"📊 Total people: {len(people)}\n")

    # Identify people who need birth years
    needs_year = []
    has_year = []

    for person_id, person in people.items():
        dob = person.get('dob', 'Unknown')
        year = extract_year(dob)

        if year:
            has_year.append((person_id, person['name'], year))
        else:
            needs_year.append((person_id, person['name'], dob))

    print(f"✅ People with birth years: {len(has_year)}")
    print(f"❓ People needing birth years: {len(needs_year)}\n")

    # Inference passes
    inferences = {}
    max_passes = 5

    for pass_num in range(1, max_passes + 1):
        print(f"🔄 Pass {pass_num}:")
        new_inferences = 0

        for person_id, name, dob in needs_year:
            # Skip if already inferred
            if person_id in inferences:
                continue

            person = people[person_id]
            inferred_year = None
            method = None

            # Try inference methods in order of reliability
            # 1. From parents (most reliable)
            inferred_year = infer_from_parents(person_id, person, people)
            if inferred_year:
                method = "parents"

            # 2. From children
            if not inferred_year:
                inferred_year = infer_from_children(person_id, person, people)
                if inferred_year:
                    method = "children"

            # 3. From spouse
            if not inferred_year:
                inferred_year = infer_from_spouse(person_id, person, people)
                if inferred_year:
                    method = "spouse"

            # 4. From siblings
            if not inferred_year:
                inferred_year = infer_from_siblings(person_id, person, people)
                if inferred_year:
                    method = "siblings"

            if inferred_year:
                inferences[person_id] = (inferred_year, method, dob)
                new_inferences += 1

                # Temporarily update for next pass
                people[person_id]['dob'] = update_dob_with_year(dob, inferred_year)

        print(f"   Inferred {new_inferences} birth years")

        if new_inferences == 0:
            print(f"   No more inferences possible\n")
            break

    # Summary
    print("="*80)
    print("📊 INFERENCE SUMMARY")
    print("="*80 + "\n")

    if inferences:
        # Group by method
        by_method = {}
        for person_id, (year, method, old_dob) in inferences.items():
            if method not in by_method:
                by_method[method] = []
            by_method[method].append((people[person_id]['name'], old_dob, year))

        for method, entries in by_method.items():
            print(f"\n{method.upper()} ({len(entries)} people):")
            for name, old_dob, year in sorted(entries, key=lambda x: x[2]):
                print(f"  {name}: {old_dob} → {year}")

        print(f"\n✨ Total inferences: {len(inferences)}")
        print(f"📅 Remaining without years: {len(needs_year) - len(inferences)}")
    else:
        print("No birth years could be inferred.")

    if dry_run:
        print("\n🔍 DRY RUN - No changes saved")
        print("Run without --dry-run to save changes")
    else:
        # Reload original data and apply inferences
        family_data = load_family_data()
        people = family_data['family']['people']

        for person_id, (year, method, old_dob) in inferences.items():
            people[person_id]['dob'] = update_dob_with_year(old_dob, year)

        family_data['family']['people'] = people
        save_family_data(family_data)
        print("\n✅ Family tree updated with inferred birth years!")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Infer birth years based on family relationships'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be inferred without making changes'
    )

    args = parser.parse_args()

    infer_birth_years(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
