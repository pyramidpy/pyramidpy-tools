import json
import pytest
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

from pyramidpy_tools.application.base import ApplicationStorage, ApplicationMetadata
from pyramidpy_tools.vector_store.dbs.chroma import Chroma
from pyramidpy_tools.vector_store.base import get_vectorstore
from pyramidpy_tools.settings import Settings, StorageSettings, EmbeddingSettings


@pytest.fixture
def mock_settings(monkeypatch):
    settings = Settings()
    settings.storage = StorageSettings(
        default_vector_store="chroma", chroma_url="test", chroma_client_type="base"
    )
    settings.embeddings = EmbeddingSettings(provider="fastembed", dimensions=384)
    monkeypatch.setattr("pyramidpy_tools.application.base.settings", settings)
    return settings


@pytest.fixture
def embeddings():
    return FastEmbedEmbeddings()


@pytest.fixture
def app_storage(monkeypatch, embeddings, mock_settings):
    # Override get_vectorstore to return our test chroma store
    stores = {}

    def mock_get_vectorstore(collection_name):
        if collection_name not in stores:
            store = Chroma()
            store.client_type = "base"
            store.collection_name = collection_name
            store.dimensions = mock_settings.embeddings.dimensions
            store.provider = mock_settings.embeddings.provider
            store.embeddings = embeddings
            try:
                store.client.delete_collection(collection_name)
            except:  # noqa: E722
                pass
            store.client.create_collection(collection_name)
            stores[collection_name] = store
        return stores[collection_name]

    monkeypatch.setattr(
        "pyramidpy_tools.application.base.get_vectorstore", mock_get_vectorstore
    )
    storage = ApplicationStorage(app_id="test-app-id")

    yield storage

    # Cleanup all collections after test
    for store in stores.values():
        try:
            store.client.delete_collection(store.collection_name)
        except:  # noqa: E722
            pass


def test_create_application(app_storage):
    name = "test-app"
    schema = {"type": "object"}
    purpose = "testing"

    app_id = app_storage.create_application(name, schema, purpose)

    # Verify the application was created
    assert isinstance(app_id, str)

    # Query to verify the data was stored correctly
    store = get_vectorstore("applications")
    results = store.query(
        query_texts=[""],  # Empty query as list
        where={"$and": [{"app_id": {"$eq": app_id}}, {"type": {"$eq": "application"}}]},
    )

    assert len(results) == 1
    doc = results[0]
    metadata = json.loads(doc.page_content)
    assert metadata["name"] == name
    assert metadata["schema"] == schema
    assert metadata["purpose"] == purpose
    assert isinstance(metadata["created_at"], str)
    assert isinstance(metadata["updated_at"], str)
    assert doc.metadata == {"type": "application", "app_id": app_id}


def test_get_application(app_storage):
    # First create an application
    name = "test-app"
    schema = {"type": "object"}
    purpose = "testing"
    app_id = app_storage.create_application(name, schema, purpose)

    # Now try to get it
    result = app_storage.get_application(app_id)

    assert isinstance(result, ApplicationMetadata)
    assert result.name == name
    assert result.purpose == purpose
    assert result.schema == schema


def test_get_application_not_found(app_storage):
    result = app_storage.get_application("non-existent")
    assert result is None


def test_add_data(app_storage):
    # First create an application
    app_id = app_storage.create_application("test-app", {"type": "object"}, "testing")

    # Add data to it
    data = {"field": "value"}
    doc_id = app_storage.add_data(app_id, data)

    # Verify the data was added
    assert isinstance(doc_id, str)
    store = get_vectorstore(f"app_{app_id}")
    results = store.query(
        query_texts=[""],  # Empty query as list
        where={"$and": [{"app_id": {"$eq": app_id}}, {"type": {"$eq": "data"}}]},
    )

    assert len(results) == 1
    doc = results[0]
    assert doc.id == doc_id
    assert json.loads(doc.page_content) == data
    assert doc.metadata == {"type": "data", "app_id": app_id}


def test_update_data(app_storage):
    # First create an application and add data
    app_id = app_storage.create_application("test-app", {"type": "object"}, "testing")
    data = {"field": "original"}
    doc_id = app_storage.add_data(app_id, data)

    # Update the data
    updated_data = {"field": "updated"}
    app_storage.update_data(app_id, doc_id, updated_data)

    # Verify the update
    store = get_vectorstore(f"app_{app_id}")
    results = store.query(
        query_texts=[""],  # Empty query as list
        where={"$and": [{"app_id": {"$eq": app_id}}, {"type": {"$eq": "data"}}]},
    )

    assert len(results) == 1
    doc = results[0]
    assert doc.id == doc_id
    assert json.loads(doc.page_content) == updated_data
    assert doc.metadata == {"type": "data", "app_id": app_id}


def test_search_data(app_storage):
    # Create application and add test data
    app_id = app_storage.create_application("test-app", {"type": "object"}, "testing")
    app_storage.add_data(app_id, {"content": "test document about machine learning"})
    app_storage.add_data(app_id, {"content": "test document about data science"})

    # Search the data
    results = app_storage.search_data(app_id, query_text="machine learning", limit=1)

    assert len(results) == 1
    assert "machine learning" in results[0]["content"]["content"]
    assert results[0]["metadata"]["type"] == "data"
    assert results[0]["metadata"]["app_id"] == app_id


def test_delete_data(app_storage):
    # Create application and add test data
    app_id = app_storage.create_application("test-app", {"type": "object"}, "testing")
    doc_id = app_storage.add_data(app_id, {"field": "value"})

    # Delete the data
    app_storage.delete_data(app_id, doc_ids=[doc_id])

    # Verify deletion
    store = get_vectorstore(f"app_{app_id}")
    results = store.query(
        query_texts=[""],  # Empty query as list
        where={"$and": [{"app_id": {"$eq": app_id}}, {"type": {"$eq": "data"}}]},
    )
    assert len(results) == 0


def test_delete_application(app_storage):
    # Create application and add some data
    app_id = app_storage.create_application("test-app", {"type": "object"}, "testing")
    app_storage.add_data(app_id, {"field": "value"})

    # Delete the application
    app_storage.delete_application(app_id)

    # Verify application metadata is deleted
    store = get_vectorstore("applications")
    results = store.query(
        query_texts=[""],  # Empty query as list
        where={"$and": [{"app_id": {"$eq": app_id}}]},
    )
    assert len(results) == 0

    # Verify application data is deleted
    data_store = get_vectorstore(f"app_{app_id}")
    results = data_store.query(
        query_texts=[""],  # Empty query as list
        where={"$and": [{"app_id": {"$eq": app_id}}]},
    )
    assert len(results) == 0
