# Generated People

This folder contains JSON files for family members generated using the Person Generator tool.

## How to Use

1. **Generate a Person**: Visit `person_generator.html` and fill out the form
2. **Download JSON**: Click "Download JSON" to save the file
3. **Add to Repo**: Add the downloaded JSON file to this `generated_people/` folder
4. **Integrate**:
   - Push to the repository, or
   - Go to Actions → "Integrate Generated People" → "Run workflow"
5. **Automatic Integration**: The workflow will:
   - Read all `.json` files in this folder
   - Add them to `family_tree.json`
   - Move processed files to `generated_people/processed/`

## Processed Files

Files that have been successfully integrated are moved to `generated_people/processed/` to prevent duplicate processing.

## JSON Format

Each generated person JSON file contains:

```json
{
  "id": "unique_identifier",
  "name": "First Last",
  "firstName": "First",
  "lastName": "Last",
  "dob": "1985",
  "dod": "alive",
  "hairColor": "brunette",
  "height": "tall",
  "education": "college",
  "occupation": "Engineer",
  "notes": "Additional information",
  "spouseId": null,
  "parentIds": [],
  "siblingIds": [],
  "childrenIds": []
}
```

## Adding Relationships

After a person is integrated into the family tree, you can manually edit `family_tree.json` to add relationships:

- Set `spouseId` to the ID of their spouse
- Add parent IDs to `parentIds` array
- Add sibling IDs to `siblingIds` array
- Add children IDs to `childrenIds` array

The family tree visualization will automatically show these relationships.
