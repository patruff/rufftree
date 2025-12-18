# Ruff Family Directory Import Tool

This tool imports contact information from an Excel spreadsheet (the Ruff Family Directory) and adds people to the family tree database.

## Overview

The `import_ruff_directory.py` script reads an Excel file containing family contact information and automatically:
- Creates new person entries in the family tree
- Updates existing person entries with contact information
- Parses names to identify married couples (using "&" separator)
- Extracts phone numbers, emails, and addresses
- Records children information in notes

## File Format

The Excel file should have the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| Last Name | Family surname | Ruff |
| First Name | First name(s), possibly with spouse | Patrick & Jenny Wang |
| Phone | Primary phone number | 302-353-8986 |
| Cell | Cell phone number | 302 353-8986 |
| Email | Email address | patruff@gmail.com |
| Children | Children names (comma-separated) | Mary Elizabeth, Tommy |
| Address | Street address | 442 W 57th St |
| Address2 | Address line 2 (apt, neighborhood) | Apt 3B |
| City | City name | New York |
| State | State abbreviation | NY |
| Zip | Zip code | 10019 |

## Usage

### Basic Usage

```bash
# Import from default location
python import_ruff_directory.py

# Import from specific file
python import_ruff_directory.py path/to/directory.xlsx

# Dry run (preview without saving)
python import_ruff_directory.py --dry-run
```

### Installation

First, install the required dependencies:

```bash
pip install -r requirements.txt
```

This will install `openpyxl` which is needed to read Excel files.

## Features

### Name Parsing

The script intelligently parses the "First Name" field to identify:

1. **Single individuals**: `"Mary Elizabeth"` → Creates one person
2. **Married couples**: `"Tom & Annemarie Thompson"` → Creates two people with spouse relationship
3. **Couples with different surnames**: `"Patrick & Jenny Wang"` → Records maiden name for spouse

### Contact Information

The script extracts and stores:
- **Phone numbers**: Prefers Cell if available, falls back to Phone
- **Email addresses**: Stored directly on the person record
- **Physical addresses**: Full address with street, city, state, zip
  - Also populates `home_city` and `home_state` fields for location tracking

### Children

Children names from the "Children" column are stored in the person's `notes` field in the format:
```
Children: Mary Elizabeth, Tommy, Khristina, Gianni Thompson
```

### Duplicate Handling

- **Existing people**: If a person with the same name already exists, their record is updated with new information
- **Missing data**: Existing data is preserved unless new data is provided
- **Smart merging**: Won't overwrite existing data with "N/A" or "Unknown" values

## Example

Given this row in the Excel file:

```
Last Name: Ruff
First Name: Patrick & Jenny Wang
Phone: 302-353-8986
Email: patruff@gmail.com
Children: Jenny's email - jenny727@gmail.com
Address: 442 W 57th St
Address2: Apt 3B
City: New York
State: NY
Zip: 10019
```

The script creates two people:

```json
{
  "patrick_ruff": {
    "id": "patrick_ruff",
    "name": "Patrick Ruff",
    "phone": "302-353-8986",
    "email": "patruff@gmail.com",
    "address": "442 W 57th St",
    "address2": "Apt 3B",
    "city": "New York",
    "home_city": "New York",
    "state": "NY",
    "home_state": "NY",
    "zip": "10019",
    "spouseId": "jenny_wang",
    "dob": "Unknown",
    "dod": "alive"
  },
  "jenny_wang": {
    "id": "jenny_wang",
    "name": "Jenny Wang",
    "maidenName": "Wang",
    "spouseId": "patrick_ruff",
    "dob": "Unknown",
    "dod": "alive"
  }
}
```

## Output

The script provides detailed output:

```
================================================================================
📇 RUFF FAMILY DIRECTORY IMPORT
================================================================================

📊 Current family tree has 145 people
📖 Reading Excel file: ruffdirectory/RuffDirectory.xlsx
📋 Found columns: ['Last Name', 'First Name', 'Phone', 'Cell', 'Email', ...]

  Processing row 1: Tom & Annemarie Thompson Abbott
  ✨ Added: Tom Abbott
  ✨ Added: Annemarie Thompson

  Processing row 2: Mary Elizabeth Abbott
  ✏️  Updated: Mary Elizabeth Abbott

================================================================================
📊 IMPORT SUMMARY
================================================================================
✨ New people added: 87
✏️  People updated: 23
📊 Total people in tree: 232

💾 Saved updated family tree to family_tree.json
✅ Family tree updated successfully!
```

## Dry Run Mode

Use `--dry-run` to preview what would be imported without making any changes:

```bash
python import_ruff_directory.py --dry-run
```

This is useful for:
- Checking if the file format is correct
- Seeing how many new people will be added
- Identifying potential duplicates or issues

## Notes

1. **Default file path**: The script looks for `ruffdirectory/RuffDirectory.xlsx` by default
2. **Backup**: Consider backing up `family_tree.json` before running the import
3. **Person IDs**: Generated automatically from names (lowercase with underscores)
4. **Relationships**: Currently only creates spouse relationships; parent/child relationships should be added separately
5. **Date of birth**: Set to "Unknown" by default; update manually for known dates

## Troubleshooting

### File not found error

```
❌ Error: File not found: ruffdirectory/RuffDirectory.xlsx
```

**Solution**: Specify the correct path to your Excel file:
```bash
python import_ruff_directory.py path/to/your/file.xlsx
```

### Missing openpyxl

```
ModuleNotFoundError: No module named 'openpyxl'
```

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Column names don't match

The script expects specific column names. Make sure your Excel file has these exact column headers:
- Last Name
- First Name
- Phone
- Cell
- Email
- Children
- Address
- Address2
- City
- State
- Zip

## Future Enhancements

Potential improvements:
- [ ] Parse relationship information from Children field
- [ ] Extract occupation from notes/children field
- [ ] Handle multiple phone numbers
- [ ] Parse generation information
- [ ] Support for CSV format
- [ ] Interactive mode for resolving duplicates
