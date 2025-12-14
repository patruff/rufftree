# Integration Test - Uber Test

This directory contains a comprehensive integration test that validates the entire rufftree workflow from person creation to RAG querying.

## 🎯 What This Test Does

The **Uber Integration Test** (`test_integration_uber.py`) is a comprehensive end-to-end test that covers:

1. **CREATE** - Add a test person as child of Patrick Ruff
2. **VERIFY** - Check that Patrick Ruff's `childrenIds` is updated (bidirectional relationship)
3. **CREATE** - Upload a test story document to File Search RAG
4. **VERIFY** - Check that story appears in RAG documents
5. **QUERY** - Query the RAG system for the test story
6. **DELETE** - Remove test person and test story (cleanup)
7. **VERIFY** - Ensure cleanup was successful

## 🛠️ Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-asyncio` - Async test support
- `pytest-mock` - Mocking utilities
- All other project dependencies

### 2. Set Environment Variables

The test requires access to Google GenAI API:

```bash
export GOOGLE_GENAI_API_KEY="your-api-key-here"
```

Get your API key from: https://aistudio.google.com/apikey

### 3. Ensure Family Tree Exists

The test expects `family_tree.json` to exist with Patrick Ruff in it:

```bash
# Check that family_tree.json exists
ls -la family_tree.json

# Verify Patrick Ruff is present
grep "patrick" family_tree.json
```

## 🚀 Running the Test

### Run the Full Test Suite

```bash
pytest test_integration_uber.py -v -s
```

**Flags:**
- `-v` - Verbose output (shows each test name)
- `-s` - Show print statements (don't capture stdout)

### Run a Specific Test

```bash
# Run only the person creation test
pytest test_integration_uber.py::TestUberIntegration::test_01_create_person -v -s

# Run only the RAG query test
pytest test_integration_uber.py::TestUberIntegration::test_05_query_story_from_rag -v -s
```

### Run with Coverage

```bash
pytest test_integration_uber.py --cov=. --cov-report=html -v -s
```

This will generate a coverage report in `htmlcov/index.html`.

### Run as Standalone Script

```bash
python test_integration_uber.py
```

## 📋 Test Breakdown

### Test 1: Create Person
- Creates a test person: "Integration Test Person"
- Sets Patrick Ruff and Jenny Wang as parents
- Adds bidirectional relationships (parent ↔ child, siblings)
- Saves to `family_tree.json`

### Test 2: Verify Parent Relationship
- Reloads `family_tree.json` (verifies persistence)
- Checks test person has Patrick in `parentIds`
- **CRITICAL**: Verifies Patrick has test person in `childrenIds` (bidirectional)
- Verifies sibling relationships are bidirectional

### Test 3: Create Story and Upload to RAG
- Creates a test DOCX file with a story about Patrick and the test child
- Uploads to Google File Search store
- Waits for upload operation to complete
- Waits for document to be indexed and active

### Test 4: Verify Story in RAG
- Lists all documents in the RAG store
- Searches for the test story by filename
- Verifies document state is ACTIVE
- Checks document metadata (size, create time)

### Test 5: Query Story from RAG
- Queries the RAG system: "What did Patrick Ruff do with his test child?"
- Verifies a non-empty answer is returned
- Checks for citations
- Validates relevant keywords appear in the answer

### Test 6: Delete Story and Person
- Removes test person from `family_tree.json`
- Updates Patrick and Jenny's `childrenIds` (removes test person)
- Removes bidirectional sibling relationships
- Deletes test story from RAG store
- Deletes local DOCX file

### Test 7: Verify Cleanup
- Reloads family tree
- Verifies test person is gone
- Verifies Patrick's children no longer includes test person
- Ensures no orphaned relationships remain

## 🔍 What Gets Tested

### ✅ Person Management
- [x] Person creation with all required fields
- [x] ID generation and uniqueness
- [x] Parent-child relationships (bidirectional)
- [x] Sibling relationships (bidirectional)
- [x] JSON persistence
- [x] Person deletion
- [x] Relationship cleanup on deletion

### ✅ RAG System
- [x] Document upload to File Search store
- [x] Upload operation completion
- [x] Document indexing
- [x] Document state verification (ACTIVE)
- [x] Document querying with natural language
- [x] Citation extraction
- [x] Answer generation
- [x] Document deletion

### ✅ Data Integrity
- [x] Bidirectional relationships maintained
- [x] No orphaned relationships after deletion
- [x] JSON structure preserved
- [x] Proper cleanup/rollback

## 🧪 Expected Output

When running successfully, you should see:

```
================================================================================
🚀 UBER INTEGRATION TEST
================================================================================
...
================================================================================
TEST 1: CREATE PERSON
================================================================================
✅ Found Patrick Ruff: Patrick Ruff
✅ Created test person: Integration Test Person (id: test_integration_person)
✅ Added test_integration_person to Patrick's children
...
✅ TEST 1 PASSED: Person created successfully

================================================================================
TEST 2: VERIFY PARENT RELATIONSHIP
================================================================================
✅ Test person exists: Integration Test Person
✅ Patrick is in test person's parentIds: ['patrick', 'jenny']
✅ BIDIRECTIONAL relationship verified!
✅ TEST 2 PASSED: Parent relationship verified

================================================================================
TEST 3: CREATE STORY AND UPLOAD TO RAG
================================================================================
✅ Created test story DOCX: /tmp/20231214_testauthor_story_integration_test.docx
📤 Uploading to RAG store: fileSearchStores/rufftreefamilydocuments-nrf1ymofronp
✅ Upload operation completed
✅ Document indexed: fileSearchStores/.../documents/...
✅ TEST 3 PASSED: Story uploaded to RAG

...

✅ All 7 tests passed!
```

## 🐛 Troubleshooting

### Test Fails: "Patrick Ruff not found"
**Solution:** Ensure `family_tree.json` exists and contains Patrick Ruff with id "patrick"

### Test Fails: "GOOGLE_GENAI_API_KEY not set"
**Solution:** Set the environment variable:
```bash
export GOOGLE_GENAI_API_KEY="your-api-key-here"
```

### Test Fails: "Rufftree File Search store not found"
**Solution:** Ensure the rufftree File Search store exists. Run:
```bash
python test_file_search.py
```

### Test Hangs During Upload
**Solution:** Network issue or Google API timeout. The test has a 5-minute timeout. Check:
- Internet connection
- Google API quota limits
- API key validity

### Test Fails: "Document not indexed after 2 minutes"
**Solution:** Google indexing can be slow. The test waits 2 minutes. If this happens frequently:
- Increase timeout in `wait_for_document_indexing()`
- Check document size (large documents take longer)
- Verify API quota

### Cleanup Fails
**Solution:** If test fails mid-way, manually clean up:
```bash
# Remove test person from family_tree.json
python -c "
import json
with open('family_tree.json') as f:
    data = json.load(f)
if 'test_integration_person' in data['family']['people']:
    del data['family']['people']['test_integration_person']
    # Also remove from Patrick's children
    patrick = data['family']['people']['patrick']
    if 'test_integration_person' in patrick['childrenIds']:
        patrick['childrenIds'].remove('test_integration_person')
    with open('family_tree.json', 'w') as f:
        json.dump(data, f, indent=2)
    print('✅ Cleaned up test person')
"
```

## 📊 Coverage

After running with coverage:

```bash
pytest test_integration_uber.py --cov=. --cov-report=term-missing
```

This test provides integration coverage for:
- `family_tree.json` manipulation
- Google GenAI API integration
- Document creation and upload
- RAG querying
- Relationship management

**Note:** This is an integration test, not a unit test. It tests the system as a whole. For unit tests of individual functions, see the test coverage analysis document.

## 🔐 Safety

The test includes several safety features:

1. **Backup & Restore** - Family tree is backed up before tests and restored after
2. **Unique IDs** - Test person uses a unique ID that won't conflict with real people
3. **Cleanup** - Test 6 removes all test data (person, story, files)
4. **Verification** - Test 7 verifies cleanup was successful
5. **Isolation** - Test uses temp directory for DOCX files

## 🎓 Learning from This Test

This test demonstrates:

1. **Pytest Fixtures** - `google_client`, `file_search_store`, `backup_family_tree`
2. **Test Ordering** - Tests run in sequence (test_01, test_02, ...)
3. **Shared State** - Class variables share data between tests
4. **Integration Testing** - Tests multiple components together
5. **End-to-End Workflow** - Covers entire user journey
6. **Cleanup** - Proper teardown of test data

## 📝 Next Steps

After running this test successfully:

1. **Add More Edge Cases** - Test invalid data, missing fields, etc.
2. **Add Unit Tests** - Test individual functions in isolation
3. **Add CI/CD** - Run this test on every PR
4. **Add Performance Tests** - Test with large family trees
5. **Add Stress Tests** - Test concurrent person additions

## 📚 Related Files

- `test_integration_uber.py` - The main test file
- `family_tree.json` - Family tree data (modified by test)
- `requirements.txt` - Python dependencies (includes pytest)
- `test_file_search.py` - Standalone RAG testing script

## ❓ Questions?

If you encounter issues or have questions:

1. Check this README's Troubleshooting section
2. Review test output carefully (use `-s` flag)
3. Check that all prerequisites are met
4. Verify environment variables are set
5. Ensure family_tree.json is valid JSON

---

**Happy Testing! 🎉**
