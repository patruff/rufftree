#!/usr/bin/env python3
"""
Script to add heritable_traits field based on parents' genetic traits.
Tracks genotypes for simple Mendelian traits like eye color, hair texture, etc.
"""

import json
from collections import defaultdict

# Define trait inheritance patterns
# Format: trait_name -> (dominant_allele, recessive_allele, trait_description)
TRAITS = {
    'eye_color': {
        'dominant': 'B',  # Brown eyes
        'recessive': 'b',  # Blue eyes
        'description': 'Eye Color',
        'phenotypes': {
            'BB': 'Brown',
            'Bb': 'Brown',
            'bb': 'Blue'
        }
    },
    'hair_texture': {
        'dominant': 'C',  # Curly hair
        'recessive': 'c',  # Straight hair
        'description': 'Hair Texture',
        'phenotypes': {
            'CC': 'Curly',
            'Cc': 'Wavy/Curly',
            'cc': 'Straight'
        }
    },
    'dimples': {
        'dominant': 'D',  # Has dimples
        'recessive': 'd',  # No dimples
        'description': 'Dimples',
        'phenotypes': {
            'DD': 'Has dimples',
            'Dd': 'Has dimples',
            'dd': 'No dimples'
        }
    }
}

def calculate_offspring_genotypes(parent1_genotype, parent2_genotype):
    """
    Calculate possible offspring genotypes from two parents.

    Args:
        parent1_genotype: String like "Bb" or "bb"
        parent2_genotype: String like "Bb" or "BB"

    Returns:
        Dict mapping genotypes to their probability percentages
    """
    if not parent1_genotype or not parent2_genotype:
        return {}

    # Get alleles from each parent
    p1_alleles = [parent1_genotype[0], parent1_genotype[1]]
    p2_alleles = [parent2_genotype[0], parent2_genotype[1]]

    # Calculate all possible combinations
    combinations = defaultdict(int)
    for a1 in p1_alleles:
        for a2 in p2_alleles:
            # Sort alleles to normalize (Bb and bB are the same)
            genotype = ''.join(sorted([a1, a2], reverse=True))
            combinations[genotype] += 1

    # Convert counts to percentages
    total = sum(combinations.values())
    probabilities = {gt: (count / total * 100) for gt, count in combinations.items()}

    # If only one genotype possible (100%), return just the genotype
    if len(probabilities) == 1:
        return list(probabilities.keys())[0]

    return probabilities

def determine_most_likely_genotype(probabilities):
    """
    Determine the most likely genotype from probabilities.
    If multiple are equally likely, choose the heterozygous if available.
    """
    if isinstance(probabilities, str):
        return probabilities

    if not probabilities:
        return None

    # Get the genotype(s) with highest probability
    max_prob = max(probabilities.values())
    likely_genotypes = [gt for gt, prob in probabilities.items() if prob == max_prob]

    # If multiple equally likely, prefer heterozygous
    if len(likely_genotypes) > 1:
        for gt in likely_genotypes:
            if len(set(gt)) == 2:  # Heterozygous (e.g., Bb)
                return gt

    return likely_genotypes[0]

def calculate_traits_from_parents(person, people, trait_name, trait_info):
    """
    Calculate a person's genotype for a trait based on parents.

    Returns:
        String genotype (e.g., "Bb") or dict of probabilities
    """
    if not person.get('parentIds') or len(person['parentIds']) != 2:
        return None

    parent1_id, parent2_id = person['parentIds']

    if parent1_id not in people or parent2_id not in people:
        return None

    parent1 = people[parent1_id]
    parent2 = people[parent2_id]

    # Get parent genotypes for this trait
    p1_traits = parent1.get('heritable_traits', {})
    p2_traits = parent2.get('heritable_traits', {})

    p1_genotype = p1_traits.get(trait_name, {}).get('genotype')
    p2_genotype = p2_traits.get(trait_name, {}).get('genotype')

    if not p1_genotype or not p2_genotype:
        return None

    return calculate_offspring_genotypes(p1_genotype, p2_genotype)

def get_phenotype(genotype, trait_info):
    """Get the phenotype (observable trait) from genotype."""
    if isinstance(genotype, dict):
        # If probabilistic, show all possibilities
        phenotypes = []
        for gt, prob in sorted(genotype.items(), key=lambda x: x[1], reverse=True):
            pheno = trait_info['phenotypes'].get(gt, gt)
            phenotypes.append(f"{pheno} ({int(prob)}%)")
        return ', '.join(phenotypes)

    return trait_info['phenotypes'].get(genotype, genotype)

def main():
    # Load family tree
    with open('family_tree.json', 'r') as f:
        data = json.load(f)

    people = data['family']['people']

    # Manually set root ancestors' genotypes
    # Edit these to match your family's actual traits
    root_genotypes = {
        # Format: person_id -> {trait_name: genotype}
        'patrick': {
            'eye_color': 'bb',  # Blue eyes (homozygous recessive)
            'hair_texture': 'cc',  # Straight hair
            'dimples': 'dd'  # No dimples
        },
        'jenny': {
            'eye_color': 'Bb',  # Brown eyes (heterozygous)
            'hair_texture': 'Cc',  # Wavy/curly hair
            'dimples': 'Dd'  # Has dimples
        },
        # Add more root ancestors as needed
        # 'joe_sr': {'eye_color': 'BB', 'hair_texture': 'cc', 'dimples': 'dd'},
    }

    # First pass: Set root genotypes
    for person_id, traits in root_genotypes.items():
        if person_id in people:
            if 'heritable_traits' not in people[person_id]:
                people[person_id]['heritable_traits'] = {}

            for trait_name, genotype in traits.items():
                if trait_name in TRAITS:
                    trait_info = TRAITS[trait_name]
                    people[person_id]['heritable_traits'][trait_name] = {
                        'genotype': genotype,
                        'phenotype': get_phenotype(genotype, trait_info)
                    }

    # Second pass: Calculate children's genotypes from parents
    # Multiple passes to handle multi-generational calculation
    max_iterations = 10
    for iteration in range(max_iterations):
        updated = False

        for person_id, person in people.items():
            # Skip if already has traits
            if 'heritable_traits' in person and person['heritable_traits']:
                continue

            # Try to calculate from parents
            person['heritable_traits'] = {}

            for trait_name, trait_info in TRAITS.items():
                result = calculate_traits_from_parents(person, people, trait_name, trait_info)

                if result:
                    # If result is a single genotype
                    if isinstance(result, str):
                        person['heritable_traits'][trait_name] = {
                            'genotype': result,
                            'phenotype': get_phenotype(result, trait_info)
                        }
                    # If result is probabilities, pick most likely
                    else:
                        best_genotype = determine_most_likely_genotype(result)
                        person['heritable_traits'][trait_name] = {
                            'genotype': best_genotype,
                            'phenotype': get_phenotype(best_genotype, trait_info),
                            'probabilities': result
                        }
                    updated = True

            # Remove empty heritable_traits
            if not person['heritable_traits']:
                del person['heritable_traits']

        if not updated:
            break

    # Update documentation
    if '_instructions' in data:
        data['_instructions']['fields']['heritable_traits'] = "Optional: Object mapping trait names to genotype/phenotype info. Auto-calculated from parents for Mendelian traits (eye color, hair texture, dimples, etc.)"

    # Save updated data
    with open('family_tree.json', 'w') as f:
        json.dump(data, f, indent=2)

    # Print summary
    print("\nHeritable Traits Analysis:")
    print("=" * 60)

    people_with_traits = sum(1 for p in people.values() if 'heritable_traits' in p)
    print(f"People with calculated traits: {people_with_traits}/{len(people)}")

    # Show trait distribution
    print("\nTrait Distribution:")
    for trait_name, trait_info in TRAITS.items():
        print(f"\n  {trait_info['description']}:")
        genotype_counts = defaultdict(int)

        for person in people.values():
            if 'heritable_traits' in person and trait_name in person['heritable_traits']:
                genotype = person['heritable_traits'][trait_name]['genotype']
                genotype_counts[genotype] += 1

        for genotype in sorted(genotype_counts.keys()):
            count = genotype_counts[genotype]
            phenotype = trait_info['phenotypes'].get(genotype, genotype)
            print(f"    {genotype} ({phenotype}): {count} people")

    # Show some examples
    print("\nExample Trait Profiles:")
    examples = ['patrick', 'jenny', 'eloise', 'patrick_jr']
    for person_id in examples:
        if person_id in people and 'heritable_traits' in people[person_id]:
            person = people[person_id]
            print(f"\n  {person['name']}:")
            for trait_name, trait_data in person['heritable_traits'].items():
                trait_info = TRAITS[trait_name]
                genotype = trait_data['genotype']
                phenotype = trait_data['phenotype']
                print(f"    {trait_info['description']}: {genotype} → {phenotype}")

                # Show probabilities if available
                if 'probabilities' in trait_data:
                    print(f"      Possible: {trait_data['probabilities']}")

if __name__ == '__main__':
    main()
