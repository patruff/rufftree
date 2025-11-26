#!/usr/bin/env python3
"""
Script to add ethnicity field to family_tree.json
Ethnicity is calculated based on parents, or manually specified for root ancestors
"""

import json
from collections import defaultdict

def merge_ethnicities(ethnicity1, ethnicity2):
    """
    Merge two ethnicity dictionaries, averaging the percentages.
    Each parent contributes 50% to the child's ethnicity.
    """
    result = defaultdict(float)

    # Add 50% of each parent's ethnicity
    for country, percentage in ethnicity1.items():
        result[country] += percentage * 0.5

    for country, percentage in ethnicity2.items():
        result[country] += percentage * 0.5

    # Round to integers and ensure it adds up to 100
    result_dict = {country: round(percentage) for country, percentage in result.items()}

    # Normalize to ensure it adds up to 100
    total = sum(result_dict.values())
    if total != 100 and total > 0:
        # Adjust the largest value to make it sum to 100
        largest_country = max(result_dict, key=result_dict.get)
        result_dict[largest_country] += (100 - total)

    return dict(result_dict)

def calculate_ethnicity_for_person(person, people, ethnicity_cache):
    """
    Calculate ethnicity for a person based on their parents.
    Uses caching to avoid recalculation.
    """
    person_id = person['id']

    # If already calculated, return cached value
    if person_id in ethnicity_cache:
        return ethnicity_cache[person_id]

    # If person already has manually set ethnicity, use it
    if 'ethnicity' in person and person['ethnicity']:
        ethnicity_cache[person_id] = person['ethnicity']
        return person['ethnicity']

    # If no parents, return None (needs manual entry)
    if not person.get('parentIds') or len(person['parentIds']) == 0:
        return None

    # Calculate from parents
    parent_ethnicities = []
    for parent_id in person['parentIds']:
        if parent_id in people:
            parent = people[parent_id]
            parent_ethnicity = calculate_ethnicity_for_person(parent, people, ethnicity_cache)
            if parent_ethnicity:
                parent_ethnicities.append(parent_ethnicity)

    # If we don't have both parents' ethnicity, can't calculate
    if len(parent_ethnicities) != 2:
        return None

    # Merge parent ethnicities
    result = merge_ethnicities(parent_ethnicities[0], parent_ethnicities[1])
    ethnicity_cache[person_id] = result
    return result

def main():
    # Load family tree
    with open('family_tree.json', 'r') as f:
        data = json.load(f)

    people = data['family']['people']

    # Define ethnicity for root ancestors (people without parents in the system)
    # These are manually set based on surnames and family history
    root_ethnicities = {
        # Ruff side (German surname, American roots)
        'grandfather_ruff': {'German': 50, 'Irish': 50},
        'grandmother_ruff': {'Irish': 60, 'English': 40},

        # Miller side
        'stan_sr': {'German': 40, 'English': 30, 'Scottish': 30},
        'annette': {'German': 50, 'Polish': 30, 'Irish': 20},

        # Wang side (Chinese)
        'jenny_father': {'Chinese': 100},
        'jenny_mother': {'Chinese': 100},
    }

    # Set ethnicity for root ancestors
    for person_id, ethnicity in root_ethnicities.items():
        if person_id in people:
            people[person_id]['ethnicity'] = ethnicity

    # For in-laws without parents, set ethnicity (these are optional, just examples)
    # You can customize these or remove them
    in_law_ethnicities = {
        'katie': {'Irish': 40, 'German': 30, 'English': 30},
        'kevin_boilon': {'French': 60, 'Irish': 40},
        'ashley': {'English': 40, 'Scottish': 30, 'Irish': 30},
        'bryan_bradley': {'English': 50, 'Welsh': 30, 'Irish': 20},
    }

    for person_id, ethnicity in in_law_ethnicities.items():
        if person_id in people and not people[person_id].get('parentIds'):
            people[person_id]['ethnicity'] = ethnicity

    # Calculate ethnicity for everyone else based on parents
    ethnicity_cache = {}

    for person_id, person in people.items():
        calculated_ethnicity = calculate_ethnicity_for_person(person, people, ethnicity_cache)
        if calculated_ethnicity:
            person['ethnicity'] = calculated_ethnicity

    # Update the instructions
    if '_instructions' in data:
        data['_instructions']['fields']['ethnicity'] = "Optional: Object mapping countries to percentages (must sum to 100). Calculated from parents if not manually set."

    # Save updated data
    with open('family_tree.json', 'w') as f:
        json.dump(data, f, indent=2)

    # Print summary
    print("\nEthnicity Summary:")
    print("=" * 60)

    # Collect all unique countries
    all_countries = set()
    people_with_ethnicity = 0

    for person in people.values():
        if 'ethnicity' in person and person['ethnicity']:
            people_with_ethnicity += 1
            all_countries.update(person['ethnicity'].keys())

    print(f"People with ethnicity data: {people_with_ethnicity}/{len(people)}")
    print(f"\nCountries represented: {', '.join(sorted(all_countries))}")

    # Show a few examples
    print("\nExample ethnicities:")
    examples = ['patrick', 'jenny', 'joe_jr', 'patrick_child1']
    for person_id in examples:
        if person_id in people and 'ethnicity' in people[person_id]:
            person = people[person_id]
            ethnicity_str = ', '.join([f"{country}: {pct}%" for country, pct in sorted(person['ethnicity'].items(), key=lambda x: -x[1])])
            print(f"  {person['name']}: {ethnicity_str}")

if __name__ == '__main__':
    main()
