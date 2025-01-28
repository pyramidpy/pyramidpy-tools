from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
import json
from langchain.docstore.document import Document

from pyramidpy_tools.vector_store.base import get_vectorstore
from ..settings import settings


class ApplicationMetadata(BaseModel):
    name: str
    purpose: str
    schema: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    def model_dump(self) -> Dict[str, Any]:
        """Custom serialization that handles datetime objects"""
        data = super().model_dump()
        data["created_at"] = data["created_at"].isoformat()
        data["updated_at"] = data["updated_at"].isoformat()
        return data


class ApplicationStorage:
    """Storage for managing applications and their data"""

    app_id: str

    def __init__(self, app_id: str):
        self.app_id = app_id

    def _format_where_clause(self, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Format where clause based on vector store type"""
        if settings.storage.default_vector_store == "chroma":
            # For Chroma, we need at least 2 conditions in an $and clause
            # If we only have one condition, return it directly
            if len(conditions) == 1:
                key, value = next(iter(conditions.items()))
                return {key: {"$eq": value}}
            # Otherwise, format as $and with multiple conditions
            return {"$and": [{k: {"$eq": v}} for k, v in conditions.items()]}
        # PG Vector style
        return conditions

    def create_application(
        self, name: str, json_schema: Dict[str, Any], purpose: str
    ) -> str:
        """Create a new application with schema"""
        app_id = str(uuid.uuid4())
        metadata = ApplicationMetadata(
            name=name,
            purpose=purpose,
            schema=json_schema,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Store application metadata
        vector_store = get_vectorstore("applications")
        doc_id = str(uuid.uuid4())
        vector_store.add(
            [
                Document(
                    page_content=json.dumps(metadata.model_dump()),
                    metadata={"type": "application", "app_id": app_id},
                    id=doc_id,
                )
            ],
        )
        return app_id

    def get_application(self, app_id: str) -> Optional[ApplicationMetadata]:
        """Get application metadata"""
        vector_store = get_vectorstore("applications")
        where_clause = self._format_where_clause(
            {"app_id": app_id, "type": "application"}
        )
        results = vector_store.query(
            query_texts=[""],  # Empty query since we're using filters
            where=where_clause,
        )
        if not results:
            return None
        data = json.loads(results[0].page_content)
        return ApplicationMetadata(**data)

    def add_data(self, app_id: str, data: Dict[str, Any]) -> str:
        """Add data to application"""
        doc_id = str(uuid.uuid4())
        vector_store = get_vectorstore(f"app_{app_id}")
        vector_store.add(
            [
                Document(
                    page_content=json.dumps(data),
                    metadata={"type": "data", "app_id": app_id},
                    id=doc_id,
                )
            ],
        )
        return doc_id

    def update_data(self, app_id: str, doc_id: str, data: Dict[str, Any]):
        """Update existing data"""
        vector_store = get_vectorstore(f"app_{app_id}")
        vector_store.add(
            [
                Document(
                    page_content=json.dumps(data),
                    metadata={"type": "data", "app_id": app_id},
                    id=doc_id,
                )
            ],
        )

    def search_data(
        self,
        app_id: str,
        query_text: Optional[str] = None,
        filters: Dict = None,
        limit: int = 10,
    ) -> List[Dict]:
        """Search data using text similarity or filters"""
        vector_store = get_vectorstore(f"app_{app_id}")
        conditions = {"app_id": app_id, "type": "data"}
        if filters:
            conditions.update(filters)

        where_clause = self._format_where_clause(conditions)
        results = vector_store.query(
            query_texts=[query_text] if query_text else [""],
            n_results=limit,
            where=where_clause,
        )

        return [
            {
                "id": doc.id,
                "content": json.loads(doc.page_content)
                if isinstance(doc.page_content, str)
                else doc.page_content,
                "metadata": doc.metadata,
            }
            for doc in results
        ]

    def delete_data(self, app_id: str, doc_ids: List[str] = None, filters: Dict = None):
        """Delete data from application"""
        vector_store = get_vectorstore(f"app_{app_id}")
        where_clause = None
        if filters:
            conditions = {"app_id": app_id, "type": "data"}
            conditions.update(filters)
            where_clause = self._format_where_clause(conditions)
        vector_store.delete(ids=doc_ids, where=where_clause)

    def delete_application(self, app_id: str):
        """Delete an application and all its data"""
        # Delete application metadata
        vector_store = get_vectorstore("applications")
        where_clause = self._format_where_clause({"app_id": app_id})
        vector_store.delete(where=where_clause)

        # Delete application data
        data_store = get_vectorstore(f"app_{app_id}")
        where_clause = self._format_where_clause({"app_id": app_id})
        data_store.delete(where=where_clause)
