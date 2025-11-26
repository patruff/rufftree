#!/usr/bin/env python3
"""
Script to track genetic lineages with specific ancestral line labels.
- Traces Y chromosome lines back to root male ancestors (e.g., "Ruff Y")
- Traces mitochondrial DNA lines back to root female ancestors (e.g., "Miller mtDNA")
- Identifies final carriers of each specific lineage
"""

import json
from collections import defaultdict

def infer_gender(person):
    """
    Infer gender from name or existing fields.
    Returns 'male', 'female', or None
    """
    if 'gender' in person:
        return person['gender'].lower()

    name = person.get('name', '').lower()

    male_indicators = ['patrick', 'joseph', 'joe', 'phil', 'philip', 'stan', 'stanley',
                       'john', 'james', 'michael', 'william', 'david', 'robert', 'thomas']
    female_indicators = ['jenny', 'jennifer', 'sarah', 'sara', 'debbie', 'deborah',
                        'annette', 'kaylin', 'eloise', 'mary', 'elizabeth', 'susan',
                        'linda', 'patricia', 'barbara', 'nancy', 'karen', 'donna']

    for indicator in male_indicators:
        if indicator in name:
            return 'male'

    for indicator in female_indicators:
        if indicator in name:
            return 'female'

    if 'maidenName' in person:
        return 'female'

    return None

def get_last_name(person):
    """Extract last name from person's name."""
    name = person.get('name', '')
    parts = name.split()
    return parts[-1] if parts else 'Unknown'

def find_y_chromosome_root(person_id, people, visited=None):
    """
    Trace back through fathers to find the root male ancestor.
    Returns the person_id of the root male ancestor.
    """
    if visited is None:
        visited = set()

    if person_id in visited:
        return None

    visited.add(person_id)
    person = people.get(person_id)

    if not person:
        return None

    # Check if this person has a father
    parent_ids = person.get('parentIds', [])
    father_id = None

    for parent_id in parent_ids:
        if parent_id in people:
            parent = people[parent_id]
            if parent.get('gender') == 'male':
                father_id = parent_id
                break

    # If no father, this person is the root
    if not father_id:
        return person_id

    # Otherwise, recurse to father
    return find_y_chromosome_root(father_id, people, visited)

def find_mtdna_root(person_id, people, visited=None):
    """
    Trace back through mothers to find the root female ancestor.
    Returns the person_id of the root female ancestor.
    """
    if visited is None:
        visited = set()

    if person_id in visited:
        return None

    visited.add(person_id)
    person = people.get(person_id)

    if not person:
        return None

    # Check if this person has a mother
    parent_ids = person.get('parentIds', [])
    mother_id = None

    for parent_id in parent_ids:
        if parent_id in people:
            parent = people[parent_id]
            if parent.get('gender') == 'female':
                mother_id = parent_id
                break

    # If no mother, this person is the root
    if not mother_id:
        return person_id

    # Otherwise, recurse to mother
    return find_mtdna_root(mother_id, people, visited)

def has_male_descendants(person_id, people, visited=None):
    """Check if a male has any male descendants."""
    if visited is None:
        visited = set()

    if person_id in visited:
        return False

    visited.add(person_id)
    person = people[person_id]

    children_ids = person.get('childrenIds', [])
    for child_id in children_ids:
        if child_id not in people:
            continue

        child = people[child_id]
        if child.get('gender') == 'male':
            return True

    return False

def has_female_descendants(person_id, people, visited=None):
    """Check if a female has any female descendants."""
    if visited is None:
        visited = set()

    if person_id in visited:
        return False

    visited.add(person_id)
    person = people[person_id]

    children_ids = person.get('childrenIds', [])
    for child_id in children_ids:
        if child_id not in people:
            continue

        child = people[child_id]
        if child.get('gender') == 'female':
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

    # Track unique lineages
    y_lineages = defaultdict(list)  # {line_name: [person_ids]}
    mtdna_lineages = defaultdict(list)  # {line_name: [person_ids]}

    # Second pass: Assign Y chromosome lines to males
    print("\n" + "=" * 60)
    print("Tracing Y Chromosome Lineages:")
    print("=" * 60)

    for person_id, person in people.items():
        if person.get('gender') != 'male':
            continue

        # Find root ancestor
        root_id = find_y_chromosome_root(person_id, people)

        if root_id and root_id in people:
            root = people[root_id]
            last_name = get_last_name(root)
            line_name = f"{last_name} Y"

            # Assign this line to the person
            person['y_chromosome_line'] = line_name
            y_lineages[line_name].append(person_id)

            # Check if this male has male descendants
            has_male_desc = has_male_descendants(person_id, people)
            person['y_chromosome_final'] = not has_male_desc

    # Third pass: Assign mtDNA lines to females
    print("\nTracing Mitochondrial DNA Lineages:")
    print("=" * 60)

    for person_id, person in people.items():
        if person.get('gender') != 'female':
            continue

        # Find root ancestor
        root_id = find_mtdna_root(person_id, people)

        if root_id and root_id in people:
            root = people[root_id]
            last_name = get_last_name(root)
            # Use maiden name if available
            if 'maidenName' in root:
                last_name = root['maidenName']
            line_name = f"{last_name} mtDNA"

            # Assign this line to the person
            person['mtdna_line'] = line_name
            mtdna_lineages[line_name].append(person_id)

            # Check if this female has female descendants
            has_female_desc = has_female_descendants(person_id, people)
            person['mtdna_final'] = not has_female_desc

    # Update documentation
    if '_instructions' in data:
        data['_instructions']['fields']['gender'] = "String: 'male' or 'female'. Auto-inferred from name if not specified."
        data['_instructions']['fields']['y_chromosome_line'] = "String: Y chromosome lineage name (e.g., 'Ruff Y'). Traced from root paternal ancestor."
        data['_instructions']['fields']['y_chromosome_final'] = "Boolean: True if this male is the last in his Y chromosome line (no male descendants)."
        data['_instructions']['fields']['mtdna_line'] = "String: Mitochondrial DNA lineage name (e.g., 'Miller mtDNA'). Traced from root maternal ancestor."
        data['_instructions']['fields']['mtdna_final'] = "Boolean: True if this female is the last in her mtDNA line (no female descendants)."

    # Save updated data
    with open('family_tree.json', 'w') as f:
        json.dump(data, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("Genetic Lineage Analysis Summary:")
    print("=" * 60)

    # Y Chromosome lines
    print(f"\n🔵 Y Chromosome Lines Identified: {len(y_lineages)}")
    for line_name, person_ids in sorted(y_lineages.items()):
        carriers = len(person_ids)
        finals = sum(1 for pid in person_ids if people[pid].get('y_chromosome_final'))
        print(f"\n  {line_name}:")
        print(f"    • Total male carriers: {carriers}")
        print(f"    • Final males (line ending): {finals}")

        if finals > 0:
            print(f"    • Males where this line ends:")
            for pid in person_ids:
                if people[pid].get('y_chromosome_final'):
                    status = "alive" if people[pid].get('dod') == 'alive' else "deceased"
                    print(f"      - {people[pid]['name']} ({status})")

    # mtDNA lines
    print(f"\n🔴 Mitochondrial DNA Lines Identified: {len(mtdna_lineages)}")
    for line_name, person_ids in sorted(mtdna_lineages.items()):
        carriers = len(person_ids)
        finals = sum(1 for pid in person_ids if people[pid].get('mtdna_final'))
        print(f"\n  {line_name}:")
        print(f"    • Total female carriers: {carriers}")
        print(f"    • Final females (line ending): {finals}")

        if finals > 0:
            print(f"    • Females where this line ends:")
            for pid in person_ids:
                if people[pid].get('mtdna_final'):
                    status = "alive" if people[pid].get('dod') == 'alive' else "deceased"
                    print(f"      - {people[pid]['name']} ({status})")

    # Overall stats
    total_y_finals = sum(1 for p in people.values() if p.get('y_chromosome_final'))
    total_mtdna_finals = sum(1 for p in people.values() if p.get('mtdna_final'))

    print(f"\n📊 Overall Statistics:")
    print(f"  • {len(y_lineages)} distinct Y chromosome lineages tracked")
    print(f"  • {len(mtdna_lineages)} distinct mitochondrial DNA lineages tracked")
    print(f"  • {total_y_finals} males are final in their Y chromosome lines")
    print(f"  • {total_mtdna_finals} females are final in their mtDNA lines")

if __name__ == '__main__':
    main()
