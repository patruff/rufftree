#!/usr/bin/env python3
"""
Script to add heritable_risk field based on parents' causes of death.
Tracks genetic predisposition to various conditions.
"""

import json

# Mapping of causes of death to their heritable risk factors
# Format: cause_of_death -> (risk_condition, base_risk_multiplier)
HEREDITARY_CONDITIONS = {
    # Cancers with strong hereditary components
    'breast-cancer': ('breast-cancer', 2.0),
    'ovarian-cancer': ('ovarian-cancer', 2.5),
    'colon-cancer': ('colorectal-cancer', 2.0),
    'prostate-cancer': ('prostate-cancer', 2.0),
    'pancreatic-cancer': ('pancreatic-cancer', 2.0),
    'stomach-cancer': ('stomach-cancer', 1.5),
    'lung-cancer': ('lung-cancer', 1.3),  # Some genetic component
    'melanoma': ('melanoma', 1.5),
    'skin-cancer': ('melanoma', 1.5),

    # Cardiovascular
    'heart-attack': ('heart-disease', 1.8),
    'heart-failure': ('heart-disease', 1.7),
    'coronary-heart-disease': ('heart-disease', 2.0),
    'stroke': ('stroke', 1.5),
    'aneurysm': ('aneurysm', 1.8),

    # Neurological
    'alzheimers': ('alzheimers', 2.0),
    'dementia': ('dementia', 1.7),
    'parkinsons': ('parkinsons', 1.5),
    'als': ('als', 1.2),

    # Metabolic/Other
    'diabetes': ('diabetes', 2.5),
    'kidney-disease': ('kidney-disease', 1.5),

    # General cancer catch-all
    'cancer-unspecified': ('cancer-general', 1.2),
    'leukemia': ('leukemia', 1.3),
    'lymphoma': ('lymphoma', 1.3),
}

def calculate_risk_level(multiplier, count):
    """
    Calculate risk level based on multiplier and number of affected relatives.

    Args:
        multiplier: Base risk multiplier for the condition
        count: Number of parents/grandparents with the condition

    Returns:
        Risk level: 'low', 'moderate', 'high', or 'very-high'
    """
    # Adjust multiplier based on number of affected relatives
    adjusted = multiplier * count

    if adjusted >= 4.0:
        return 'very-high'
    elif adjusted >= 2.5:
        return 'high'
    elif adjusted >= 1.5:
        return 'moderate'
    else:
        return 'low'

def analyze_family_causes(person, people):
    """
    Analyze causes of death in family to determine heritable risks.

    Args:
        person: The person object
        people: Dictionary of all people

    Returns:
        Dictionary mapping conditions to risk levels
    """
    risks = {}
    condition_counts = {}

    # Check parents
    if person.get('parentIds'):
        for parent_id in person['parentIds']:
            if parent_id in people:
                parent = people[parent_id]
                cause = parent.get('causeOfDeath')

                if cause and cause in HEREDITARY_CONDITIONS:
                    risk_condition, multiplier = HEREDITARY_CONDITIONS[cause]

                    if risk_condition not in condition_counts:
                        condition_counts[risk_condition] = {'count': 0, 'multiplier': multiplier}

                    condition_counts[risk_condition]['count'] += 1

    # Calculate risk levels
    for condition, data in condition_counts.items():
        risk_level = calculate_risk_level(data['multiplier'], data['count'])
        risks[condition] = risk_level

    return risks

def main():
    # Load family tree
    with open('family_tree.json', 'r') as f:
        data = json.load(f)

    people = data['family']['people']

    # Calculate heritable risk for each person
    people_with_risk = 0
    total_risk_factors = 0

    for person_id, person in people.items():
        # Skip if person is deceased (only relevant for living people)
        # Actually, keep it for everyone for medical history purposes

        heritable_risk = analyze_family_causes(person, people)

        if heritable_risk:
            person['heritable_risk'] = heritable_risk
            people_with_risk += 1
            total_risk_factors += len(heritable_risk)

    # Update documentation
    if '_instructions' in data:
        data['_instructions']['fields']['heritable_risk'] = "Optional: Object mapping health conditions to risk levels (low/moderate/high/very-high). Auto-calculated from parents' causes of death."

    # Save updated data
    with open('family_tree.json', 'w') as f:
        json.dump(data, f, indent=2)

    # Print summary
    print("\nHeritable Risk Analysis:")
    print("=" * 60)
    print(f"People with identified risk factors: {people_with_risk}/{len(people)}")
    print(f"Total risk factors identified: {total_risk_factors}")

    # Show risk distribution
    print("\nRisk Distribution by Condition:")
    condition_stats = {}
    for person in people.values():
        if 'heritable_risk' in person:
            for condition, level in person['heritable_risk'].items():
                if condition not in condition_stats:
                    condition_stats[condition] = {'low': 0, 'moderate': 0, 'high': 0, 'very-high': 0}
                condition_stats[condition][level] += 1

    for condition in sorted(condition_stats.keys()):
        levels = condition_stats[condition]
        total = sum(levels.values())
        print(f"  {condition}: {total} people")
        for level in ['low', 'moderate', 'high', 'very-high']:
            if levels[level] > 0:
                print(f"    - {level}: {levels[level]}")

    # Show some examples
    print("\nExample Risk Profiles:")
    examples = ['patrick', 'joe_jr', 'kaylin', 'eloise']
    for person_id in examples:
        if person_id in people and 'heritable_risk' in people[person_id]:
            person = people[person_id]
            risks = person['heritable_risk']
            risk_str = ', '.join([f"{cond}: {level}" for cond, level in risks.items()])
            print(f"  {person['name']}: {risk_str}")
        elif person_id in people:
            print(f"  {people[person_id]['name']}: No identified risk factors")

if __name__ == '__main__':
    main()
