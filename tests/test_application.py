import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from langchain.docstore.document import Document

from pyramidpy_tools.application.base import (
    ApplicationStorage,
    ApplicationConfig,
    ApplicationMetadata,
)
from pyramidpy_tools.vector_store.base import VectorStore


@pytest.fixture
def mock_vector_store():
    with patch("pyramidpy_tools.application.base.VectorStore") as mock_store:
        mock_instance = MagicMock(spec=VectorStore)
        mock_store.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def app_config():
    return ApplicationConfig(
        pg_vector_url="postgresql://test:test@localhost:5432/test",
        openai_api_key="test-key",
        embedding_dimensions=1536,
    )


@pytest.fixture
def app_storage(app_config, mock_vector_store):
    return ApplicationStorage(config=app_config)


def test_application_config_from_settings():
    with patch("pyramidpy_tools.application.base.settings") as mock_settings:
        mock_settings.storage.postgres_url = "test-pg-url"
        mock_settings.llm.openai_api_key = "test-openai-key"

        config = ApplicationConfig.from_settings()

        assert config.pg_vector_url == "test-pg-url"
        assert config.openai_api_key == "test-openai-key"
        assert config.embedding_dimensions == 1536


def test_application_storage_init_missing_config():
    with pytest.raises(ValueError, match="pg_vector_url must be configured"):
        ApplicationStorage(ApplicationConfig(openai_api_key="test"))

    with pytest.raises(ValueError, match="openai_api_key must be configured"):
        ApplicationStorage(ApplicationConfig(pg_vector_url="test"))


def test_create_application(app_storage, mock_vector_store):
    name = "test-app"
    schema = {"type": "object"}
    purpose = "testing"

    app_id = app_storage.create_application(name, schema, purpose)

    assert isinstance(app_id, str)
    mock_vector_store.add_documents.assert_called_once()
    call_args = mock_vector_store.add_documents.call_args
    assert call_args[0][0] == "applications"

    doc = call_args[0][1][0]
    assert isinstance(doc, Document)
    metadata = json.loads(doc.page_content)
    assert metadata["name"] == name
    assert metadata["schema"] == schema
    assert metadata["purpose"] == purpose
    assert isinstance(metadata["created_at"], str)
    assert isinstance(metadata["updated_at"], str)


def test_get_application(app_storage, mock_vector_store):
    app_id = "test-id"
    app_data = {
        "name": "test-app",
        "purpose": "testing",
        "schema": {"type": "object"},
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    mock_vector_store.query.return_value = [Document(page_content=json.dumps(app_data))]

    result = app_storage.get_application(app_id)

    assert isinstance(result, ApplicationMetadata)
    assert result.name == app_data["name"]
    assert result.purpose == app_data["purpose"]
    assert result.schema == app_data["schema"]
    mock_vector_store.query.assert_called_with(
        "applications", query_text="", where={"app_id": app_id}
    )


def test_get_application_not_found(app_storage, mock_vector_store):
    mock_vector_store.query.return_value = []

    result = app_storage.get_application("non-existent")

    assert result is None


def test_add_data(app_storage, mock_vector_store):
    app_id = "test-id"
    data = {"field": "value"}

    doc_id = app_storage.add_data(app_id, data)

    assert isinstance(doc_id, str)
    mock_vector_store.add_documents.assert_called_once()
    call_args = mock_vector_store.add_documents.call_args
    assert call_args[0][0] == f"app_{app_id}"

    doc = call_args[0][1][0]
    assert isinstance(doc, Document)
    assert doc.id == doc_id
    assert json.loads(doc.page_content) == data
    assert doc.metadata == {"type": "data", "app_id": app_id}


def test_update_data(app_storage, mock_vector_store):
    app_id = "test-id"
    doc_id = "doc-id"
    data = {"field": "updated"}

    app_storage.update_data(app_id, doc_id, data)

    mock_vector_store.add_documents.assert_called_once()
    call_args = mock_vector_store.add_documents.call_args
    assert call_args[0][0] == f"app_{app_id}"

    doc = call_args[0][1][0]
    assert doc.id == doc_id
    assert json.loads(doc.page_content) == data
    assert doc.metadata == {"type": "data", "app_id": app_id}


def test_search_data(app_storage, mock_vector_store):
    app_id = "test-id"
    query = "test query"
    filters = {"field": "value"}
    mock_results = [
        Document(
            page_content=json.dumps({"data": "1"}), metadata={"type": "data"}, id="doc1"
        ),
        Document(
            page_content=json.dumps({"data": "2"}), metadata={"type": "data"}, id="doc2"
        ),
    ]
    mock_vector_store.query.return_value = mock_results

    results = app_storage.search_data(app_id, query, filters, limit=2)

    assert len(results) == 2
    mock_vector_store.query.assert_called_with(
        f"app_{app_id}", query_text=query, n_results=2, where=filters
    )

    for i, result in enumerate(results, 1):
        assert result["content"] == {"data": str(i)}
        assert result["metadata"] == {"type": "data"}
        assert result["id"] == f"doc{i}"


def test_delete_data(app_storage, mock_vector_store):
    app_id = "test-id"
    doc_ids = ["doc1", "doc2"]
    filters = {"field": "value"}

    app_storage.delete_data(app_id, doc_ids, filters)

    mock_vector_store.delete.assert_called_with(
        f"app_{app_id}", ids=doc_ids, where=filters
    )


def test_delete_application(app_storage, mock_vector_store):
    app_id = "test-id"

    app_storage.delete_application(app_id)

    mock_vector_store.delete_collection.assert_called_with(f"app_{app_id}")
    mock_vector_store.delete.assert_called_with(
        "applications", where={"app_id": app_id}
    )
