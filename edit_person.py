#!/usr/bin/env python3
"""
Script to view and edit a person's information in the family tree.
Can be run locally or in GitHub Actions workflows.
"""

import json
import sys
from typing import Optional, Dict, Any
from pathlib import Path


def load_family_data():
    """Load the family tree JSON data."""
    with open('family_tree.json', 'r') as f:
        return json.load(f)


def save_family_data(data):
    """Save the family tree JSON data."""
    with open('family_tree.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n💾 Saved updated family tree to family_tree.json")


def search_person(name: str, people: Dict) -> Optional[tuple]:
    """
    Search for a person by name (flexible matching).

    Args:
        name: Full name or partial name to search for
        people: Dictionary of all people

    Returns:
        Tuple of (person_id, person_data) if found, None otherwise
    """
    name_lower = name.lower()

    # First try exact match
    for person_id, person in people.items():
        if person['name'].lower() == name_lower:
            return (person_id, person)

    # Then try partial match
    matches = []
    for person_id, person in people.items():
        if name_lower in person['name'].lower():
            matches.append((person_id, person))

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(f"⚠️  Multiple matches found for '{name}':")
        for i, (pid, p) in enumerate(matches, 1):
            dod_text = p['dod'] if p['dod'] != 'alive' else 'Present'
            print(f"  {i}. {p['name']} ({p['dob']} - {dod_text})")
        print(f"\n✅ Using first match: {matches[0][1]['name']}")
        return matches[0]

    return None


def display_person(person_id: str, person: Dict):
    """Display all information about a person in a readable format."""
    print("\n" + "="*80)
    print(f"PERSON: {person.get('name', 'Unknown')}")
    print("="*80)

    # Core fields
    print(f"\n📋 CORE INFORMATION:")
    print(f"   ID: {person_id}")
    print(f"   Name: {person.get('name', 'N/A')}")
    print(f"   Date of Birth: {person.get('dob', 'N/A')}")
    print(f"   Date of Death: {person.get('dod', 'N/A')}")

    if person.get('generation'):
        print(f"   Generation: {person['generation']}")
    if person.get('gender'):
        print(f"   Gender: {person['gender']}")

    # Location
    if person.get('home_city') or person.get('home_state'):
        print(f"\n🏠 HOME LOCATION:")
        if person.get('home_city'):
            print(f"   City: {person['home_city']}")
        if person.get('home_state'):
            print(f"   State: {person['home_state']}")

    # Cemetery (for deceased)
    if person.get('cemetery_name') or person.get('cemetery_city') or person.get('cemetery_state'):
        print(f"\n⚰️  CEMETERY:")
        if person.get('cemetery_name'):
            print(f"   Name: {person['cemetery_name']}")
        if person.get('cemetery_city'):
            print(f"   City: {person['cemetery_city']}")
        if person.get('cemetery_state'):
            print(f"   State: {person['cemetery_state']}")

    # Contact & Personal
    contact_fields = ['occupation', 'phone', 'maidenName', 'education']
    contact_info = {k: person.get(k) for k in contact_fields if person.get(k)}
    if contact_info:
        print(f"\n👤 CONTACT & PERSONAL:")
        if 'occupation' in contact_info:
            print(f"   Occupation: {contact_info['occupation']}")
        if 'phone' in contact_info:
            print(f"   Phone: {contact_info['phone']}")
        if 'maidenName' in contact_info:
            print(f"   Maiden Name: {contact_info['maidenName']}")
        if 'education' in contact_info:
            print(f"   Education: {contact_info['education']}")

    # Health
    if person.get('health_condition') or person.get('causeOfDeath'):
        print(f"\n🏥 HEALTH:")
        if person.get('health_condition'):
            print(f"   Health Conditions: {', '.join(person['health_condition'])}")
        if person.get('causeOfDeath'):
            print(f"   Cause of Death: {person['causeOfDeath']}")
        if person.get('heritable_risk'):
            print(f"   Heritable Risk: {person['heritable_risk']}")

    # Physical
    if person.get('hairColor') or person.get('height'):
        print(f"\n👁️  PHYSICAL:")
        if person.get('hairColor'):
            print(f"   Hair Color: {person['hairColor']}")
        if person.get('height'):
            print(f"   Height: {person['height']}")

    # Ethnicity
    if person.get('ethnicity'):
        print(f"\n🌍 ETHNICITY:")
        for ethnicity, percentage in sorted(person['ethnicity'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {ethnicity}: {percentage}%")

    # Genetic lineage
    if person.get('y_chromosome_line') or person.get('mtdna_line'):
        print(f"\n🧬 GENETIC LINEAGE:")
        if person.get('y_chromosome_line'):
            status = " (FINAL)" if person.get('y_chromosome_final') else ""
            print(f"   Y Chromosome: {person['y_chromosome_line']}{status}")
        if person.get('mtdna_line'):
            status = " (FINAL)" if person.get('mtdna_final') else ""
            print(f"   Mitochondrial DNA: {person['mtdna_line']}{status}")

    # Genetic traits
    if person.get('heritable_traits'):
        print(f"\n🧬 GENETIC TRAITS:")
        for trait, data in person['heritable_traits'].items():
            trait_label = trait.replace('_', ' ').title()
            genotype = data.get('genotype', 'N/A')
            phenotype = data.get('phenotype', 'N/A')
            print(f"   {trait_label}: {genotype} → {phenotype}")

    # Data coverage
    if 'rag_chunks' in person:
        print(f"\n📚 DOCUMENTATION COVERAGE:")
        print(f"   RAG Chunks: {person['rag_chunks']}")
        print(f"   Lacks Data: {person.get('lacks_data', False)}")

    # Relationships
    if person.get('spouseId'):
        print(f"\n💑 SPOUSE:")
        print(f"   Spouse ID: {person['spouseId']}")

    if person.get('parentIds'):
        print(f"\n👨‍👩 PARENTS:")
        print(f"   Parent IDs: {', '.join(person['parentIds'])}")

    if person.get('siblingIds'):
        print(f"\n👥 SIBLINGS:")
        print(f"   Sibling IDs: {', '.join(person['siblingIds'])}")

    if person.get('childrenIds'):
        print(f"\n👶 CHILDREN:")
        print(f"   Children IDs: {', '.join(person['childrenIds'])}")

    # Notes
    if person.get('notes'):
        print(f"\n📝 NOTES:")
        print(f"   {person['notes']}")

    # Attributes & Personality
    if person.get('attributes'):
        print(f"\n⭐ ATTRIBUTES:")
        print(f"   {', '.join(person['attributes'])}")

    if person.get('personality'):
        print(f"\n🎭 PERSONALITY (OCEAN):")
        for trait, value in person['personality'].items():
            print(f"   {trait.capitalize()}: {value}")

    print("\n" + "="*80)


def apply_updates(person: Dict, updates: Dict[str, Any]) -> Dict:
    """
    Apply updates to a person's data.

    Args:
        person: Current person data
        updates: Dictionary of field updates

    Returns:
        Updated person dictionary
    """
    changes_made = []

    for field, value in updates.items():
        # Skip None values
        if value is None:
            continue

        # Skip empty strings for most fields
        if isinstance(value, str) and value.strip() == '':
            continue

        # Convert "null" string to None for removal
        if isinstance(value, str) and value.lower() == 'null':
            if field in person:
                old_value = person[field]
                del person[field]
                changes_made.append(f"Removed {field} (was: {old_value})")
            continue

        # Handle arrays (health_condition, attributes, etc.)
        if field in ['health_condition', 'attributes', 'parentIds', 'siblingIds', 'childrenIds']:
            if isinstance(value, str):
                # Parse comma-separated values
                value = [v.strip() for v in value.split(',') if v.strip()]
            if isinstance(value, list) and len(value) > 0:
                old_value = person.get(field, [])
                person[field] = value
                changes_made.append(f"Updated {field}: {old_value} → {value}")
            continue

        # Handle special field transformations
        if field == 'dod' and isinstance(value, str):
            # Allow "alive" or year
            if value.lower() == 'alive' or value.isdigit():
                old_value = person.get(field, 'N/A')
                person[field] = value if value.lower() == 'alive' else value
                changes_made.append(f"Updated {field}: {old_value} → {person[field]}")
            continue

        # Regular field update
        old_value = person.get(field, 'N/A')
        person[field] = value
        changes_made.append(f"Updated {field}: {old_value} → {value}")

    return person, changes_made


def main():
    """Main function to edit a person."""
    if len(sys.argv) < 2:
        print("❌ Error: No person name provided")
        print("\nUsage:")
        print("  python3 edit_person.py 'Person Name' [--view-only]")
        print("  python3 edit_person.py 'Person Name' --field value [--field2 value2 ...]")
        print("\nExamples:")
        print("  python3 edit_person.py 'Patrick Ruff' --view-only")
        print("  python3 edit_person.py 'Patrick Ruff' --occupation 'Engineer' --phone '555-1234'")
        print("  python3 edit_person.py 'Jenny Wang' --home_city 'Seattle' --home_state 'Washington'")
        sys.exit(1)

    person_name = sys.argv[1]

    # Load family data
    print("📂 Loading family tree...")
    data = load_family_data()
    people = data['family']['people']
    print(f"   ✅ Loaded {len(people)} family members")

    # Search for person
    print(f"\n🔍 Searching for '{person_name}'...")
    result = search_person(person_name, people)

    if not result:
        print(f"\n❌ No match found for '{person_name}'")
        print("\nTip: Try searching by first name only, or check spelling.")
        sys.exit(1)

    person_id, person = result
    print(f"✅ Found: {person['name']}")

    # Display current information
    display_person(person_id, person)

    # Check if view-only mode
    if '--view-only' in sys.argv:
        print("\n👁️  View-only mode - no changes made")
        sys.exit(0)

    # Parse update arguments
    updates = {}
    i = 2
    while i < len(sys.argv):
        if sys.argv[i].startswith('--'):
            field_name = sys.argv[i][2:]  # Remove --
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('--'):
                field_value = sys.argv[i + 1]
                updates[field_name] = field_value
                i += 2
            else:
                print(f"⚠️  Warning: No value provided for --{field_name}")
                i += 1
        else:
            i += 1

    if not updates:
        print("\n⚠️  No updates specified. Use --field_name value to make changes.")
        print("   Or use --view-only to just view information.")
        sys.exit(0)

    # Apply updates
    print("\n" + "="*80)
    print("APPLYING UPDATES")
    print("="*80)

    person, changes_made = apply_updates(person, updates)

    if changes_made:
        print("\n✅ Changes made:")
        for change in changes_made:
            print(f"   • {change}")

        # Update the person in the data
        data['family']['people'][person_id] = person

        # Save changes
        save_family_data(data)

        print("\n" + "="*80)
        print("✅ SUCCESS - Person updated!")
        print("="*80)
    else:
        print("\n⚠️  No valid changes to apply")

    # Display updated information
    print("\n📋 UPDATED INFORMATION:")
    display_person(person_id, person)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
