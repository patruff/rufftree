#!/usr/bin/env python3
"""
Script to update generation assignments based on birth years.

Uses standard generational ranges:
- Greatest Generation: Before 1928
- Silent Generation: 1928-1945
- Baby Boomer: 1946-1964
- Gen X: 1965-1980
- Millennial: 1981-1996
- Gen Z: 1997-2012
- Gen Alpha: 2013+
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


def extract_year(dob):
    """Extract birth year from DOB string."""
    if not dob:
        return None
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', str(dob))
    return int(year_match.group(1)) if year_match else None


def get_generation_from_year(year):
    """
    Get generation name from birth year.

    Args:
        year: Birth year as integer

    Returns:
        Generation name
    """
    if not year:
        return None

    if year < 1928:
        return 'Greatest Generation'
    elif 1928 <= year <= 1945:
        return 'Silent Generation'
    elif 1946 <= year <= 1964:
        return 'Baby Boomer'
    elif 1965 <= year <= 1980:
        return 'Gen X'
    elif 1981 <= year <= 1996:
        return 'Millennial'
    elif 1997 <= year <= 2012:
        return 'Gen Z'
    else:  # 2013+
        return 'Gen Alpha'


def update_generations():
    """Update all generation assignments based on birth years."""
    print("\n" + "="*80)
    print("👥 UPDATING GENERATION ASSIGNMENTS")
    print("="*80 + "\n")

    family_data = load_family_data()
    people = family_data['family']['people']

    updates = {
        'Greatest Generation': [],
        'Silent Generation': [],
        'Baby Boomer': [],
        'Gen X': [],
        'Millennial': [],
        'Gen Z': [],
        'Gen Alpha': [],
        'No Change': []
    }

    total_updated = 0

    for person_id, person in people.items():
        name = person['name']
        dob = person.get('dob')
        year = extract_year(dob)

        if not year:
            # No birth year, can't assign generation
            continue

        correct_gen = get_generation_from_year(year)
        current_gen = person.get('generation')

        if current_gen != correct_gen:
            person['generation'] = correct_gen
            updates[correct_gen].append((name, year, current_gen or 'None'))
            total_updated += 1
        else:
            updates['No Change'].append((name, year))

    # Display results
    print("📊 Generation Updates:\n")

    for gen in ['Greatest Generation', 'Silent Generation', 'Baby Boomer',
                'Gen X', 'Millennial', 'Gen Z', 'Gen Alpha']:
        if updates[gen]:
            print(f"{gen} ({len(updates[gen])} people):")
            for name, year, old_gen in sorted(updates[gen], key=lambda x: x[1]):
                print(f"  {name:30} Born {year} (was: {old_gen})")
            print()

    print(f"✅ No changes needed: {len(updates['No Change'])} people")
    print(f"\n📈 Total updates: {total_updated}")

    if total_updated > 0:
        family_data['family']['people'] = people
        save_family_data(family_data)
        print("\n✅ All generations updated successfully!")
    else:
        print("\n✅ All generations already correct!")

    # Show summary by generation
    print("\n" + "="*80)
    print("📊 GENERATION DISTRIBUTION")
    print("="*80 + "\n")

    gen_counts = {}
    for person in people.values():
        gen = person.get('generation', 'Unknown')
        gen_counts[gen] = gen_counts.get(gen, 0) + 1

    for gen in ['Greatest Generation', 'Silent Generation', 'Baby Boomer',
                'Gen X', 'Millennial', 'Gen Z', 'Gen Alpha', 'Unknown']:
        count = gen_counts.get(gen, 0)
        if count > 0:
            print(f"{gen:25} {count:3} people")


def main():
    """Main entry point."""
    update_generations()


if __name__ == '__main__':
    main()
