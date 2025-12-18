#!/usr/bin/env python3
"""
Script to import contact information from CSV files:
- ruffdirectory.csv: Contact information (names, phones, emails, addresses)
- ruffoccasions.csv: Birthdays, anniversaries, and death dates

This script intelligently parses both files and adds people to the family tree.
"""

import json
import sys
import re
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
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


def create_person_id(name: str) -> str:
    """
    Create a person ID from their name.

    Args:
        name: Full name of the person

    Returns:
        ID string (lowercase, underscores instead of spaces)
    """
    # Remove special characters like +, &, etc.
    clean_name = re.sub(r'[^\w\s-]', '', name.lower())
    # Replace spaces and hyphens with underscores
    person_id = re.sub(r'[\s-]+', '_', clean_name.strip())
    return person_id


def parse_name_field(first_name: str, last_name: str) -> List[Tuple[str, Optional[str]]]:
    """
    Parse the First Name field which may contain multiple names and relationships.

    Args:
        first_name: The first name field from the directory
        last_name: The last name field

    Returns:
        List of tuples: [(full_name, maiden_name), ...]

    Examples:
        "Tom & Annemarie Thompson", "Abbott" -> [("Tom Abbott", None), ("Annemarie Thompson", "Thompson")]
        "Patrick & Jenny Wang", "Ruff" -> [("Patrick Ruff", None), ("Jenny Wang", "Wang")]
        "Mary Elizabeth", "Abbott" -> [("Mary Elizabeth Abbott", None)]
    """
    results = []

    # Handle deceased marker
    first_name = first_name.replace(' +', '').replace('+', '').strip()

    # Check for & pattern indicating spouse
    if '&' in first_name:
        parts = first_name.split('&')
        first_person = parts[0].strip()
        second_person = parts[1].strip()

        # First person gets the last name
        results.append((f"{first_person} {last_name}", None))

        # Second person might have their own last name
        if ' ' in second_person:
            # Has their own last name (e.g., "Jenny Wang")
            spouse_parts = second_person.split()
            spouse_last = spouse_parts[-1]
            results.append((second_person, spouse_last if spouse_last != last_name else None))
        else:
            # Uses the family last name
            results.append((f"{second_person} {last_name}", None))

    # Handle comma-separated names (e.g., "John Colin, Justin Tyler")
    elif ',' in first_name:
        names = [n.strip() for n in first_name.split(',')]
        for name in names:
            if name:
                results.append((f"{name} {last_name}", None))

    else:
        # Single person
        results.append((f"{first_name} {last_name}", None))

    return results


def parse_phone(phone_str: Optional[str]) -> Optional[str]:
    """
    Parse phone number, handling various formats and extracting primary number.

    Args:
        phone_str: Phone number string (may contain labels like "P" or "M")

    Returns:
        Cleaned phone number or None
    """
    if not phone_str or phone_str.strip() == '':
        return None

    # Remove labels like "302 995-1365 P" -> "302 995-1365"
    phone_str = re.sub(r'\s+[A-Z]+$', '', phone_str.strip())

    # If multiple numbers separated by semicolon, take the first
    if ';' in phone_str:
        phone_str = phone_str.split(';')[0].strip()

    return phone_str if phone_str else None


def parse_children(children_str: Optional[str]) -> Tuple[List[str], Optional[str]]:
    """
    Parse the children field which may contain children names, occupation, or notes.

    Args:
        children_str: String containing children, occupation, or other info

    Returns:
        Tuple of (children_list, notes)
    """
    if not children_str or children_str.strip() == '':
        return [], None

    # Check if it's likely an occupation (common keywords)
    occupation_keywords = ['Physical Therapist', 'Social Work', 'School Counselor',
                          'Banking', 'Customer Service', 'Yoga Instructor',
                          'fund raising', 'RN', 'Physician', 'UD', 'graduate']

    if any(keyword in children_str for keyword in occupation_keywords):
        return [], children_str

    # Check for relationship notes (e.g., "Mom - Rose Thompson Gola")
    if 'Mom -' in children_str or 'Dad -' in children_str or 'son -' in children_str:
        return [], children_str

    # Otherwise, try to extract children names
    # Split by comma and clean up
    potential_children = [child.strip() for child in children_str.split(',')]

    # Filter out entries that look like emails or notes
    children = []
    notes_parts = []

    for item in potential_children:
        if '@' in item or 'email' in item.lower() or '-' in item and 'Mom' in item:
            notes_parts.append(item)
        elif item and item != 'N/A':
            children.append(item)

    notes = '; '.join(notes_parts) if notes_parts else children_str if not children else None

    return children, notes


def is_deceased(name: str) -> bool:
    """Check if a person is marked as deceased (has + marker)."""
    return '+' in name


def parse_date(date_str: str) -> Optional[str]:
    """
    Parse date from occasions file (e.g., "1-Jan" -> "01-01" or year if available).

    Args:
        date_str: Date string like "1-Jan"

    Returns:
        Formatted date string or None
    """
    try:
        # Parse format like "1-Jan"
        date_parts = date_str.split('-')
        if len(date_parts) == 2:
            day = date_parts[0].zfill(2)
            month_abbr = date_parts[1]

            # Convert month abbreviation to number
            month_map = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }

            month = month_map.get(month_abbr, '01')
            return f"{month}-{day}"  # Return as MM-DD

    except Exception as e:
        print(f"Warning: Could not parse date '{date_str}': {e}")

    return None


def read_occasions_csv(file_path: str) -> Dict[str, Dict]:
    """
    Read the occasions CSV file and extract birthdays, anniversaries, and death dates.

    Args:
        file_path: Path to ruffoccasions.csv

    Returns:
        Dictionary mapping person names to their occasions
    """
    occasions = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            date = row['Date']
            family = row['Family']
            individual = row['Individual']
            occasion = row['Occasion']

            # Create a searchable name
            name_key = individual.lower().strip()

            if name_key not in occasions:
                occasions[name_key] = {
                    'birthdays': [],
                    'anniversaries': [],
                    'death_dates': [],
                    'family': family
                }

            parsed_date = parse_date(date)

            if occasion == 'Birthday':
                occasions[name_key]['birthdays'].append(parsed_date)
            elif occasion == 'Anniversary':
                occasions[name_key]['anniversaries'].append(parsed_date)
            elif occasion == 'Deceased':
                occasions[name_key]['death_dates'].append(parsed_date)

    return occasions


def find_matching_occasion(full_name: str, occasions: Dict) -> Optional[Dict]:
    """
    Find matching occasion data for a person.

    Args:
        full_name: Full name of the person
        occasions: Dictionary of occasions from ruffoccasions.csv

    Returns:
        Occasion data if found
    """
    # Try exact match first
    name_key = full_name.lower().strip()
    if name_key in occasions:
        return occasions[name_key]

    # Try just first name
    first_name = full_name.split()[0].lower()
    if first_name in occasions:
        return occasions[first_name]

    # Try last name
    if ' ' in full_name:
        last_name = full_name.split()[-1].lower()
        if last_name in occasions:
            return occasions[last_name]

    # Try partial matches
    for occ_name, occ_data in occasions.items():
        if first_name in occ_name or occ_name in name_key:
            return occ_data

    return None


def import_from_csvs(directory_csv: str, occasions_csv: str, dry_run: bool = False):
    """
    Import contacts from CSV files and add to family tree.

    Args:
        directory_csv: Path to ruffdirectory.csv
        occasions_csv: Path to ruffoccasions.csv
        dry_run: If True, show what would be added without saving
    """
    print("\n" + "="*80)
    print("📇 RUFF FAMILY CSV IMPORT")
    print("="*80 + "\n")

    # Load existing family tree
    family_data = load_family_data()
    people = family_data['family']['people']

    print(f"📊 Current family tree has {len(people)} people\n")

    # Read occasions first
    print(f"📖 Reading occasions from: {occasions_csv}")
    occasions = read_occasions_csv(occasions_csv)
    print(f"✅ Loaded {len(occasions)} occasion entries\n")

    # Read directory
    print(f"📖 Reading directory from: {directory_csv}")

    new_people = []
    updated_people = []

    with open(directory_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            last_name = row['Last Name']
            first_name = row['First Name']

            if not last_name or not first_name:
                continue

            # Parse names to identify individuals
            persons_names = parse_name_field(first_name, last_name)

            for idx, (full_name, maiden_name) in enumerate(persons_names):
                # Create person ID
                person_id = create_person_id(full_name)

                # Check if person already exists
                existing_person = None
                for pid, pdata in people.items():
                    if pdata.get('name', '').lower() == full_name.lower():
                        existing_person = pid
                        person_id = pid
                        break

                # Create or update person
                person = people.get(existing_person, {}) if existing_person else {}

                person['id'] = person_id
                person['name'] = full_name

                # Set birth/death status
                if is_deceased(row['First Name']):
                    person['dod'] = person.get('dod', 'Unknown')
                else:
                    person['dod'] = person.get('dod', 'alive')

                # Try to find birthday/death date from occasions
                occasion_data = find_matching_occasion(full_name, occasions)
                if occasion_data:
                    if occasion_data['birthdays'] and not person.get('dob'):
                        person['dob'] = occasion_data['birthdays'][0]
                    if occasion_data['death_dates'] and person.get('dod') != 'alive':
                        person['dod'] = occasion_data['death_dates'][0]

                # Set default dob if not found
                if 'dob' not in person:
                    person['dob'] = 'Unknown'

                # Add contact information (only for the first person in a couple)
                if idx == 0:
                    phone = parse_phone(row.get('Phone', '')) or parse_phone(row.get('Cell', ''))
                    if phone:
                        person['phone'] = phone

                    email = row.get('Email', '').strip()
                    if email and email != 'N/A':
                        person['email'] = email

                    # Add address information
                    if row.get('Address'):
                        person['address'] = row['Address']
                    if row.get('Address2'):
                        person['address2'] = row['Address2']
                    if row.get('City'):
                        person['city'] = row['City']
                        person['home_city'] = row['City']
                    if row.get('State'):
                        person['state'] = row['State']
                        person['home_state'] = row['State']
                    if row.get('Zip'):
                        person['zip'] = str(row['Zip']).replace('.0', '')

                # Parse children/notes
                children, notes = parse_children(row.get('Children', ''))
                if children:
                    child_notes = f"Children: {', '.join(children)}"
                    if person.get('notes'):
                        person['notes'] += f"; {child_notes}"
                    else:
                        person['notes'] = child_notes
                elif notes:
                    if person.get('notes'):
                        person['notes'] += f"; {notes}"
                    else:
                        person['notes'] = notes

                # Add maiden name if present
                if maiden_name:
                    person['maidenName'] = maiden_name

                # Handle spouse relationship
                if len(persons_names) == 2:
                    other_idx = 1 - idx
                    spouse_name = persons_names[other_idx][0]
                    spouse_id = create_person_id(spouse_name)
                    person['spouseId'] = spouse_id

                # Add or update in the tree
                if existing_person:
                    # Merge with existing
                    for key, value in person.items():
                        if value and value not in ['N/A', 'Unknown', '']:
                            people[person_id][key] = value
                    updated_people.append(full_name)
                    print(f"  ✏️  Updated: {full_name}")
                else:
                    people[person_id] = person
                    new_people.append(full_name)
                    print(f"  ✨ Added: {full_name}")

    # Summary
    print("\n" + "="*80)
    print("📊 IMPORT SUMMARY")
    print("="*80)
    print(f"✨ New people added: {len(new_people)}")
    print(f"✏️  People updated: {len(updated_people)}")
    print(f"📊 Total people in tree: {len(people)}")

    if dry_run:
        print("\n🔍 DRY RUN - No changes saved")
        print("\nRun without --dry-run to save changes")
    else:
        # Save updated family tree
        family_data['family']['people'] = people
        save_family_data(family_data)
        print("\n✅ Family tree updated successfully!")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Import Ruff Family data from CSV files'
    )
    parser.add_argument(
        '--directory',
        default='ruffdirectory.csv',
        help='Path to the directory CSV file (default: ruffdirectory.csv)'
    )
    parser.add_argument(
        '--occasions',
        default='ruffoccasions.csv',
        help='Path to the occasions CSV file (default: ruffoccasions.csv)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be imported without making changes'
    )

    args = parser.parse_args()

    # Check if files exist
    if not Path(args.directory).exists():
        print(f"❌ Error: Directory file not found: {args.directory}")
        sys.exit(1)

    if not Path(args.occasions).exists():
        print(f"❌ Error: Occasions file not found: {args.occasions}")
        sys.exit(1)

    # Import data
    import_from_csvs(args.directory, args.occasions, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
