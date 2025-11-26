#!/usr/bin/env python3
"""
Script to extract a person's immediate family tree and upload to Google Drive.
This is designed to run in GitHub Actions workflows.
"""

import json
import sys
import os
import io
from pathlib import Path
from typing import Optional, Dict
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from datetime import datetime


SCOPES = ['https://www.googleapis.com/auth/drive.file']
DRIVE_FOLDER_NAME = "rufftree_person_trees"


def load_family_data():
    """Load the family tree JSON data."""
    with open('family_tree.json', 'r') as f:
        return json.load(f)


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
        print(f"⚠️  Multiple matches found for '{name}', using first match:")
        for i, (pid, p) in enumerate(matches, 1):
            dod_text = p['dod'] if p['dod'] != 'alive' else 'Present'
            print(f"  {i}. {p['name']} ({p['dob']} - {dod_text})")
        print(f"\n✅ Selected: {matches[0][1]['name']}")
        return matches[0]

    return None


def format_person_info(person: Dict, person_id: str) -> str:
    """Format a person's basic info for display."""
    name = person['name']
    dob = person['dob']
    dod = person['dod'] if person['dod'] != 'alive' else 'Present'

    age_info = ""
    if person['dod'] == 'alive':
        try:
            current_year = datetime.now().year
            age = current_year - int(dob)
            age_info = f" (age {age})"
        except:
            pass
    else:
        try:
            years_lived = int(person['dod']) - int(dob)
            age_info = f" (lived {years_lived} years)"
        except:
            pass

    gen_info = ""
    if 'generation' in person:
        gen_info = f" - {person['generation']}"

    location_info = ""
    if person.get('home_city') or person.get('home_state'):
        location = ', '.join(filter(None, [person.get('home_city'), person.get('home_state')]))
        location_info = f" - {location}"

    return f"{name} ({dob} - {dod}{age_info}){gen_info}{location_info}"


def get_immediate_family(person_id: str, person: Dict, people: Dict) -> Dict:
    """Extract immediate family tree for a person."""
    family_tree = {
        'person': {
            'id': person_id,
            'info': format_person_info(person, person_id),
            'data': person
        },
        'parents': [],
        'siblings': [],
        'spouse': None,
        'children': []
    }

    # Get parents
    for parent_id in person.get('parentIds', []):
        if parent_id in people:
            parent = people[parent_id]
            family_tree['parents'].append({
                'id': parent_id,
                'info': format_person_info(parent, parent_id),
                'data': parent
            })

    # Get siblings
    for sibling_id in person.get('siblingIds', []):
        if sibling_id in people:
            sibling = people[sibling_id]
            family_tree['siblings'].append({
                'id': sibling_id,
                'info': format_person_info(sibling, sibling_id),
                'data': sibling
            })

    # Get spouse
    spouse_id = person.get('spouseId')
    if spouse_id and spouse_id in people:
        spouse = people[spouse_id]
        family_tree['spouse'] = {
            'id': spouse_id,
            'info': format_person_info(spouse, spouse_id),
            'data': spouse
        }

    # Get children
    for child_id in person.get('childrenIds', []):
        if child_id in people:
            child = people[child_id]
            family_tree['children'].append({
                'id': child_id,
                'info': format_person_info(child, child_id),
                'data': child
            })

    return family_tree


def display_family_tree(family_tree: Dict):
    """Display the family tree in a readable format."""
    print("\n" + "=" * 80)
    print("IMMEDIATE FAMILY TREE")
    print("=" * 80)

    print(f"\n👤 PERSON:")
    print(f"   {family_tree['person']['info']}")

    if family_tree['parents']:
        print(f"\n👨‍👩 PARENTS ({len(family_tree['parents'])}):")
        for parent in family_tree['parents']:
            print(f"   • {parent['info']}")
    else:
        print(f"\n👨‍👩 PARENTS: None recorded")

    if family_tree['spouse']:
        print(f"\n💑 SPOUSE:")
        print(f"   • {family_tree['spouse']['info']}")
    else:
        print(f"\n💑 SPOUSE: None recorded")

    if family_tree['siblings']:
        print(f"\n👥 SIBLINGS ({len(family_tree['siblings'])}):")
        for sibling in family_tree['siblings']:
            print(f"   • {sibling['info']}")
    else:
        print(f"\n👥 SIBLINGS: None recorded")

    if family_tree['children']:
        print(f"\n👶 CHILDREN ({len(family_tree['children'])}):")
        for child in family_tree['children']:
            print(f"   • {child['info']}")
    else:
        print(f"\n👶 CHILDREN: None recorded")

    print("\n" + "=" * 80)


def get_drive_service():
    """Initialize Google Drive API service using service account credentials."""
    creds_json = os.getenv("GOOGLE_DRIVE_CREDENTIALS")

    if not creds_json:
        raise ValueError(
            "GOOGLE_DRIVE_CREDENTIALS environment variable not set. "
            "This should contain your service account JSON credentials."
        )

    try:
        creds_info = json.loads(creds_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in GOOGLE_DRIVE_CREDENTIALS: {e}")

    credentials = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=SCOPES
    )

    service = build('drive', 'v3', credentials=credentials)
    print("✅ Connected to Google Drive API")

    return service


def find_or_create_folder(service, folder_name: str) -> str:
    """Find a folder by name, or create it if it doesn't exist."""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)'
    ).execute()

    files = results.get('files', [])

    if files:
        folder_id = files[0]['id']
        print(f"📁 Found existing folder: {folder_name} (ID: {folder_id})")
        return folder_id

    # Create folder
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    folder = service.files().create(
        body=file_metadata,
        fields='id'
    ).execute()

    folder_id = folder.get('id')
    print(f"📁 Created new folder: {folder_name} (ID: {folder_id})")

    return folder_id


def upload_to_drive(service, folder_id: str, file_name: str, content: str) -> str:
    """Upload a JSON file to Google Drive."""
    # Create file metadata
    file_metadata = {
        'name': file_name,
        'parents': [folder_id],
        'mimeType': 'application/json'
    }

    # Create media from string content
    media = MediaIoBaseUpload(
        io.BytesIO(content.encode('utf-8')),
        mimetype='application/json',
        resumable=True
    )

    # Upload file
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, webViewLink'
    ).execute()

    file_id = file.get('id')
    web_link = file.get('webViewLink', 'N/A')

    print(f"📤 Uploaded to Drive: {file_name}")
    print(f"   File ID: {file_id}")
    print(f"   Link: {web_link}")

    return file_id


def create_focused_json(family_tree: Dict) -> str:
    """Create a focused JSON with just this person's immediate family."""
    focused_data = {
        'generated_at': datetime.now().isoformat(),
        'person': family_tree['person']['data'],
        'parents': [p['data'] for p in family_tree['parents']],
        'siblings': [s['data'] for s in family_tree['siblings']],
        'spouse': family_tree['spouse']['data'] if family_tree['spouse'] else None,
        'children': [c['data'] for c in family_tree['children']]
    }

    return json.dumps(focused_data, indent=2)


def main():
    """Main function to run the immediate family tree extraction and upload."""
    if len(sys.argv) < 2:
        print("❌ Error: No person name provided")
        print("Usage: python3 generate_person_tree_to_drive.py 'Person Name'")
        sys.exit(1)

    search_name = ' '.join(sys.argv[1:])

    # Load data
    print("Loading family tree data...")
    data = load_family_data()
    people = data['family']['people']
    print(f"Loaded {len(people)} family members.")

    # Search for person
    print(f"\nSearching for '{search_name}'...")
    result = search_person(search_name, people)

    if not result:
        print(f"\n❌ No match found for '{search_name}'")
        print("\nTip: Try searching by first name only, or check spelling.")
        sys.exit(1)

    person_id, person = result
    print(f"✅ Found: {person['name']}")

    # Get immediate family
    family_tree = get_immediate_family(person_id, person, people)

    # Display results
    display_family_tree(family_tree)

    # Create JSON content
    json_content = create_focused_json(family_tree)

    # Generate filename
    safe_name = person['name'].lower().replace(' ', '_').replace("'", "")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"{safe_name}_family_tree_{timestamp}.json"

    # Upload to Google Drive
    print(f"\n📤 Uploading to Google Drive...")
    drive_service = get_drive_service()
    folder_id = find_or_create_folder(drive_service, DRIVE_FOLDER_NAME)
    file_id = upload_to_drive(drive_service, folder_id, file_name, json_content)

    print("\n" + "=" * 80)
    print("✅ SUCCESS!")
    print("=" * 80)
    print(f"📁 Folder: {DRIVE_FOLDER_NAME}")
    print(f"📄 File: {file_name}")
    print(f"🆔 File ID: {file_id}")
    print("=" * 80)


if __name__ == '__main__':
    main()
