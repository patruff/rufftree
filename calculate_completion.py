#!/usr/bin/env python3
"""
Calculate completion percentage for each person in the family tree.
Measures how many optional fields are filled out vs total available fields.
"""

import json
import sys
from typing import Dict, Tuple


def load_family_data():
    """Load the family tree JSON data."""
    with open('family_tree.json', 'r') as f:
        return json.load(f)


def save_family_data(data):
    """Save the family tree JSON data."""
    with open('family_tree.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n💾 Saved updated family tree to family_tree.json")


def calculate_person_completion(person: Dict) -> Tuple[int, int, float]:
    """
    Calculate completion percentage for a person.

    Args:
        person: Person data dictionary

    Returns:
        Tuple of (fields_filled, total_fields, percentage)
    """
    is_deceased = person.get('dod', 'alive') != 'alive'

    # Define optional fields that count toward completion
    # These are organized by category for clarity

    location_fields = ['home_city', 'home_state']
    if is_deceased:
        location_fields.extend(['cemetery_name', 'cemetery_city', 'cemetery_state'])

    contact_fields = ['occupation', 'phone', 'maidenName', 'education']

    health_fields = ['health_condition']
    if is_deceased:
        health_fields.append('causeOfDeath')

    physical_fields = ['hairColor', 'height']

    personal_fields = ['notes', 'attributes', 'personality']

    # Relationships - these are important for family tree completeness
    relationship_fields = ['spouseId', 'parentIds', 'siblingIds', 'childrenIds']

    # Combine all optional fields
    all_optional_fields = (
        location_fields +
        contact_fields +
        health_fields +
        physical_fields +
        personal_fields +
        relationship_fields
    )

    # Count filled fields
    filled = 0
    for field in all_optional_fields:
        value = person.get(field)

        # Check if field is meaningfully filled
        if value is not None:
            if isinstance(value, str) and value.strip():
                filled += 1
            elif isinstance(value, list) and len(value) > 0:
                filled += 1
            elif isinstance(value, dict) and len(value) > 0:
                filled += 1

    total = len(all_optional_fields)
    percentage = round((filled / total * 100), 1) if total > 0 else 0.0

    return filled, total, percentage


def categorize_completion(percentage: float) -> str:
    """
    Categorize completion percentage into levels.

    Args:
        percentage: Completion percentage (0-100)

    Returns:
        Category string
    """
    if percentage >= 80:
        return "excellent"
    elif percentage >= 60:
        return "good"
    elif percentage >= 40:
        return "fair"
    elif percentage >= 20:
        return "minimal"
    else:
        return "incomplete"


def calculate_all_completions():
    """Calculate completion percentage for all people in the family tree."""
    print("\n" + "="*80)
    print("📊 CALCULATING PROFILE COMPLETION")
    print("="*80 + "\n")

    # Load family data
    print("📂 Loading family tree...")
    data = load_family_data()
    people = data['family']['people']
    print(f"   ✅ Loaded {len(people)} family members\n")

    # Calculate completion for each person
    print("🔢 Calculating completion percentages...")
    print("="*80 + "\n")

    results = {
        'total': len(people),
        'excellent': 0,  # >= 80%
        'good': 0,       # >= 60%
        'fair': 0,       # >= 40%
        'minimal': 0,    # >= 20%
        'incomplete': 0, # < 20%
        'details': []
    }

    for i, (person_id, person) in enumerate(people.items(), 1):
        person_name = person.get('name', 'Unknown')

        filled, total, percentage = calculate_person_completion(person)
        category = categorize_completion(percentage)

        # Update person data
        person['completion_percentage'] = percentage

        # Update statistics
        results[category] += 1

        # Format output
        status_icon = "✅" if percentage >= 80 else "⚠️" if percentage >= 40 else "❌"
        print(f"[{i}/{len(people)}] {status_icon} {person_name:<30} {percentage:5.1f}% ({filled}/{total} fields)")

        # Store detailed results
        results['details'].append({
            'name': person_name,
            'id': person_id,
            'filled': filled,
            'total': total,
            'percentage': percentage,
            'category': category
        })

    # Save updated data
    print("\n" + "="*80)
    print("💾 Saving updated family tree with completion percentages...")
    save_family_data(data)

    # Print summary
    print("\n" + "="*80)
    print("📊 COMPLETION SUMMARY")
    print("="*80)
    print(f"✅ Excellent (≥80%):  {results['excellent']:3d} people ({results['excellent']/results['total']*100:.1f}%)")
    print(f"👍 Good (60-79%):     {results['good']:3d} people ({results['good']/results['total']*100:.1f}%)")
    print(f"😐 Fair (40-59%):     {results['fair']:3d} people ({results['fair']/results['total']*100:.1f}%)")
    print(f"⚠️  Minimal (20-39%):  {results['minimal']:3d} people ({results['minimal']/results['total']*100:.1f}%)")
    print(f"❌ Incomplete (<20%): {results['incomplete']:3d} people ({results['incomplete']/results['total']*100:.1f}%)")
    print("="*80)

    # Calculate average completion
    avg_completion = sum(d['percentage'] for d in results['details']) / len(results['details'])
    print(f"\n📈 Average Completion: {avg_completion:.1f}%")

    # List people needing more information
    needs_work = [d for d in results['details'] if d['percentage'] < 60]
    if needs_work:
        print(f"\n⚠️  PEOPLE NEEDING MORE INFORMATION ({len(needs_work)}):")
        print("="*80)
        for person in sorted(needs_work, key=lambda x: x['percentage']):
            print(f"   • {person['name']:<30} {person['percentage']:5.1f}% ({person['filled']}/{person['total']} fields)")
    else:
        print("\n🎉 All family members have good profile completion!")

    print("\n" + "="*80)

    # Create a report file
    from pathlib import Path
    report_file = Path('completion_report.json')
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"📄 Detailed report saved to: {report_file}")
    print("="*80 + "\n")

    return results


def main():
    """Entry point for the script."""
    try:
        calculate_all_completions()
    except KeyboardInterrupt:
        print("\n\n❌ Calculation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
