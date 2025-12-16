#!/usr/bin/env python3
"""Update README with the newly added person."""

import json
import re
from datetime import datetime

print("════════════════════════════════════════════════════════")
print("📝 UPDATING README")
print("════════════════════════════════════════════════════════")

print("📋 Loading person info...")
with open('/tmp/person_info.json', 'r') as f:
    person = json.load(f)

print(f"✅ Loaded: {person}")

# Get current date
date_str = datetime.now().strftime("%B %d, %Y")
print(f"📅 Date: {date_str}")

# Load family tree for total count
with open('family_tree.json', 'r') as f:
    family_data = json.load(f)

total_people = len(family_data['family']['people'])
print(f"📊 Total people: {total_people}")

# Read README
print("\n📖 Reading README...")
with open('README.md', 'r') as f:
    readme = f.read()

print(f"✅ README loaded ({len(readme)} chars)")

# Prepare values
person_name = person['name']
issue_number = person['issue_number']
action = person.get('action', 'added')  # Default to 'added' for backwards compatibility
action_verb = 'Updated' if action == 'updated' else 'Added'

# Generate relationship description
relationship_text = None
if person.get('spouseId'):
    spouse_id = person['spouseId']
    if spouse_id in family_data['family']['people']:
        spouse_name = family_data['family']['people'][spouse_id]['name']
        relationship_text = f"Spouse of {spouse_name}"
elif person.get('parentIds'):
    # Pick first parent
    parent_id = person['parentIds'][0]
    if parent_id in family_data['family']['people']:
        parent_name = family_data['family']['people'][parent_id]['name']
        relationship_text = f"Child of {parent_name}"
elif person.get('childrenIds'):
    # Pick first child
    child_id = person['childrenIds'][0]
    if child_id in family_data['family']['people']:
        child_name = family_data['family']['people'][child_id]['name']
        relationship_text = f"Parent of {child_name}"

if not relationship_text:
    relationship_text = "No immediate family listed"

print(f"\n📝 Updating README with:")
print(f"   Action: {action_verb}")
print(f"   Name: {person_name}")
print(f"   Relationship: {relationship_text}")
print(f"   Date: {date_str}")
print(f"   Issue: #{issue_number}")

# Find and update section
pattern = r'(## 🆕 Recent Additions\s+### Recently Added People\s+)(.*?)(\n### Recent Family Stories)'

def update_people_section(match):
    header = match.group(1)
    old_content = match.group(2)
    stories_header = match.group(3)

    people_lines = [line for line in old_content.strip().split('\n') if line.strip() and not line.startswith('>')]

    new_entry = f"- **{person_name}** - {relationship_text}. {action_verb} on {date_str}. _(Issue #{issue_number})_"

    second_person = ""
    if people_lines and not people_lines[0].startswith('- _('):
        if len(people_lines) > 0 and '(' in people_lines[0]:
            second_person = "\n" + people_lines[0]

    new_section = f"{header}{new_entry}{second_person}\n\n> **Total People in Family Tree:** {total_people}\n{stories_header}"
    return new_section

readme = re.sub(pattern, update_people_section, readme, flags=re.DOTALL)

# Write
print("\n💾 Writing updated README...")
with open('README.md', 'w') as f:
    f.write(readme)

print("✅ README updated!")
print("════════════════════════════════════════════════════════")
