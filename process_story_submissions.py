#!/usr/bin/env python3
"""
Process Story Submissions from Google Sheets

Reads new story submissions from a Google Sheet (fed by a Google Form)
and adds them to the RAG system automatically.

Setup:
1. Create a Google Form with fields: Title, About (who), Story, Author Name
2. Link form responses to a Google Sheet
3. Share the sheet with the service account email
4. Set STORY_SUBMISSIONS_SHEET_ID in environment or this script

The script tracks processed rows by adding a "Processed" column.
"""

import os
import sys
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Import our existing story function
from add_story_to_drive import add_story

# Configuration
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/documents'
]

# Column mapping (adjust based on your Google Form questions)
# Assumes: Timestamp | Title | About | Story | Author | Processed
COL_TIMESTAMP = 0
COL_TITLE = 1
COL_ABOUT = 2
COL_STORY = 3
COL_AUTHOR = 4
COL_PROCESSED = 5  # We'll add this column to track processed rows


def get_sheets_service():
    """Initialize Google Sheets API service."""
    creds_json = os.getenv("GOOGLE_DRIVE_CREDENTIALS")

    if not creds_json:
        raise ValueError(
            "GOOGLE_DRIVE_CREDENTIALS environment variable not set."
        )

    creds_info = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=SCOPES
    )

    service = build('sheets', 'v4', credentials=credentials)
    print("✅ Connected to Google Sheets API")
    return service


def get_sheet_id():
    """Get the Google Sheet ID from environment."""
    sheet_id = os.getenv("STORY_SUBMISSIONS_SHEET_ID")
    if not sheet_id:
        raise ValueError(
            "STORY_SUBMISSIONS_SHEET_ID environment variable not set. "
            "This should be the ID from your Google Sheet URL."
        )
    return sheet_id


def process_submissions():
    """Process new story submissions from the Google Sheet."""
    print("📖 Processing Story Submissions")
    print("=" * 60)

    sheets_service = get_sheets_service()
    sheet_id = get_sheet_id()

    # Read all data from the sheet
    print(f"\n📊 Reading from sheet: {sheet_id}")

    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='Form Responses 1'  # Default sheet name for form responses
        ).execute()
    except Exception as e:
        # Try alternative sheet name
        print(f"   Trying 'Sheet1' instead...")
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='Sheet1'
        ).execute()

    rows = result.get('values', [])

    if not rows:
        print("ℹ️  No data found in sheet")
        return 0

    # Skip header row
    header = rows[0]
    data_rows = rows[1:]

    print(f"   Found {len(data_rows)} submission(s)")

    # Check if we need to add "Processed" column to header
    if len(header) <= COL_PROCESSED or header[COL_PROCESSED] != 'Processed':
        print("   Adding 'Processed' column to track submissions...")
        # Extend header
        while len(header) <= COL_PROCESSED:
            header.append('')
        header[COL_PROCESSED] = 'Processed'

        # Update header in sheet
        sheets_service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range='Form Responses 1!A1',
            valueInputOption='RAW',
            body={'values': [header]}
        ).execute()

    # Process unprocessed rows
    processed_count = 0
    errors = []

    for i, row in enumerate(data_rows):
        row_num = i + 2  # +2 because of 0-index and header row

        # Extend row if needed
        while len(row) <= COL_PROCESSED:
            row.append('')

        # Skip if already processed
        if row[COL_PROCESSED] == 'Yes':
            continue

        # Extract story data
        try:
            title = row[COL_TITLE] if len(row) > COL_TITLE else ''
            about = row[COL_ABOUT] if len(row) > COL_ABOUT else ''
            story = row[COL_STORY] if len(row) > COL_STORY else ''
            author = row[COL_AUTHOR] if len(row) > COL_AUTHOR else 'Anonymous'

            if not title or not story:
                print(f"\n⚠️  Row {row_num}: Missing title or story, skipping")
                continue

            print(f"\n{'='*60}")
            print(f"📝 Processing Row {row_num}: {title}")
            print(f"   About: {about}")
            print(f"   Author: {author}")
            print(f"   Story length: {len(story)} chars")

            # Add the story using existing function
            add_story(title, about, story, author or 'Anonymous')

            # Mark as processed
            sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f'Form Responses 1!{chr(65 + COL_PROCESSED)}{row_num}',
                valueInputOption='RAW',
                body={'values': [['Yes']]}
            ).execute()

            processed_count += 1
            print(f"✅ Row {row_num} processed successfully!")

        except Exception as e:
            error_msg = f"Row {row_num}: {str(e)}"
            errors.append(error_msg)
            print(f"❌ Error processing row {row_num}: {e}")

            # Mark as error
            sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f'Form Responses 1!{chr(65 + COL_PROCESSED)}{row_num}',
                valueInputOption='RAW',
                body={'values': [[f'Error: {str(e)[:50]}']]}
            ).execute()

    # Summary
    print("\n" + "=" * 60)
    print("📊 PROCESSING SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully processed: {processed_count} story(ies)")
    if errors:
        print(f"❌ Errors: {len(errors)}")
        for err in errors:
            print(f"   - {err}")
    print("=" * 60)

    return processed_count


def main():
    """Entry point."""
    try:
        count = process_submissions()
        if count > 0:
            print(f"\n🎉 {count} new story(ies) added to the RAG system!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
