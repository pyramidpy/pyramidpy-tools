import pytest
from unittest.mock import MagicMock, patch
from pyramidpy_tools.vector_store.base import VectorStore, VectorStoreConfig
from langchain.docstore.document import Document


@pytest.fixture
def mock_vecs_client():
    with patch("vecs.create_client") as mock_create_client:
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        yield mock_client


@pytest.fixture
def vector_store(mock_vecs_client):
    # Create a test config that doesn't require real credentials
    config = VectorStoreConfig(
        pg_vector_url="postgresql://postgres:postgres@localhost:5432/test",
        use_openai=False,  # Use FastEmbed
        max_parallel_embeddings=5,
    )
    store = VectorStore(config=config)
    yield store


def test_add_and_query_documents(vector_store, mock_vecs_client):
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

    # Mock collection
    mock_collection = MagicMock()
    mock_vecs_client.get_or_create_collection.return_value = mock_collection
    mock_collection.upsert.return_value = ["id1", "id2"]

    # Mock query response in the correct format
    mock_collection.query.return_value = [
        ("id1", {"content": docs[0].page_content, "type": "test"}),
        ("id2", {"content": docs[1].page_content, "type": "test"}),
    ]

    # Add documents - this will use real FastEmbed embeddings
    ids = vector_store.add_documents("test_collection", docs)
    assert len(ids) == 2

    # Verify upsert was called with the right number of records
    assert mock_collection.upsert.call_count == 1
    records = mock_collection.upsert.call_args[1]["records"]
    assert len(records) == 2
    # Each record should be a tuple of (id, embeddings, metadata)
    for record in records:
        assert len(record) == 3
        assert isinstance(record[0], str)  # id
        assert isinstance(record[1], list)  # embeddings
        assert isinstance(record[2], dict)  # metadata
        assert "content" in record[2]
        assert "type" in record[2]

    # Query documents - this will use real FastEmbed embeddings
    results = vector_store.query(
        "test_collection", query_text="machine learning", n_results=2
    )
    assert len(results) == 2
    mock_collection.query.assert_called_once()
    # Verify query was called with embeddings
    query_args = mock_collection.query.call_args[1]
    assert "data" in query_args
    assert isinstance(query_args["data"], list)
    assert len(query_args["data"]) > 0


def test_delete_documents(vector_store, mock_vecs_client):
    # Mock collection
    mock_collection = MagicMock()
    mock_vecs_client.get_or_create_collection.return_value = mock_collection
    mock_collection.delete.return_value = True

    # Delete document
    vector_store.delete("test_collection", ids=["id1"])
    mock_collection.delete.assert_called_once_with(ids=["id1"])


def test_list_collections(vector_store, mock_vecs_client):
    # Mock collections
    mock_vecs_client.list_collections.return_value = ["collection1", "collection2"]

    # List collections
    collections = vector_store.list_collections()
    assert "collection1" in collections
    assert "collection2" in collections
    mock_vecs_client.list_collections.assert_called_once()


def test_delete_collection(vector_store, mock_vecs_client):
    # Mock delete collection
    mock_vecs_client.delete_collection.return_value = True

    # Delete collection
    vector_store.delete_collection("test_collection")
    mock_vecs_client.delete_collection.assert_called_once_with("test_collection")
