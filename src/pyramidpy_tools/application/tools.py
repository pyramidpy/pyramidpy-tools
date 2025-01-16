from typing import Dict, List, Optional, Any
from controlflow.tools.tools import tool
from pyramidpy_tools.toolkit import Toolkit
from .base import ApplicationStorage, ApplicationConfig

@tool(
    name="create_application",
    description="Create a new application with schema definition"
)
def create_application(name: str, json_schema: Dict[str, Any], purpose: str, config: Dict):
    """Create a new application with schema
    
    Args:
        name: Application name
        json_schema: JSON schema for application data
        purpose: Purpose/description of the application
        config: Application configuration with pg_vector_url
    """
    storage = ApplicationStorage(ApplicationConfig(**config))
    app_id = storage.create_application(name, json_schema, purpose)
    return {"app_id": app_id, "message": f"Application {name} created successfully"}

@tool(
    name="get_application",
    description="Get application metadata"
)
def get_application(app_id: str, config: Dict):
    """Get application metadata
    
    Args:
        app_id: Application ID
        config: Application configuration
    """
    storage = ApplicationStorage(ApplicationConfig(**config))
    app = storage.get_application(app_id)
    if not app:
        return {"error": "Application not found"}
    return app.dict()

@tool(
    name="add_data",
    description="Add data to an application"
)
def add_data(app_id: str, data: Dict[str, Any], embeddings: List[float], config: Dict):
    """Add data to an application
    
    Args:
        app_id: Application ID
        data: Data to add (must match application schema)
        embeddings: Vector embeddings for the data
        config: Application configuration
    """
    storage = ApplicationStorage(ApplicationConfig(**config))
    doc_id = storage.add_data(app_id, data, embeddings)
    return {"doc_id": doc_id, "message": "Data added successfully"}

@tool(
    name="update_data",
    description="Update existing data in an application"
)
def update_data(app_id: str, doc_id: str, data: Dict[str, Any], embeddings: List[float], config: Dict):
    """Update existing data in an application
    
    Args:
        app_id: Application ID
        doc_id: Document ID to update
        data: Updated data (must match application schema)
        embeddings: Updated vector embeddings
        config: Application configuration
    """
    storage = ApplicationStorage(ApplicationConfig(**config))
    storage.update_data(app_id, doc_id, data, embeddings)
    return {"message": f"Document {doc_id} updated successfully"}

@tool(
    name="search_data",
    description="Search data in an application"
)
def search_data(
    app_id: str,
    query_embedding: Optional[List[float]] = None,
    filters: Optional[Dict] = None,
    limit: int = 10,
    config: Dict = None
):
    """Search data in an application
    
    Args:
        app_id: Application ID
        query_embedding: Optional vector embedding for similarity search
        filters: Optional filters to apply
        limit: Maximum number of results
        config: Application configuration
    """
    storage = ApplicationStorage(ApplicationConfig(**config))
    results = storage.search_data(app_id, query_embedding, filters, limit)
    return results

@tool(
    name="delete_data",
    description="Delete data from an application"
)
def delete_data(
    app_id: str,
    doc_ids: Optional[List[str]] = None,
    filters: Optional[Dict] = None,
    config: Dict = None
):
    """Delete data from an application
    
    Args:
        app_id: Application ID
        doc_ids: Optional list of document IDs to delete
        filters: Optional filters for deletion
        config: Application configuration
    """
    storage = ApplicationStorage(ApplicationConfig(**config))
    storage.delete_data(app_id, doc_ids, filters)
    return {"message": "Data deleted successfully"}

@tool(
    name="delete_application",
    description="Delete an application and all its data"
)
def delete_application(app_id: str, config: Dict):
    """Delete an application and all its data
    
    Args:
        app_id: Application ID
        config: Application configuration
    """
    storage = ApplicationStorage(ApplicationConfig(**config))
    storage.delete_application(app_id)
    return {"message": f"Application {app_id} deleted successfully"}

application_toolkit = Toolkit.create_toolkit(
    id="application_toolkit",
    tools=[
        create_application,
        get_application,
        add_data,
        update_data,
        search_data,
        delete_data,
        delete_application
    ],
    description="Tools for managing applications and their data",
    requires_config=True,
    name="Application Toolkit",
) 