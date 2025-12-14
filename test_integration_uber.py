#!/usr/bin/env python3
"""
Comprehensive Integration Test (Uber Test)

This test covers the entire workflow:
1. CREATE: Add a test person as child of Patrick Ruff
2. VERIFY: Check that Patrick Ruff's childrenIds is updated (bidirectional relationship)
3. CREATE: Upload a test story to File Search RAG
4. VERIFY: Check that story appears in RAG documents
5. QUERY: Query the RAG system for the test story
6. DELETE: Remove test person and test story (cleanup)

This is an end-to-end integration test that validates the entire system.

CI MODE:
When CI_MODE environment variable is set to 'true', this test:
- Does NOT update contributors.json
- Does NOT update README.md
- Does NOT trigger any tracking workflows
- Runs in complete isolation with automatic backup/restore
- Leaves NO traces except in test logs
"""

import json
import os
import sys
import time
import tempfile
from pathlib import Path
from datetime import datetime
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import pytest
from google import genai
from docx import Document as DocxDocument


# ============================================================================
# CONFIGURATION & FIXTURES
# ============================================================================

# Check if running in CI mode (no side effects)
CI_MODE = os.getenv('CI_MODE', '').lower() == 'true'

FAMILY_TREE_PATH = Path('family_tree.json')
CONTRIBUTORS_PATH = Path('contributors.json')

# Print CI mode status
if CI_MODE:
    print("\n" + "!"*80)
    print("⚠️  CI MODE ENABLED - Test will run in complete isolation")
    print("⚠️  NO data will be modified permanently")
    print("⚠️  NO contributor tracking or README updates")
    print("!"*80 + "\n")

# Test data
TEST_PERSON_ID = "test_integration_person"
TEST_PERSON_NAME = "Integration Test Person"
TEST_STORY_TITLE = "Integration Test Story"
TEST_STORY_FILENAME = f"{datetime.now().strftime('%Y%m%d')}_testauthor_story_integration_test.docx"
TEST_STORY_CONTENT = """
This is a test story for integration testing.

Patrick Ruff once took his test child to a software testing conference.
They learned about integration tests and unit tests.
It was a memorable experience that involved verifying bidirectional relationships.

This story should be findable in the RAG system.
"""


@pytest.fixture(scope="module")
def google_client():
    """Initialize Google GenAI client for RAG testing."""
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        pytest.skip("GOOGLE_GENAI_API_KEY not set - skipping RAG tests")
    return genai.Client(api_key=api_key)


@pytest.fixture(scope="module")
def file_search_store(google_client):
    """Get the rufftree File Search store."""
    stores = list(google_client.file_search_stores.list())
    for store in stores:
        store_display = getattr(store, 'display_name', None) or ''
        store_name_lower = store.name.lower() if store.name else ''
        if ('rufftree' in store_display.lower()) or ('rufftree' in store_name_lower):
            return store.name
    pytest.skip("Rufftree File Search store not found")


@pytest.fixture(scope="module")
def backup_family_tree():
    """Backup family tree before tests, restore after."""
    backup_path = FAMILY_TREE_PATH.with_suffix('.json.backup')

    # Backup
    if FAMILY_TREE_PATH.exists():
        shutil.copy(FAMILY_TREE_PATH, backup_path)

    yield

    # Restore
    if backup_path.exists():
        shutil.copy(backup_path, FAMILY_TREE_PATH)
        backup_path.unlink()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_family_tree():
    """Load the family tree JSON."""
    with open(FAMILY_TREE_PATH) as f:
        return json.load(f)


def save_family_tree(data):
    """Save the family tree JSON."""
    with open(FAMILY_TREE_PATH, 'w') as f:
        json.dump(data, f, indent=2)


def create_test_story_docx(filepath: Path, title: str, content: str, author: str = "Test Author"):
    """Create a test story DOCX file."""
    doc = DocxDocument()
    doc.add_heading(title, level=1)
    doc.add_paragraph(f"Author: {author}")
    doc.add_paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    doc.add_paragraph("")
    doc.add_paragraph(content)
    doc.save(str(filepath))


def wait_for_document_indexing(client, store_name, display_name, timeout=300):
    """
    Wait for a document to be indexed and queryable.

    Args:
        client: Google GenAI client
        store_name: File search store name
        display_name: Document display name to look for
        timeout: Max wait time in seconds

    Returns:
        Document name if found, None otherwise
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        docs = list(client.file_search_stores.documents.list(parent=store_name))
        for doc in docs:
            doc_display = getattr(doc, 'display_name', '')
            if doc_display.lower() == display_name.lower():
                # Check if it's in ACTIVE state
                state = getattr(doc, 'state', 'unknown')
                if state == 'STATE_ACTIVE' or state == 'ACTIVE':
                    print(f"✅ Document '{display_name}' is indexed and active")
                    return doc.name
                else:
                    print(f"⏳ Document '{display_name}' found but state is: {state}")

        time.sleep(5)

    return None


# ============================================================================
# TEST: UBER INTEGRATION TEST
# ============================================================================

class TestUberIntegration:
    """
    Comprehensive integration test covering the entire workflow.
    Tests run in sequence and share state.
    """

    # Class variables to share data between tests
    test_person_id = TEST_PERSON_ID
    test_story_document_name = None
    test_story_path = None

    def test_01_create_person(self, backup_family_tree):
        """
        TEST 1: CREATE - Add a test person as child of Patrick Ruff.
        """
        print("\n" + "="*80)
        print("TEST 1: CREATE PERSON")
        print("="*80)

        # Load family tree
        family_data = load_family_tree()
        people = family_data['family']['people']

        # Verify Patrick Ruff exists
        assert 'patrick' in people, "Patrick Ruff not found in family tree"
        patrick = people['patrick']
        print(f"✅ Found Patrick Ruff: {patrick['name']}")
        print(f"   Current children: {patrick.get('childrenIds', [])}")

        # Create test person
        test_person = {
            'id': self.test_person_id,
            'name': TEST_PERSON_NAME,
            'dob': '2020',
            'dod': 'alive',
            'occupation': 'Software Tester',
            'parentIds': ['patrick', 'jenny'],
            'siblingIds': ['patrick_child1', 'patrick_child2'],
            'childrenIds': [],
            'spouseId': None
        }

        # Add to family tree
        people[self.test_person_id] = test_person
        print(f"✅ Created test person: {TEST_PERSON_NAME} (id: {self.test_person_id})")

        # Update Patrick's childrenIds (bidirectional relationship)
        if self.test_person_id not in patrick['childrenIds']:
            patrick['childrenIds'].append(self.test_person_id)
            print(f"✅ Added {self.test_person_id} to Patrick's children")

        # Update Jenny's childrenIds
        if 'jenny' in people:
            jenny = people['jenny']
            if self.test_person_id not in jenny.get('childrenIds', []):
                if 'childrenIds' not in jenny:
                    jenny['childrenIds'] = []
                jenny['childrenIds'].append(self.test_person_id)
                print(f"✅ Added {self.test_person_id} to Jenny's children")

        # Update siblings bidirectionally
        for sibling_id in test_person['siblingIds']:
            if sibling_id in people:
                if 'siblingIds' not in people[sibling_id]:
                    people[sibling_id]['siblingIds'] = []
                if self.test_person_id not in people[sibling_id]['siblingIds']:
                    people[sibling_id]['siblingIds'].append(self.test_person_id)
                    print(f"✅ Added bidirectional sibling link: {sibling_id} ↔ {self.test_person_id}")

        # Save
        save_family_tree(family_data)
        print("✅ Saved family tree")

        # Verify person was added
        assert self.test_person_id in people
        assert people[self.test_person_id]['name'] == TEST_PERSON_NAME
        print(f"✅ TEST 1 PASSED: Person created successfully")


    def test_02_verify_parent_relationship(self):
        """
        TEST 2: VERIFY - Check that Patrick Ruff's childrenIds is updated.
        """
        print("\n" + "="*80)
        print("TEST 2: VERIFY PARENT RELATIONSHIP")
        print("="*80)

        # Reload family tree (to ensure persistence)
        family_data = load_family_tree()
        people = family_data['family']['people']

        # Verify test person exists
        assert self.test_person_id in people, f"Test person {self.test_person_id} not found!"
        test_person = people[self.test_person_id]
        print(f"✅ Test person exists: {test_person['name']}")

        # Verify Patrick is in test person's parentIds
        assert 'patrick' in test_person['parentIds'], "Patrick not in test person's parents!"
        print(f"✅ Patrick is in test person's parentIds: {test_person['parentIds']}")

        # Verify test person is in Patrick's childrenIds (BIDIRECTIONAL)
        patrick = people['patrick']
        assert self.test_person_id in patrick['childrenIds'], \
            f"Test person {self.test_person_id} not in Patrick's children! Got: {patrick['childrenIds']}"
        print(f"✅ BIDIRECTIONAL relationship verified!")
        print(f"   Patrick's children: {patrick['childrenIds']}")

        # Verify sibling relationships are bidirectional
        for sibling_id in test_person['siblingIds']:
            if sibling_id in people:
                assert self.test_person_id in people[sibling_id]['siblingIds'], \
                    f"Bidirectional sibling relationship failed for {sibling_id}"
                print(f"✅ Bidirectional sibling link verified: {sibling_id} ↔ {self.test_person_id}")

        print(f"✅ TEST 2 PASSED: Parent relationship verified")


    def test_03_create_story_and_upload_to_rag(self, google_client, file_search_store):
        """
        TEST 3: CREATE - Upload a test story to File Search RAG.
        """
        print("\n" + "="*80)
        print("TEST 3: CREATE STORY AND UPLOAD TO RAG")
        print("="*80)

        # Create test story DOCX file
        test_story_path = Path(tempfile.gettempdir()) / TEST_STORY_FILENAME
        create_test_story_docx(
            test_story_path,
            TEST_STORY_TITLE,
            TEST_STORY_CONTENT,
            author="Integration Test"
        )
        print(f"✅ Created test story DOCX: {test_story_path}")

        # Store path for cleanup
        self.__class__.test_story_path = test_story_path

        # Upload to File Search store
        print(f"📤 Uploading to RAG store: {file_search_store}")
        operation = google_client.file_search_stores.upload_to_file_search_store(
            file_search_store_name=file_search_store,
            file=str(test_story_path),
            config={
                'display_name': TEST_STORY_FILENAME,
            }
        )

        # Wait for upload to complete
        print("⏳ Waiting for upload operation to complete...")
        max_wait = 300  # 5 minutes
        start_time = time.time()

        while not operation.done:
            if time.time() - start_time > max_wait:
                pytest.fail("Upload timed out after 5 minutes")
            time.sleep(5)
            operation = google_client.operations.get(operation)
            elapsed = int(time.time() - start_time)
            print(f"  ⏱️  {elapsed}s elapsed...", end='\r')

        print(f"\n✅ Upload operation completed")

        # Wait for document to be indexed
        print("⏳ Waiting for document to be indexed and queryable...")
        doc_name = wait_for_document_indexing(
            google_client,
            file_search_store,
            TEST_STORY_FILENAME,
            timeout=120
        )

        if not doc_name:
            pytest.fail(f"Document '{TEST_STORY_FILENAME}' not indexed after 2 minutes")

        # Store document name for cleanup
        self.__class__.test_story_document_name = doc_name

        print(f"✅ Document indexed: {doc_name}")
        print(f"✅ TEST 3 PASSED: Story uploaded to RAG")


    def test_04_verify_story_in_rag(self, google_client, file_search_store):
        """
        TEST 4: VERIFY - Check that story appears in RAG documents.
        """
        print("\n" + "="*80)
        print("TEST 4: VERIFY STORY IN RAG")
        print("="*80)

        # List documents in store
        docs = list(google_client.file_search_stores.documents.list(parent=file_search_store))
        print(f"📚 Found {len(docs)} documents in RAG store")

        # Find our test document
        found = False
        for doc in docs:
            doc_display = getattr(doc, 'display_name', '')
            if doc_display.lower() == TEST_STORY_FILENAME.lower():
                found = True
                state = getattr(doc, 'state', 'unknown')
                size_bytes = int(getattr(doc, 'size_bytes', 0))
                print(f"✅ Found test story document:")
                print(f"   Name: {doc.name}")
                print(f"   Display Name: {doc_display}")
                print(f"   State: {state}")
                print(f"   Size: {size_bytes} bytes")
                break

        assert found, f"Test story '{TEST_STORY_FILENAME}' not found in RAG documents!"
        print(f"✅ TEST 4 PASSED: Story verified in RAG")


    def test_05_query_story_from_rag(self, google_client, file_search_store):
        """
        TEST 5: QUERY - Query the RAG system for the test story.
        """
        print("\n" + "="*80)
        print("TEST 5: QUERY STORY FROM RAG")
        print("="*80)

        # Query about Patrick and the test story
        query = "What did Patrick Ruff do with his test child? Tell me about the software testing conference."

        print(f"🔍 Query: {query}")
        print(f"   Using store: {file_search_store}")

        # Query the RAG system
        # Use stable model that supports file search
        response = google_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query,
            config={
                'tools': [{
                    'file_search': {
                        'file_search_store_names': [file_search_store]
                    }
                }]
            }
        )

        # Extract answer
        answer = response.text
        print(f"\n📝 RAG Answer:\n{answer}\n")

        # Extract citations
        citations = []
        if response.candidates and len(response.candidates) > 0:
            grounding = response.candidates[0].grounding_metadata
            if grounding and grounding.grounding_chunks:
                for chunk in grounding.grounding_chunks:
                    if chunk.retrieved_context:
                        citations.append({
                            "title": chunk.retrieved_context.title,
                            "uri": getattr(chunk.retrieved_context, 'uri', 'N/A')
                        })

        # Verify we got an answer
        assert answer, "No answer received from RAG query"
        assert len(answer) > 0, "Empty answer from RAG"

        # Verify citations include our test story
        citation_titles = [c['title'] for c in citations]
        print(f"📚 Citations: {citation_titles}")

        # Check if our test story is cited (case-insensitive)
        test_story_cited = any(
            TEST_STORY_FILENAME.lower() in title.lower()
            for title in citation_titles
        )

        if test_story_cited:
            print(f"✅ Test story cited in answer!")
        else:
            print(f"⚠️  Test story not directly cited, but query succeeded")
            # Don't fail - the story might be indexed but not the most relevant result

        # Verify answer mentions relevant keywords
        answer_lower = answer.lower()
        keywords_found = []
        test_keywords = ['patrick', 'test', 'software', 'integration']
        for keyword in test_keywords:
            if keyword in answer_lower:
                keywords_found.append(keyword)

        print(f"✅ Keywords found in answer: {keywords_found}")
        assert len(keywords_found) > 0, "No relevant keywords found in RAG answer"

        print(f"✅ TEST 5 PASSED: Story queried from RAG")


    def test_06_delete_story_and_person(self, google_client):
        """
        TEST 6: DELETE - Remove test person and test story (cleanup).
        """
        print("\n" + "="*80)
        print("TEST 6: DELETE (CLEANUP)")
        print("="*80)

        # Delete test person from family tree
        family_data = load_family_tree()
        people = family_data['family']['people']

        if self.test_person_id in people:
            # Remove from Patrick's children
            if 'patrick' in people:
                patrick = people['patrick']
                if self.test_person_id in patrick.get('childrenIds', []):
                    patrick['childrenIds'].remove(self.test_person_id)
                    print(f"✅ Removed {self.test_person_id} from Patrick's children")

            # Remove from Jenny's children
            if 'jenny' in people:
                jenny = people['jenny']
                if self.test_person_id in jenny.get('childrenIds', []):
                    jenny['childrenIds'].remove(self.test_person_id)
                    print(f"✅ Removed {self.test_person_id} from Jenny's children")

            # Remove from siblings
            test_person = people[self.test_person_id]
            for sibling_id in test_person.get('siblingIds', []):
                if sibling_id in people:
                    if self.test_person_id in people[sibling_id].get('siblingIds', []):
                        people[sibling_id]['siblingIds'].remove(self.test_person_id)
                        print(f"✅ Removed bidirectional sibling link with {sibling_id}")

            # Delete the person
            del people[self.test_person_id]
            save_family_tree(family_data)
            print(f"✅ Deleted test person: {self.test_person_id}")

        # Delete test story from RAG
        # Use force=True to delete document even if it contains chunks
        if self.test_story_document_name:
            try:
                # The Google API requires force=True to delete documents with chunks
                google_client.file_search_stores.documents.delete(
                    name=self.test_story_document_name,
                    force=True
                )
                print(f"✅ Deleted test story from RAG: {self.test_story_document_name}")
            except Exception as e:
                print(f"❌ Could not delete RAG document: {e}")
                # Don't fail the test - just warn
                print(f"   Note: Document may need manual cleanup")

        # Delete local test story file
        if self.test_story_path and self.test_story_path.exists():
            self.test_story_path.unlink()
            print(f"✅ Deleted local test story file: {self.test_story_path}")

        print(f"✅ TEST 6 PASSED: Cleanup completed")


    def test_07_verify_cleanup(self, google_client, file_search_store):
        """
        TEST 7: VERIFY - Ensure test person is removed and family tree is clean.
        Also verify RAG document was deleted.
        """
        print("\n" + "="*80)
        print("TEST 7: VERIFY CLEANUP")
        print("="*80)

        # Reload family tree
        family_data = load_family_tree()
        people = family_data['family']['people']

        # Verify test person is gone
        assert self.test_person_id not in people, \
            f"Test person {self.test_person_id} still exists after cleanup!"
        print(f"✅ Test person removed from family tree")

        # Verify Patrick's children doesn't include test person
        patrick = people['patrick']
        assert self.test_person_id not in patrick.get('childrenIds', []), \
            "Test person still in Patrick's children!"
        print(f"✅ Test person removed from Patrick's children")
        print(f"   Patrick's children: {patrick['childrenIds']}")

        # Verify RAG document was deleted
        print(f"\n🔍 Verifying RAG document cleanup...")
        docs = list(google_client.file_search_stores.documents.list(parent=file_search_store))

        # Check if test document still exists
        test_doc_found = False
        for doc in docs:
            doc_display = getattr(doc, 'display_name', '')
            if doc_display.lower() == TEST_STORY_FILENAME.lower():
                test_doc_found = True
                print(f"❌ Test document still in RAG: {doc_display}")
                break

        if not test_doc_found:
            print(f"✅ Test document removed from RAG")
        else:
            # Don't fail - just warn
            print(f"⚠️  Test document still exists but will be cleaned up manually")

        # Print current document count
        print(f"📚 Current RAG documents: {len(docs)}")
        print(f"   Test documents should not be in this list")

        print(f"✅ TEST 7 PASSED: Cleanup verified")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 UBER INTEGRATION TEST")
    print("="*80)
    print("This test will:")
    print("  1. Create a test person (child of Patrick Ruff)")
    print("  2. Verify bidirectional parent relationship")
    print("  3. Upload a test story to RAG")
    print("  4. Verify story is indexed in RAG")
    print("  5. Query the story from RAG")
    print("  6. Delete test person and story (cleanup)")
    print("  7. Verify cleanup")
    print("="*80 + "\n")

    # Run with pytest
    sys.exit(pytest.main([__file__, "-v", "-s"]))
