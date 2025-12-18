# Ruff Directory Excel Files

Place your Ruff Family Directory Excel file in this folder.

## Expected File

The import script looks for `RuffDirectory.xlsx` by default, but you can specify any filename when running the script.

## Format

Your Excel file should contain a sheet with contact information in the following format:

### Column Headers (First Row)

```
Last Name | First Name | Phone | Cell | Email | Children | Address | Address2 | City | State | Zip
```

### Example Data

```
Ruff | Patrick & Jenny Wang | 302-353-8986 | 302 353-8986 | patruff@gmail.com | Jenny's email - jenny727@gmail.com | 442 W 57th St | Apt 3B | New York | NY | 10019
```

## Usage

Once you've placed your Excel file here, run:

```bash
# From the rufftree directory
python import_ruff_directory.py ruffdirectory/YourFileName.xlsx

# Or if using the default filename RuffDirectory.xlsx
python import_ruff_directory.py
```

See `IMPORT_DIRECTORY_README.md` for complete documentation.
