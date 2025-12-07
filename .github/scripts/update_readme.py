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
occupation = person['occupation']
home_city = person['home_city']
home_state = person['home_state']
location = f"{home_city}, {home_state}" if home_city and home_state else home_city or home_state or "Location unknown"

print(f"\n📝 Updating README with:")
print(f"   Name: {person_name}")
print(f"   Occupation: {occupation}")
print(f"   Location: {location}")
print(f"   Date: {date_str}")
print(f"   Issue: #{issue_number}")

# Find and update section
pattern = r'(## 🆕 Recent Additions\s+### Recently Added People\s+)(.*?)(\n### Recent Family Stories)'

def update_people_section(match):
    header = match.group(1)
    old_content = match.group(2)
    stories_header = match.group(3)

    people_lines = [line for line in old_content.strip().split('\n') if line.strip() and not line.startswith('>')]

    new_entry = f"- **{person_name}** - {occupation} from {location}. Added on {date_str}. _(Issue #{issue_number})_"

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
