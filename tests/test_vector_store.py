import pytest
from pyramidpy_tools.vector_store.base import VectorStore
from langchain.docstore.document import Document
from pyramidpy_tools.settings import settings
import os


@pytest.fixture
def vector_store():
    # Override settings for testing
    settings.storage.postgres_url = os.getenv(
        "TEST_PG_VECTOR_URL", "postgresql://postgres:postgres@localhost:5432/test"
    )
    settings.openai_api_key = os.getenv("TEST_OPENAI_API_KEY", "test-key")
    store = VectorStore()  # Will use settings by default
    yield store
    # Cleanup
    for collection in store.list_collections():
        store.delete_collection(collection)


def test_add_and_query_documents(vector_store):
    # Test data
    docs = [
        Document(
            page_content="test document about machine learning",
            metadata={"type": "test"},
        ),
        Document(
            page_content="test document about data science", metadata={"type": "test"}
        ),
    ]

    # Add documents
    ids = vector_store.add_documents("test_collection", docs)
    assert len(ids) == 2

    # Query documents
    results = vector_store.query(
        "test_collection", query_text="machine learning", n_results=2
    )
    assert len(results) == 2
    assert any("machine learning" in r.page_content for r in results)


def test_delete_documents(vector_store):
    # Add test document
    doc = Document(page_content="test document", metadata={"type": "test"})
    ids = vector_store.add_documents("test_collection", [doc])

    # Delete document
    vector_store.delete("test_collection", ids=ids)

    # Verify deletion
    results = vector_store.query(
        "test_collection", query_text="test document", n_results=1
    )
    assert len(results) == 0


def test_list_collections(vector_store):
    # Add documents to two collections
    doc = Document(page_content="test document", metadata={"type": "test"})
    vector_store.add_documents("collection1", [doc])
    vector_store.add_documents("collection2", [doc])

    # List collections
    collections = vector_store.list_collections()
    assert "collection1" in collections
    assert "collection2" in collections


def test_delete_collection(vector_store):
    # Add documents to collection
    doc = Document(page_content="test document", metadata={"type": "test"})
    vector_store.add_documents("test_collection", [doc])

    # Delete collection
    vector_store.delete_collection("test_collection")

    # Verify deletion
    collections = vector_store.list_collections()
    assert "test_collection" not in collections
