import pytest
from pyramidpy_tools.application.base import ApplicationStorage
from pyramidpy_tools.settings import settings
import os
from datetime import datetime

@pytest.fixture
def app_storage():
    # Override settings for testing
    settings.storage.postgres_url = os.getenv(
        "TEST_PG_VECTOR_URL", 
        "postgresql://postgres:postgres@localhost:5432/test"
    )
    settings.openai_api_key = os.getenv("TEST_OPENAI_API_KEY", "test-key")
    storage = ApplicationStorage()  # Will use settings by default
    yield storage
    # Cleanup
    for collection in storage.vector_store.list_collections():
        storage.vector_store.delete_collection(collection)

def test_create_and_get_application(app_storage):
    # Test data
    name = "Test App"
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "completed": {"type": "boolean"}
        }
    }
    purpose = "Test application for unit tests"
    
    # Create application
    app_id = app_storage.create_application(name, schema, purpose)
    assert app_id is not None
    
    # Get application
    app = app_storage.get_application(app_id)
    assert app is not None
    assert app.name == name
    assert app.schema == schema
    assert app.purpose == purpose
    assert isinstance(app.created_at, datetime)
    assert isinstance(app.updated_at, datetime)

def test_add_and_search_data(app_storage):
    # Create test application
    app_id = app_storage.create_application(
        "Test App",
        {"type": "object"},
        "Test purpose"
    )
    
    # Test data
    data = {"title": "Buy groceries", "completed": False}
    
    # Add data
    doc_id = app_storage.add_data(app_id, data)
    assert doc_id is not None
    
    # Search data by text
    results = app_storage.search_data(
        app_id,
        query_text="groceries",
        limit=1
    )
    assert len(results) == 1
    assert results[0]["content"] == data

def test_update_data(app_storage):
    # Create test application and add data
    app_id = app_storage.create_application(
        "Test App",
        {"type": "object"},
        "Test purpose"
    )
    data = {"title": "Buy groceries", "completed": False}
    doc_id = app_storage.add_data(app_id, data)
    
    # Update data
    updated_data = {"title": "Buy groceries", "completed": True}
    app_storage.update_data(app_id, doc_id, updated_data)
    
    # Verify update
    results = app_storage.search_data(
        app_id,
        filters={"id": doc_id}
    )
    assert len(results) == 1
    assert results[0]["content"] == updated_data

def test_delete_data(app_storage):
    # Create test application and add data
    app_id = app_storage.create_application(
        "Test App",
        {"type": "object"},
        "Test purpose"
    )
    data = {"title": "Buy groceries", "completed": False}
    doc_id = app_storage.add_data(app_id, data)
    
    # Delete data
    app_storage.delete_data(app_id, doc_ids=[doc_id])
    
    # Verify deletion
    results = app_storage.search_data(app_id, filters={"id": doc_id})
    assert len(results) == 0

def test_delete_application(app_storage):
    # Create test application
    app_id = app_storage.create_application(
        "Test App",
        {"type": "object"},
        "Test purpose"
    )
    
    # Add some data
    data = {"title": "Buy groceries", "completed": False}
    app_storage.add_data(app_id, data)
    
    # Delete application
    app_storage.delete_application(app_id)
    
    # Verify application deletion
    app = app_storage.get_application(app_id)
    assert app is None
    
    # Verify data collection deletion
    collections = app_storage.vector_store.list_collections()
    assert f"app_{app_id}" not in collections 