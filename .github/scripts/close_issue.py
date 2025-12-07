#!/usr/bin/env python3
"""Close the processed issue with a success comment."""

import json
import subprocess

print("════════════════════════════════════════════════════════")
print("🔒 CLOSING ISSUE")
print("════════════════════════════════════════════════════════")

with open('/tmp/person_info.json', 'r') as f:
    person = json.load(f)

issue_number = person['issue_number']
person_name = person['name']
person_id = person['id']

print(f"📌 Closing issue #{issue_number}...")

comment_body = f"""## Person Successfully Added to Family Tree!

| Field | Value |
|-------|-------|
| **Name** | {person_name} |
| **ID** | `{person_id}` |

The family tree has been updated and will be visible on the website shortly.

**Next steps:**
- View on the [Family Tree](https://patruff.github.io/rufftree/)
- View on the [Family Graph](https://patruff.github.io/rufftree/graph.html)

---
*This issue was automatically processed by the test workflow.*"""

print("💬 Adding comment...")
result = subprocess.run([
    'gh', 'issue', 'comment', str(issue_number),
    '--body', comment_body
], capture_output=True, text=True)

if result.returncode == 0:
    print("✅ Comment added")
else:
    print(f"❌ Comment failed: {result.stderr}")

print("\n🏷️  Updating labels...")
result = subprocess.run([
    'gh', 'issue', 'edit', str(issue_number),
    '--remove-label', 'person:pending',
    '--add-label', 'person:added'
], capture_output=True, text=True)

if result.returncode == 0:
    print("✅ Labels updated")
else:
    print(f"⚠️  Label update warning: {result.stderr}")

print("\n🔒 Closing issue...")
result = subprocess.run([
    'gh', 'issue', 'close', str(issue_number)
], capture_output=True, text=True)

if result.returncode == 0:
    print(f"✅ Issue #{issue_number} closed!")
else:
    print(f"❌ Close failed: {result.stderr}")

print("════════════════════════════════════════════════════════")
