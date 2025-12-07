#!/usr/bin/env python3
"""Test script to process a single person issue with extensive debugging."""

import json
import os
import re
import sys

print("════════════════════════════════════════════════════════")
print("🚀 PROCESSING PERSON")
print("════════════════════════════════════════════════════════")

print("🐍 Python script started")
print(f"📂 Current directory: {os.getcwd()}")
print(f"📄 Files in directory: {os.listdir('.')[:10]}")

# Load issue
print("\n📋 Loading issue data...")
with open('/tmp/issue.json', 'r') as f:
    issue = json.load(f)

issue_number = issue['number']
issue_title = issue['title']
issue_body = issue['body']

print(f"📌 Issue #{issue_number}: {issue_title}")
print(f"📝 Body length: {len(issue_body)} characters")

# Check if family tree exists
if not os.path.exists('family_tree.json'):
    print("❌ ERROR: family_tree.json not found!")
    print(f"   Current directory: {os.getcwd()}")
    print(f"   Files available: {os.listdir('.')}")
    sys.exit(1)

print("\n✅ family_tree.json found")

# Load existing family tree
print("📚 Loading family tree...")
with open('family_tree.json', 'r') as f:
    family_data = json.load(f)

people = family_data['family']['people']
print(f"✅ Loaded family tree with {len(people)} people")

# Try to extract JSON from code block
print("\n🔍 Looking for JSON data in issue body...")
json_match = re.search(r'```json\s*([\s\S]*?)\s*```', issue_body)
person = None

if json_match:
    json_str = json_match.group(1).strip()
    print(f"✅ Found JSON block ({len(json_str)} chars)")
    print(f"📄 JSON content preview:\n{json_str[:200]}...")
    try:
        person = json.loads(json_str)
        print(f"✅ Successfully parsed JSON")
        print(f"   Person data keys: {list(person.keys())}")
        print(f"   Name: {person.get('name', 'N/A')}")
        print(f"   ID: {person.get('id', 'N/A')}")
        print(f"   DOB: {person.get('dob', 'N/A')}")
        print(f"   DOD: {person.get('dod', 'N/A')}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        person = None
else:
    print("ℹ️  No JSON block found")

# If no JSON, try form fields
if not person:
    print("\n📝 Parsing from form fields...")
    person = {}

    # Look for name
    name_match = re.search(r'(?:### Full Name|Name:)\s*\n\n(.+?)(?:\n\n###|\n\n|\Z)', issue_body, re.MULTILINE)
    if name_match:
        person['name'] = name_match.group(1).strip()
        print(f"✅ Found name: {person['name']}")
    else:
        print("❌ No name found")
        print("📄 Issue body preview:")
        print(issue_body[:500])

# Validate
if not person.get('name'):
    print("\n❌ ERROR: Person must have a name!")
    sys.exit(1)

person_name = person['name']
print(f"\n👤 Person name: {person_name}")

# Generate ID if needed
if 'id' not in person:
    safe_id = re.sub(r'[^a-z0-9]+', '_', person_name.lower()).strip('_')
    person['id'] = safe_id
    print(f"🔑 Generated ID: {safe_id}")

person_id = person['id']

# Check if already exists
if person_id in people:
    print(f"⚠️  Person {person_id} already exists in the family tree!")
    print(f"   Existing person: {people[person_id].get('name')}")
    print(f"   This appears to be a duplicate issue.")
    print(f"   Skipping to avoid creating duplicate entries.")
    # Don't save person_info.json - this signals to the workflow that we skipped
    sys.exit(0)

# Set defaults
print("\n🔧 Setting default relationship fields...")
if 'parentIds' not in person:
    person['parentIds'] = []
if 'siblingIds' not in person:
    person['siblingIds'] = []
if 'childrenIds' not in person:
    person['childrenIds'] = []
if 'spouseId' not in person:
    person['spouseId'] = None

# Ensure dob and dod fields exist
if 'dob' not in person or not person['dob']:
    person['dob'] = 'unknown'
    print("⚠️  No birth year found, setting to 'unknown'")
if 'dod' not in person or not person['dod']:
    person['dod'] = 'alive'
    print("⚠️  No death status found, setting to 'alive'")

print(f"   parentIds: {person['parentIds']}")
print(f"   siblingIds: {person['siblingIds']}")
print(f"   childrenIds: {person['childrenIds']}")
print(f"   spouseId: {person['spouseId']}")

# Handle spouse from JSON
if person.get('spouseId'):
    spouse_id = person['spouseId']
    print(f"\n🔗 Found spouse ID in JSON: {spouse_id}")
    if spouse_id in people:
        print(f"✅ Spouse {spouse_id} exists in tree")
        people[spouse_id]['spouseId'] = person_id
        person['childrenIds'] = people[spouse_id].get('childrenIds', []).copy()
        print(f"   Set bidirectional spouse relationship")
        print(f"   Inherited children: {person['childrenIds']}")
    else:
        print(f"⚠️  Spouse {spouse_id} not found in tree")

# Extract optional fields
occupation_match = re.search(r'### Occupation.*?\s*\n\n(.+?)(?:\n\n###|\Z)', issue_body)
if occupation_match and occupation_match.group(1).strip().lower() not in ['_no response_', '']:
    person['occupation'] = occupation_match.group(1).strip()
    print(f"💼 Occupation: {person.get('occupation')}")

location_match = re.search(r'### Home Location.*?\s*\n\n(.+?)(?:\n\n###|\Z)', issue_body)
if location_match and location_match.group(1).strip().lower() not in ['_no response_', '']:
    location = location_match.group(1).strip()
    if ',' in location:
        parts = location.split(',')
        person['home_city'] = parts[0].strip()
        person['home_state'] = parts[1].strip()
        print(f"🏠 Location: {person['home_city']}, {person['home_state']}")

# Add to tree
print(f"\n➕ Adding {person_name} to family tree...")
people[person_id] = person
print(f"✅ Added successfully!")
print(f"📊 Family tree now has {len(people)} people")

# Save
print("\n💾 Saving family tree...")
with open('family_tree.json', 'w') as f:
    json.dump(family_data, f, indent=2)
print("✅ Saved!")

# Save info for later steps
info = {
    'name': person_name,
    'id': person_id,
    'issue_number': issue_number,
    'occupation': person.get('occupation', 'Occupation unknown'),
    'home_city': person.get('home_city', ''),
    'home_state': person.get('home_state', '')
}

with open('/tmp/person_info.json', 'w') as f:
    json.dump(info, f, indent=2)

print("\n✅ Person processing complete!")
print(f"📋 Person info saved to /tmp/person_info.json")
print("════════════════════════════════════════════════════════")
