#!/usr/bin/env python3
"""Process a person update issue to modify an existing person in the family tree."""

import json
import os
import re
import sys

print("════════════════════════════════════════════════════════")
print("🔄 UPDATING PERSON")
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

# Extract person ID from issue body
print("\n🔍 Looking for person ID in issue body...")
id_match = re.search(r'\*\*ID:\*\*\s+(\S+)', issue_body)
person_id = None

if id_match:
    person_id = id_match.group(1).strip()
    print(f"✅ Found person ID: {person_id}")
else:
    print("❌ Could not find person ID in issue body")
    sys.exit(1)

# Check if person exists
if person_id not in people:
    print(f"❌ ERROR: Person {person_id} not found in the family tree!")
    print(f"   Available IDs: {list(people.keys())[:10]}...")
    sys.exit(1)

print(f"✅ Found existing person: {people[person_id].get('name')}")

# Extract updated JSON from code block
print("\n🔍 Looking for updated JSON data in issue body...")
json_match = re.search(r'```json\s*([\s\S]*?)\s*```', issue_body)
updated_person = None

if json_match:
    json_str = json_match.group(1).strip()
    print(f"✅ Found JSON block ({len(json_str)} chars)")
    print(f"📄 JSON content preview:\n{json_str[:200]}...")
    try:
        updated_person = json.loads(json_str)
        print(f"✅ Successfully parsed JSON")
        print(f"   Person data keys: {list(updated_person.keys())}")
        print(f"   Name: {updated_person.get('name', 'N/A')}")
        print(f"   ID: {updated_person.get('id', 'N/A')}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        sys.exit(1)
else:
    print("❌ No JSON block found in issue body")
    sys.exit(1)

# Validate that the ID matches
if updated_person.get('id') != person_id:
    print(f"⚠️  WARNING: Updated person ID ({updated_person.get('id')}) doesn't match issue ID ({person_id})")
    print(f"   Using issue ID: {person_id}")
    updated_person['id'] = person_id

# Preserve critical relationship data if not explicitly provided
# This prevents accidental removal of relationships
existing_person = people[person_id]
print("\n🔧 Merging updated data with existing relationships...")

# If relationships aren't in the update or are null, preserve them from existing
# This handles both missing keys and null values from form submissions
if 'parentIds' not in updated_person or updated_person.get('parentIds') is None:
    updated_person['parentIds'] = existing_person.get('parentIds', [])
    print(f"   Preserved parentIds: {updated_person['parentIds']}")

if 'siblingIds' not in updated_person or updated_person.get('siblingIds') is None:
    updated_person['siblingIds'] = existing_person.get('siblingIds', [])
    print(f"   Preserved siblingIds: {updated_person['siblingIds']}")

if 'childrenIds' not in updated_person or updated_person.get('childrenIds') is None:
    updated_person['childrenIds'] = existing_person.get('childrenIds', [])
    print(f"   Preserved childrenIds: {updated_person['childrenIds']}")

if 'spouseId' not in updated_person or updated_person.get('spouseId') is None:
    updated_person['spouseId'] = existing_person.get('spouseId', None)
    print(f"   Preserved spouseId: {updated_person['spouseId']}")

# Track what changed
changes = []
for key in updated_person:
    old_val = existing_person.get(key)
    new_val = updated_person[key]
    if old_val != new_val:
        changes.append(f"   {key}: {old_val} → {new_val}")

if changes:
    print("\n📝 Changes detected:")
    for change in changes:
        print(change)
else:
    print("\n⚠️  No changes detected - data is identical")

# Update the person in the tree
print(f"\n🔄 Updating {updated_person.get('name')} in family tree...")
people[person_id] = updated_person
print(f"✅ Updated successfully!")

# Update bidirectional relationships
print("\n🔗 Updating bidirectional relationships...")
relationships_updated = 0

# Update siblings (bidirectional)
old_siblings = set(existing_person.get('siblingIds', []))
new_siblings = set(updated_person.get('siblingIds', []))

# Add this person to new siblings
for sibling_id in new_siblings:
    if sibling_id in people and person_id not in people[sibling_id].get('siblingIds', []):
        if 'siblingIds' not in people[sibling_id]:
            people[sibling_id]['siblingIds'] = []
        people[sibling_id]['siblingIds'].append(person_id)
        print(f"   ✓ Added {person_id} to {sibling_id}'s siblings")
        relationships_updated += 1

# Remove this person from old siblings that are no longer siblings
for old_sibling_id in old_siblings - new_siblings:
    if old_sibling_id in people and person_id in people[old_sibling_id].get('siblingIds', []):
        people[old_sibling_id]['siblingIds'].remove(person_id)
        print(f"   ✓ Removed {person_id} from {old_sibling_id}'s siblings")
        relationships_updated += 1

# Update parents (add this person to their children)
old_parents = set(existing_person.get('parentIds', []))
new_parents = set(updated_person.get('parentIds', []))

for parent_id in new_parents:
    if parent_id in people and person_id not in people[parent_id].get('childrenIds', []):
        if 'childrenIds' not in people[parent_id]:
            people[parent_id]['childrenIds'] = []
        people[parent_id]['childrenIds'].append(person_id)
        print(f"   ✓ Added {person_id} to {parent_id}'s children")
        relationships_updated += 1

for old_parent_id in old_parents - new_parents:
    if old_parent_id in people and person_id in people[old_parent_id].get('childrenIds', []):
        people[old_parent_id]['childrenIds'].remove(person_id)
        print(f"   ✓ Removed {person_id} from {old_parent_id}'s children")
        relationships_updated += 1

# Update children (add this person to their parents)
old_children = set(existing_person.get('childrenIds', []))
new_children = set(updated_person.get('childrenIds', []))

for child_id in new_children:
    if child_id in people and person_id not in people[child_id].get('parentIds', []):
        if 'parentIds' not in people[child_id]:
            people[child_id]['parentIds'] = []
        people[child_id]['parentIds'].append(person_id)
        print(f"   ✓ Added {person_id} to {child_id}'s parents")
        relationships_updated += 1

for old_child_id in old_children - new_children:
    if old_child_id in people and person_id in people[old_child_id].get('parentIds', []):
        people[old_child_id]['parentIds'].remove(person_id)
        print(f"   ✓ Removed {person_id} from {old_child_id}'s parents")
        relationships_updated += 1

# Update spouse (bidirectional)
old_spouse = existing_person.get('spouseId')
new_spouse = updated_person.get('spouseId')

if new_spouse and new_spouse != old_spouse:
    if new_spouse in people:
        people[new_spouse]['spouseId'] = person_id
        print(f"   ✓ Set {person_id} as spouse of {new_spouse}")
        relationships_updated += 1

if old_spouse and old_spouse != new_spouse:
    if old_spouse in people and people[old_spouse].get('spouseId') == person_id:
        people[old_spouse]['spouseId'] = None
        print(f"   ✓ Removed {person_id} as spouse of {old_spouse}")
        relationships_updated += 1

if relationships_updated == 0:
    print("   No relationship updates needed")
else:
    print(f"   Total relationship updates: {relationships_updated}")

# Save
print("\n💾 Saving family tree...")
with open('family_tree.json', 'w') as f:
    json.dump(family_data, f, indent=2)
print("✅ Saved!")

# Save info for later steps
person_name = updated_person.get('name', 'Unknown')
info = {
    'name': person_name,
    'id': person_id,
    'issue_number': issue_number,
    'occupation': updated_person.get('occupation', 'Occupation unknown'),
    'home_city': updated_person.get('home_city', ''),
    'home_state': updated_person.get('home_state', ''),
    'changes': len(changes),
    'action': 'updated'
}

with open('/tmp/person_info.json', 'w') as f:
    json.dump(info, f, indent=2)

print("\n✅ Person update complete!")
print(f"📋 Person info saved to /tmp/person_info.json")
print(f"📊 {len(changes)} fields updated")
print("════════════════════════════════════════════════════════")
