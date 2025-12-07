#!/usr/bin/env python3
"""Close a story issue with a success comment."""

import os
import subprocess
import sys

# Get issue info from environment
issue_number = os.environ.get('ISSUE_NUM')
story_title = os.environ.get('STORY_TITLE', 'Unknown')
story_about = os.environ.get('STORY_ABOUT', 'Family')
story_author = os.environ.get('STORY_AUTHOR', 'Anonymous')

if not issue_number:
    print("❌ ERROR: ISSUE_NUM environment variable not set")
    sys.exit(1)

print(f"📌 Closing story issue #{issue_number}...")

comment_body = f"""## ✅ Story Added Successfully!

The story has been added to the family archive and is now searchable.

**Story Details:**
- Title: {story_title}
- About: {story_about}
- Author: {story_author}

Thank you for sharing this family memory! 🙏

---
*This story was automatically processed and added to the family archive.*"""

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
subprocess.run([
    'gh', 'issue', 'edit', str(issue_number),
    '--remove-label', 'story:pending',
    '--add-label', 'story:processed'
], capture_output=True, text=True)

print("\n🔒 Closing issue...")
result = subprocess.run([
    'gh', 'issue', 'close', str(issue_number)
], capture_output=True, text=True)

if result.returncode == 0:
    print(f"✅ Story issue #{issue_number} closed!")
else:
    print(f"❌ Close failed: {result.stderr}")
    sys.exit(1)
