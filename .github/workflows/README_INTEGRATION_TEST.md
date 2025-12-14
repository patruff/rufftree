# Integration Test GitHub Action

This workflow runs the comprehensive integration test in **complete isolation** - zero traces left in the repository.

## 🎯 Purpose

Validates the entire rufftree system:
- Person CRUD operations
- Bidirectional relationship management
- RAG document upload and indexing
- Natural language querying
- Data integrity and cleanup

## 🔒 Zero-Trace Guarantee

**This workflow NEVER commits anything back to the repository.**

### Safety Features

1. **Backup Before Test**
   - `family_tree.json` → `family_tree.json.ci-backup`
   - `contributors.json` → `contributors.json.ci-backup`
   - `README.md` → `README.md.ci-backup`

2. **CI Mode Enabled**
   - Sets `CI_MODE=true` environment variable
   - Test runs in isolation
   - No contributor tracking
   - No README updates
   - No workflow triggers

3. **Restore After Test** (even on failure)
   - Restores all backups
   - Verifies `git diff` shows no changes
   - Cleans up test artifacts

4. **Cleanup**
   - Removes temp DOCX files
   - Removes RAG test documents
   - Removes pytest cache
   - Removes coverage reports

## 🚀 How to Run

### Manual Trigger (GitHub UI)

1. Go to **Actions** tab
2. Click "Integration Test (Uber Test)"
3. Click "Run workflow"
4. Select branch (default: main)
5. Choose verbose output (optional)
6. Click "Run workflow"

### Manual Trigger (GitHub CLI)

```bash
gh workflow run integration-test.yml
```

### Manual Trigger (API)

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/patruff/rufftree/actions/workflows/integration-test.yml/dispatches \
  -d '{"ref":"main"}'
```

## 📅 Schedule

**Automatic Run:** Every Sunday at 2:00 AM UTC

This provides weekly validation that the system is healthy.

## 🔧 Configuration

### Required Secrets

- `GOOGLE_GENAI_API_KEY` - Google GenAI API key for RAG testing

**To set:**
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click "New repository secret"
3. Name: `GOOGLE_GENAI_API_KEY`
4. Value: Your API key from https://aistudio.google.com/apikey

### Workflow File

Location: `.github/workflows/integration-test.yml`

Key settings:
- **Timeout:** 15 minutes
- **Runner:** ubuntu-latest
- **Python:** 3.11

## 📊 What Gets Tested

### Test 1: Create Person
- Creates test child of Patrick Ruff
- Verifies bidirectional parent-child links
- Checks sibling relationships

### Test 2: Verify Relationships
- Reloads family tree (persistence)
- Validates bidirectional updates
- Confirms no orphaned references

### Test 3: Upload Story to RAG
- Creates test DOCX file
- Uploads to Google File Search
- Waits for indexing

### Test 4: Verify RAG Document
- Lists documents in store
- Finds test document
- Checks ACTIVE state

### Test 5: Query RAG
- Natural language query
- Validates answer quality
- Checks citations

### Test 6: Cleanup
- Deletes test person
- Removes RAG document
- Cleans relationships

### Test 7: Verify Cleanup
- Confirms test person removed
- Validates no orphaned data
- Ensures family tree is clean

## 📈 Success Criteria

**All 7 tests must pass** for the workflow to succeed.

Expected output:
```
✅ TEST 1 PASSED: Person created successfully
✅ TEST 2 PASSED: Parent relationship verified
✅ TEST 3 PASSED: Story uploaded to RAG
✅ TEST 4 PASSED: Story verified in RAG
✅ TEST 5 PASSED: Story queried from RAG
✅ TEST 6 PASSED: Cleanup completed
✅ TEST 7 PASSED: Cleanup verified
```

## ❌ Failure Handling

If any test fails:

1. **Workflow Status:** ❌ Failed (red X in Actions tab)
2. **Data Restored:** All backups automatically restored
3. **Logs Available:** Full test output in workflow logs
4. **No Side Effects:** No data committed to repository

## 🔍 Viewing Results

### Via GitHub UI

1. Go to **Actions** tab
2. Click on the workflow run
3. Click on "Run Uber Integration Test" job
4. Expand test steps to see detailed output

### Via GitHub CLI

```bash
# List recent runs
gh run list --workflow=integration-test.yml

# View latest run
gh run view --log

# View specific run
gh run view <run-id> --log
```

## 🐛 Troubleshooting

### Test Fails: "GOOGLE_GENAI_API_KEY not set"

**Fix:** Add the secret to repository settings (see Configuration above)

### Test Fails: "Rufftree File Search store not found"

**Fix:** Ensure the File Search store exists:
1. Run `python test_file_search.py` locally
2. Verify store is created
3. Store name should contain "rufftree"

### Test Hangs on Upload

**Possible Causes:**
- Google API timeout
- Network issues
- Large document size

**Fix:**
- Check Google API status
- Verify API quota
- Re-run workflow

### Cleanup Fails

**What Happens:**
- Workflow restores backups automatically
- Even if cleanup fails, data is safe
- Check logs for specific error

## 📝 Workflow Steps Explained

### 1. Checkout Repository
- Fetches latest code
- Sets up Git environment

### 2. Set up Python
- Installs Python 3.11
- Caches pip dependencies

### 3. Install Dependencies
- Runs `pip install -r requirements.txt`
- Installs pytest, python-docx, google-genai, etc.

### 4. Verify Family Tree
- Checks `family_tree.json` exists
- Prints file size

### 5. Create Backups
- Copies data files to `.ci-backup` versions
- Safety net for data integrity

### 6. Run Integration Test
- Sets `CI_MODE=true`
- Runs pytest with verbose output
- Captures exit code

### 7. Restore Original Files
- Runs even if test fails (`if: always()`)
- Copies backups back to originals
- Verifies no `git diff` changes

### 8. Cleanup Test Artifacts
- Removes temp files
- Removes pytest cache
- Removes coverage data

### 9. Test Summary
- Prints pass/fail status
- Lists what was validated
- Marks workflow success/failure

## 🎓 Best Practices

### When to Run

- **Before Major Changes:** Validate system before big updates
- **After Bug Fixes:** Confirm fixes didn't break anything
- **Weekly (Automatic):** Regular health check
- **Before Releases:** Final validation

### What to Check

After a successful run:
1. ✅ All 7 tests passed
2. ✅ No changes to family_tree.json
3. ✅ No changes to contributors.json
4. ✅ No changes to README.md
5. ✅ Clean `git diff` output

### Integration with Development

This test is **separate from development workflows**:
- Doesn't run on every commit (too slow)
- Doesn't block PRs (runs independently)
- Provides confidence in system health
- Catches integration issues early

## 🔗 Related Files

- `test_integration_uber.py` - The actual test code
- `TEST_README.md` - Test documentation
- `requirements.txt` - Python dependencies
- `.github/workflows/integration-test.yml` - This workflow

## ❓ FAQ

**Q: Does this test affect my data?**
A: No. All data is backed up and restored. CI_MODE ensures no permanent changes.

**Q: Can I run this locally?**
A: Yes! See TEST_README.md for local run instructions.

**Q: How long does it take?**
A: ~5-10 minutes (includes RAG upload/indexing wait times)

**Q: What if the test fails?**
A: Data is still safe (restored from backups). Check logs to identify the issue.

**Q: Does it count toward contributor stats?**
A: No. CI_MODE disables all contributor tracking.

**Q: Can I customize the schedule?**
A: Yes. Edit the `cron` line in `integration-test.yml`

---

**Questions or Issues?** Check the test logs in GitHub Actions or refer to TEST_README.md.
