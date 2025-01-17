from typing import Optional, Sequence, List, Dict
from langchain.docstore.document import Document
import vecs
import uuid
from pydantic import BaseModel
from pyramidpy_tools.settings import settings
import openai
import asyncio


class VectorStoreConfig(BaseModel):
    pg_vector_url: str | None = None
    embedding_dimensions: int = 1536
    openai_api_key: str | None = None

    @classmethod
    def from_settings(cls) -> "VectorStoreConfig":
        """Create config from settings"""
        return cls(
            pg_vector_url=settings.storage.postgres_url,
            embedding_dimensions=1536,
            openai_api_key=settings.llm.openai_api_key,
        )


class VectorStore:
    """A wrapper for PG Vector database operations"""

    def __init__(self, config: Optional[VectorStoreConfig] = None):
        self.config = config or VectorStoreConfig.from_settings()
        if not self.config.pg_vector_url:
            raise ValueError(
                "pg_vector_url must be configured in settings or provided directly"
            )
        if not self.config.openai_api_key:
            raise ValueError(
                "openai_api_key must be configured in settings or provided directly"
            )

        self._client = vecs.create_client(self.config.pg_vector_url)
        openai.api_key = self.config.openai_api_key

    async def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for texts using OpenAI API"""
        response = await openai.embeddings.create(
            model="text-embedding-ada-002",
            input=texts,
            dimensions=self.config.embedding_dimensions,
        )
        return [item.embedding for item in response.data]

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Synchronous wrapper for getting embeddings"""
        return asyncio.run(self._get_embeddings(texts))

    def get_collection(self, name: str):
        """Get or create a collection"""
        return self._client.get_or_create_collection(
            name=name, dimension=self.config.embedding_dimensions
        )

    def add_documents(
        self, collection_name: str, documents: Sequence[Document]
    ) -> List[str]:
        """Add documents to a collection with automatic embeddings generation"""
        collection = self.get_collection(collection_name)
        records = []
        ids = []

        # Get embeddings for all documents
        texts = [doc.page_content for doc in documents]
        embeddings = self.get_embeddings(texts)

        for doc, embedding in zip(documents, embeddings):
            doc_id = doc.id or str(uuid.uuid4())
            ids.append(doc_id)
            # Use generated embeddings if not provided
            doc_embeddings = doc.metadata.get("embeddings", embedding)
            metadata = doc.metadata.copy()
            metadata.pop("embeddings", None)  # Remove embeddings from metadata

            records.append(
                (doc_id, doc_embeddings, {"content": doc.page_content, **metadata})
            )

        collection.upsert(records=records)
        return ids

    def query(
        self,
        collection_name: str,
        query_text: Optional[str] = None,
        query_embedding: Optional[List[float]] = None,
        n_results: int = 10,
        where: Dict = None,
    ) -> List[Document]:
        """Query documents by text or vector similarity"""
        collection = self.get_collection(collection_name)

        # Generate embedding from text if provided
        if query_text and not query_embedding:
            query_embedding = self.get_embeddings([query_text])[0]
        elif not query_embedding:
            raise ValueError("Either query_text or query_embedding must be provided")

        results = collection.query(
            data=query_embedding,
            limit=n_results,
            filters=where,
            include_metadata=True,
        )

        documents = []
        for r in results:
            documents.append(
                Document(page_content=r[1]["content"], metadata=r[1], id=r[0])
            )

        return documents

    def delete(self, collection_name: str, ids: List[str] = None, where: Dict = None):
        """Delete documents from collection"""
        collection = self.get_collection(collection_name)
        if ids:
            collection.delete(ids=ids)
        elif where:
            collection.delete(filters=where)

    def list_collections(self) -> List[str]:
        """List all collections"""
        return self._client.list_collections()

    def delete_collection(self, name: str):
        """Delete a collection"""
        try:
            self._client.delete_collection(name)
        except Exception:
            pass
