#!/usr/bin/env python3
"""
Script to add generation labels and from_pat field to family_tree.json
"""

import json

def get_generation_info(birth_year):
    """
    Returns (generation_label, from_pat) based on birth year.
    Patrick Ruff (1985) is a Millennial, which is the baseline (from_pat = 0)
    Returns (None, None) if birth year is unknown or invalid.
    """
    # Handle missing, unknown, or invalid birth years
    if not birth_year or birth_year in ['unknown', 'alive', '']:
        return None, None

    try:
        year = int(birth_year)
    except (ValueError, TypeError):
        return None, None

    if year <= 1927:
        return "Greatest Generation", -4
    elif year <= 1945:
        return "Silent Generation", -3
    elif year <= 1964:
        return "Baby Boomer", -2
    elif year <= 1980:
        return "Generation X", -1
    elif year <= 1996:
        return "Millennial", 0
    elif year <= 2012:
        return "Generation Z", 1
    else:  # 2013+
        return "Generation Alpha", 2

def main():
    # Load family tree
    with open('family_tree.json', 'r') as f:
        data = json.load(f)

    # Add generation info to each person
    people = data['family']['people']

    for person_id, person in people.items():
        dob = person.get('dob', 'unknown')
        generation, from_pat = get_generation_info(dob)

        # Only set if we got valid results
        if generation is not None:
            person['generation'] = generation
            person['from_pat'] = from_pat

    # Update the instructions
    if '_instructions' in data:
        data['_instructions']['fields']['generation'] = "Generation label (e.g., 'Millennial', 'Baby Boomer', 'Generation Z')"
        data['_instructions']['fields']['from_pat'] = "Integer showing generations from Patrick Ruff (Millennial = 0, Gen X = -1, Gen Z = +1, etc.)"

    # Save updated data
    with open('family_tree.json', 'w') as f:
        json.dump(data, f, indent=2)

    # Print summary
    print("Generation distribution:")
    gen_counts = {}
    people_without_generation = 0

    for person in people.values():
        if 'generation' in person:
            gen = person['generation']
            gen_counts[gen] = gen_counts.get(gen, 0) + 1
        else:
            people_without_generation += 1

    # Sort generations by from_pat value
    gen_order = []
    for gen in gen_counts.keys():
        sample_person = next(p for p in people.values() if p.get('generation') == gen)
        gen_order.append((gen, sample_person['from_pat']))

    for gen, from_pat in sorted(gen_order, key=lambda x: x[1]):
        count = gen_counts[gen]
        print(f"  {gen} (from_pat: {from_pat:+d}): {count} people")

    if people_without_generation > 0:
        print(f"  Unknown (no birth year): {people_without_generation} people")

    print(f"\nTotal: {len(people)} people processed")

if __name__ == '__main__':
    main()
