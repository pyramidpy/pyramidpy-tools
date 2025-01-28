from unittest.mock import MagicMock, patch

import pytest
from langchain.docstore.document import Document
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

from pyramidpy_tools.vector_store.dbs.chroma import Chroma
from pyramidpy_tools.vector_store.dbs.pg_vector import PGVector


@pytest.fixture
def mock_vecs_client():
    with patch("vecs.create_client") as mock_create_client:
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        yield mock_client


@pytest.fixture
def embeddings():
    return FastEmbedEmbeddings()


@pytest.fixture
def pg_vector(mock_vecs_client):
    store = PGVector(collection_name="test_collection")
    store.provider = "fastembed"  # Override to use fastembed instead of OpenAI
    store.dimensions = 384  # FastEmbed dimensions
    yield store


@pytest.fixture
def chroma_vector():
    store = Chroma()
    store.client_type = "base"  # Use in-memory client
    store.collection_name = "test_collection1"
    store.dimensions = 384  # FastEmbed dimensions
    store.provider = "fastembed"  # Use FastEmbed
    # Reset collection before each test
    try:
        store.client.delete_collection(store.collection_name)
    except:  # noqa: E722
        pass
    yield store
    # Cleanup after test
    try:
        store.client.delete_collection(store.collection_name)
    except:  # noqa: E722
        pass


@pytest.fixture
def test_documents():
    return [
        Document(
            page_content="test document about machine learning",
            metadata={"type": "test"},
            id="doc1",
        ),
        Document(
            page_content="test document about data science",
            metadata={"type": "test"},
            id="doc2",
        ),
    ]


class TestPGVector:
    def test_add_and_query_documents(self, pg_vector, mock_vecs_client, test_documents):
        # Mock collection
        mock_collection = MagicMock()
        mock_vecs_client.get_or_create_collection.return_value = mock_collection
        mock_collection.upsert.return_value = ["doc1", "doc2"]

        # Mock query response
        mock_collection.query.return_value = [
            ("doc1", {"content": test_documents[0].page_content, "type": "test"}),
            ("doc2", {"content": test_documents[1].page_content, "type": "test"}),
        ]

        # Add documents - this will use real FastEmbed embeddings
        ids = pg_vector.add(test_documents)
        assert len(ids) == 2

        # Verify upsert was called correctly
        assert mock_collection.upsert.call_count == 1
        records = mock_collection.upsert.call_args[1]["records"]
        assert len(records) == 2
        for record in records:
            assert len(record) == 3
            assert isinstance(record[0], str)  # id
            assert isinstance(record[1], list)  # embeddings
            assert isinstance(record[2], dict)  # metadata
            assert "content" in record[2]
            assert "type" in record[2]

        # Query documents - this will use real FastEmbed embeddings
        results = pg_vector.query(query_texts=["machine learning"], n_results=2)
        assert len(results) == 2
        mock_collection.query.assert_called_once()

    def test_delete_documents(self, pg_vector, mock_vecs_client):
        mock_collection = MagicMock()
        mock_vecs_client.get_or_create_collection.return_value = mock_collection

        pg_vector.delete(ids=["doc1"])
        mock_collection.delete.assert_called_once_with(ids=["doc1"])

    def test_count(self, pg_vector, mock_vecs_client):
        mock_collection = MagicMock()
        mock_vecs_client.get_or_create_collection.return_value = mock_collection
        mock_collection.peek.return_value = MagicMock(ids=["doc1", "doc2"])

        count = pg_vector.count()
        assert count == 2


class TestChroma:
    def test_add_and_query_documents(self, chroma_vector, test_documents):
        # Add documents - this will use real FastEmbed embeddings

        ids = chroma_vector.add(test_documents)
        assert len(ids) == 2

        # Query documents - this will use real FastEmbed embeddings
        results = chroma_vector.query(query_texts=["machine learning"], n_results=1)
        assert len(results) == 1
        assert isinstance(results[0], Document)
        assert results[0].page_content == test_documents[0].page_content
        assert results[0].metadata["type"] == "test"
        assert "distance" in results[0].metadata

    def test_delete_documents(self, chroma_vector, test_documents):
        # Add documents first
        chroma_vector.add(test_documents)
        assert chroma_vector.count() == 2

        # Delete one document
        chroma_vector.delete(ids=["doc1"])
        assert chroma_vector.count() == 1

        # Query to verify deletion
        results = chroma_vector.query(
            query_texts=["machine learning"],
            n_results=2,
        )
        assert len(results) == 1
        assert results[0].id != "doc1"

    def test_count(self, chroma_vector, test_documents):
        assert chroma_vector.count() == 0
        chroma_vector.add(test_documents)
        assert chroma_vector.count() == 2
