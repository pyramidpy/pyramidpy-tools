from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
import json
from langchain.docstore.document import Document
from pyramidpy_tools.vector_store.base import VectorStore, VectorStoreConfig
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


class ApplicationConfig(BaseModel):
    pg_vector_url: str | None = None
    openai_api_key: str | None = None
    embedding_dimensions: int = 1536

    @classmethod
    def from_settings(cls) -> "ApplicationConfig":
        """Create config from settings"""
        return cls(
            pg_vector_url=settings.storage.postgres_url,
            openai_api_key=settings.llm.openai_api_key,
            embedding_dimensions=1536,
        )


class ApplicationStorage:
    """Storage for managing applications and their data"""

    def __init__(self, config: Optional[ApplicationConfig] = None):
        self.config = config or ApplicationConfig.from_settings()
        if not self.config.pg_vector_url:
            raise ValueError(
                "pg_vector_url must be configured in settings or provided directly"
            )
        if not self.config.openai_api_key:
            raise ValueError(
                "openai_api_key must be configured in settings or provided directly"
            )

        self.vector_store = VectorStore(
            VectorStoreConfig(
                pg_vector_url=self.config.pg_vector_url,
                openai_api_key=self.config.openai_api_key,
                embedding_dimensions=self.config.embedding_dimensions,
            )
        )

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
        self.vector_store.add_documents(
            "applications",
            [
                Document(
                    page_content=json.dumps(metadata.model_dump()),
                    metadata={"type": "application", "app_id": app_id},
                )
            ],
        )
        return app_id

    def get_application(self, app_id: str) -> Optional[ApplicationMetadata]:
        """Get application metadata"""
        results = self.vector_store.query(
            "applications",
            query_text="",  # Empty query since we're using filters
            where={"app_id": app_id},
        )
        if not results:
            return None
        data = json.loads(results[0].page_content)
        return ApplicationMetadata(**data)

    def add_data(self, app_id: str, data: Dict[str, Any]) -> str:
        """Add data to application"""
        doc_id = str(uuid.uuid4())
        self.vector_store.add_documents(
            f"app_{app_id}",
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
        self.vector_store.add_documents(
            f"app_{app_id}",
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
        results = self.vector_store.query(
            f"app_{app_id}", query_text=query_text or "", n_results=limit, where=filters
        )

        return [
            {
                "id": doc.id,
                "content": json.loads(doc.page_content),
                "metadata": doc.metadata,
            }
            for doc in results
        ]

    def delete_data(self, app_id: str, doc_ids: List[str] = None, filters: Dict = None):
        """Delete data from application"""
        self.vector_store.delete(f"app_{app_id}", ids=doc_ids, where=filters)

    def delete_application(self, app_id: str):
        """Delete an application and all its data"""
        self.vector_store.delete_collection(f"app_{app_id}")
        self.vector_store.delete("applications", where={"app_id": app_id})
