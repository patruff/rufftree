#!/usr/bin/env python3
"""
Calculated Fields Validation System

This script validates and updates all calculated fields in the family tree to ensure
consistency. It should be run after any data changes.

Calculated fields include:
- generation: Based on birth year
- from_pat: Generation offset from Patrick Ruff (for graph UI positioning)
- age: Based on birth year and current year
- lineage: Based on parent relationships (for same-name generations)
- completion_percentage: Based on how many fields are filled

This ensures the data stays consistent and prevents display bugs.
"""

import json
import re
from typing import Dict, Optional
from datetime import datetime


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


def calculate_generation(year: Optional[int]) -> Optional[str]:
    """
    Calculate generation from birth year.

    Args:
        year: Birth year as integer

    Returns:
        Generation name or None
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


def calculate_from_pat(generation: Optional[str]) -> Optional[int]:
    """
    Calculate generation offset from Patrick Ruff (Millennial, born 1985).

    This field is used by graph.html for vertical positioning and coloring.
    Patrick's generation (Millennial) is 0, earlier generations are negative,
    later generations are positive.

    Args:
        generation: Generation name

    Returns:
        Integer offset from Patrick's generation, or None
    """
    if not generation:
        return None

    generation_to_offset = {
        'Greatest Generation': -4,
        'Silent Generation': -3,
        'Baby Boomer': -2,
        'Gen X': -1,
        'Millennial': 0,
        'Gen Z': 1,
        'Gen Alpha': 2
    }

    return generation_to_offset.get(generation)


def calculate_age(year: Optional[int]) -> Optional[int]:
    """Calculate current age from birth year."""
    if not year:
        return None
    current_year = datetime.now().year
    return current_year - year


def calculate_completion_percentage(person: Dict) -> float:
    """
    Calculate how complete a person's profile is.

    Args:
        person: Person dictionary

    Returns:
        Completion percentage (0-100)
    """
    # Define important fields
    important_fields = [
        'name', 'dob', 'dod', 'gender', 'occupation',
        'spouseId', 'parentIds', 'childrenIds',
        'home_city', 'home_state', 'phone', 'email',
        'ethnicity', 'generation'
    ]

    filled_count = 0
    total_count = len(important_fields)

    for field in important_fields:
        value = person.get(field)
        if value:
            # Check if it's a meaningful value
            if isinstance(value, str) and value not in ['Unknown', 'unknown', 'alive', '']:
                filled_count += 1
            elif isinstance(value, list) and len(value) > 0:
                filled_count += 1
            elif isinstance(value, dict) and len(value) > 0:
                filled_count += 1

    return round((filled_count / total_count) * 100, 1)


def validate_and_update_calculated_fields():
    """Validate and update all calculated fields."""
    print("\n" + "="*80)
    print("🔍 VALIDATING CALCULATED FIELDS")
    print("="*80 + "\n")

    family_data = load_family_data()
    people = family_data['family']['people']

    updates = {
        'generation': [],
        'from_pat': [],
        'age': [],
        'completion': [],
        'correct': 0
    }

    for person_id, person in people.items():
        name = person['name']
        dob = person.get('dob')
        year = extract_year(dob)

        # 1. Validate/Update Generation
        if year:
            correct_gen = calculate_generation(year)
            stored_gen = person.get('generation')

            if stored_gen != correct_gen:
                old_gen = stored_gen or 'None'
                person['generation'] = correct_gen
                updates['generation'].append((name, year, old_gen, correct_gen))
            else:
                updates['correct'] += 1

        # 2. Validate/Update from_pat (graph UI positioning field)
        current_gen = person.get('generation')
        if current_gen:
            correct_from_pat = calculate_from_pat(current_gen)
            stored_from_pat = person.get('from_pat')

            if stored_from_pat != correct_from_pat:
                old_from_pat = stored_from_pat if stored_from_pat is not None else 'NOT SET'
                person['from_pat'] = correct_from_pat
                updates['from_pat'].append((name, current_gen, old_from_pat, correct_from_pat))

        # 3. Calculate Age (optional field, for reference)
        if year:
            age = calculate_age(year)
            # Store age as a calculated field (not critical, just useful)
            person['_calculated_age'] = age

        # 3. Update Completion Percentage
        completion = calculate_completion_percentage(person)
        old_completion = person.get('completion_percentage', 0)

        if abs(completion - old_completion) > 0.1:  # Changed significantly
            person['completion_percentage'] = completion
            updates['completion'].append((name, old_completion, completion))

    # Display results
    print("📊 Validation Results:\n")

    if updates['generation']:
        print(f"❌ Generation Mismatches ({len(updates['generation'])} people):\n")
        for name, year, old_gen, correct_gen in updates['generation']:
            print(f"  {name:30} Born {year}: '{old_gen}' → '{correct_gen}'")
        print()

    if updates['from_pat']:
        print(f"🎯 from_pat Updates ({len(updates['from_pat'])} people):\n")
        for name, gen, old_from_pat, correct_from_pat in updates['from_pat'][:15]:
            print(f"  {name:30} ({gen:20}): {old_from_pat} → {correct_from_pat}")
        if len(updates['from_pat']) > 15:
            print(f"  ... and {len(updates['from_pat']) - 15} more")
        print()

    if updates['completion']:
        print(f"📈 Completion Updates ({len(updates['completion'])} people):\n")
        for name, old_comp, new_comp in updates['completion'][:10]:
            print(f"  {name:30} {old_comp:.1f}% → {new_comp:.1f}%")
        if len(updates['completion']) > 10:
            print(f"  ... and {len(updates['completion']) - 10} more")
        print()

    print(f"✅ Correct: {updates['correct']} people")

    total_issues = len(updates['generation']) + len(updates['from_pat']) + len(updates['completion'])

    if total_issues > 0:
        family_data['family']['people'] = people
        save_family_data(family_data)
        print(f"\n✅ Fixed {total_issues} calculated field issues!")
    else:
        print("\n✅ All calculated fields are correct!")

    return total_issues


def verify_specific_people():
    """Verify specific people mentioned in bug reports."""
    print("\n" + "="*80)
    print("🔬 VERIFYING SPECIFIC PEOPLE")
    print("="*80 + "\n")

    family_data = load_family_data()
    people = family_data['family']['people']

    # People to verify
    verify_list = [
        'Andy Greismeyer',
        'Debbie Miller',
        'Joe Ruff Sr.',
        'Joe Ruff Jr.',
        'Patrick Ruff'
    ]

    for name_to_find in verify_list:
        for person_id, person in people.items():
            if person['name'] == name_to_find:
                year = extract_year(person.get('dob'))
                gen = person.get('generation', 'None')
                correct_gen = calculate_generation(year) if year else 'None'
                from_pat = person.get('from_pat', 'NOT SET')

                status = '✅' if gen == correct_gen else '❌'
                print(f"{status} {person['name']:25} Born {year or 'Unknown':4} Gen: {gen:20} from_pat: {from_pat}")
                break


def main():
    """Main entry point."""
    issues_fixed = validate_and_update_calculated_fields()
    verify_specific_people()

    print("\n" + "="*80)
    print("💡 RECOMMENDATION")
    print("="*80)
    print("\nRun this script after making any data changes to ensure consistency.")
    print("Consider adding it as a pre-commit hook or validation step.")
    print("\nUsage:")
    print("  python validate_calculated_fields.py")


if __name__ == '__main__':
    main()
