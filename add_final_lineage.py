#!/usr/bin/env python3
"""
Script to add final_male and final_female fields to track genetic lineages.
- final_male: Last male descendant carrying a particular Y chromosome (paternal line)
- final_female: Last female descendant carrying particular mitochondrial DNA (maternal line)
"""

import json

def infer_gender(person):
    """
    Infer gender from name or existing fields.
    Returns 'male', 'female', or None
    """
    # Check if gender is already specified
    if 'gender' in person:
        return person['gender'].lower()

    # Common male/female name patterns
    name = person.get('name', '').lower()

    # Male names (common patterns)
    male_indicators = ['patrick', 'joseph', 'joe', 'phil', 'philip', 'stan', 'stanley',
                       'john', 'james', 'michael', 'william', 'david', 'robert']

    # Female names (common patterns)
    female_indicators = ['jenny', 'jennifer', 'sarah', 'sara', 'debbie', 'deborah',
                        'annette', 'kaylin', 'eloise', 'mary', 'elizabeth', 'susan']

    for indicator in male_indicators:
        if indicator in name:
            return 'male'

    for indicator in female_indicators:
        if indicator in name:
            return 'female'

    # Check if person has maiden name (likely female)
    if 'maidenName' in person:
        return 'female'

    return None

def has_male_descendants(person_id, people, visited=None):
    """
    Check if a male person has any male descendants.
    Returns True if there are male descendants, False otherwise.
    """
    if visited is None:
        visited = set()

    if person_id in visited:
        return False

    visited.add(person_id)
    person = people[person_id]

    # Check all children
    children_ids = person.get('childrenIds', [])
    for child_id in children_ids:
        if child_id not in people:
            continue

        child = people[child_id]
        child_gender = infer_gender(child)

        # If this child is male, check if they have male descendants
        if child_gender == 'male':
            # This person has at least one male descendant
            return True

        # Even if child is female, check their children (for Y chromosome tracking)
        # Actually, no - Y chromosome only passes through males

    return False

def has_female_descendants(person_id, people, visited=None):
    """
    Check if a female person has any female descendants.
    Returns True if there are female descendants, False otherwise.
    """
    if visited is None:
        visited = set()

    if person_id in visited:
        return False

    visited.add(person_id)
    person = people[person_id]

    # Check all children
    children_ids = person.get('childrenIds', [])
    for child_id in children_ids:
        if child_id not in people:
            continue

        child = people[child_id]
        child_gender = infer_gender(child)

        # If this child is female, they carry the mtDNA
        if child_gender == 'female':
            # This person has at least one female descendant
            return True

    return False

def main():
    # Load family tree
    with open('family_tree.json', 'r') as f:
        data = json.load(f)

    people = data['family']['people']

    # First pass: Infer and store genders
    print("\nInferring genders...")
    for person_id, person in people.items():
        gender = infer_gender(person)
        if gender:
            person['gender'] = gender
            print(f"  {person['name']}: {gender}")

    # Second pass: Calculate final_male for males
    males_analyzed = 0
    final_males = 0

    for person_id, person in people.items():
        gender = person.get('gender')

        if gender == 'male':
            males_analyzed += 1
            # Check if this male has male descendants
            has_male_desc = has_male_descendants(person_id, people)

            if not has_male_desc:
                person['final_male'] = True
                final_males += 1
                print(f"\n🔵 Final Male: {person['name']} (Y chromosome line ends)")
            else:
                person['final_male'] = False

    # Third pass: Calculate final_female for females
    females_analyzed = 0
    final_females = 0

    for person_id, person in people.items():
        gender = person.get('gender')

        if gender == 'female':
            females_analyzed += 1
            # Check if this female has female descendants
            has_female_desc = has_female_descendants(person_id, people)

            if not has_female_desc:
                person['final_female'] = True
                final_females += 1
                print(f"\n🔴 Final Female: {person['name']} (mtDNA line ends)")
            else:
                person['final_female'] = False

    # Update documentation
    if '_instructions' in data:
        data['_instructions']['fields']['gender'] = "String: 'male' or 'female'. Auto-inferred from name if not specified."
        data['_instructions']['fields']['final_male'] = "Boolean: True if this male is the last male descendant in his Y chromosome (paternal) line. Auto-calculated."
        data['_instructions']['fields']['final_female'] = "Boolean: True if this female is the last female descendant in her mitochondrial DNA (maternal) line. Auto-calculated."

    # Save updated data
    with open('family_tree.json', 'w') as f:
        json.dump(data, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("Genetic Lineage Analysis Summary:")
    print("=" * 60)
    print(f"\nMales analyzed: {males_analyzed}")
    print(f"Final males (Y chromosome lines ending): {final_males}")
    print(f"\nFemales analyzed: {females_analyzed}")
    print(f"Final females (mtDNA lines ending): {final_females}")

    print("\n📊 Interpretation:")
    print(f"  • {final_males} Y chromosome lineages will end without male heirs")
    print(f"  • {final_females} mitochondrial DNA lineages will end without female descendants")

    # List all final males and females
    print("\n🔵 All Final Males (Y chromosome):")
    for person_id, person in people.items():
        if person.get('final_male'):
            status = "alive" if person.get('dod') == 'alive' else "deceased"
            print(f"  • {person['name']} ({status})")

    print("\n🔴 All Final Females (mtDNA):")
    for person_id, person in people.items():
        if person.get('final_female'):
            status = "alive" if person.get('dod') == 'alive' else "deceased"
            print(f"  • {person['name']} ({status})")

if __name__ == '__main__':
    main()
