import uuid
from typing import List, Sequence

import vecs
from langchain.docstore.document import Document

from pyramidpy_tools.settings import settings
from pyramidpy_tools.utilities.embeddings import create_embeddings
from pyramidpy_tools.vector_store.dbs.base import BaseVectorStore


def get_table_name(uuid_str: str) -> str:
    """Generate a consistent table name from a UUID.
    Format: vs_{first_8_chars_of_uuid}
    """
    if not uuid_str:
        return "vs_default"
    # Take first 8 characters of the UUID to keep names short but unique
    short_id = str(uuid_str).replace("-", "")[:8]
    return f"vs_{short_id}"


def get_connection():
    return vecs.create_client(settings.storage.pg_vector_url)


def get_collection(name: str):
    return get_connection().get_or_create_collection(
        name=name, dimension=settings.embeddings.dimensions
    )


class PGVector(BaseVectorStore):
    """A wrapper for vecs PG Vector database."""

    collection_name: str = "docs"
    dimensions: int = settings.embeddings.dimensions
    provider: str = settings.embeddings.provider

    @property
    def collection(self):
        return get_collection(self.collection_name)

    def __init__(self, collection_name: str = "docs"):
        self.collection_name = collection_name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def add(
        self,
        documents: Sequence[Document],
    ) -> list[str]:
        records = []
        for doc in documents:
            embeddings = create_embeddings(
                self.provider, [doc.page_content], dimensions=self.dimensions
            )
            records.append(
                (
                    doc.id or str(uuid.uuid4()),
                    embeddings[0],
                    {"content": doc.page_content, **doc.metadata},
                )
            )

        self.collection.upsert(records=records)
        return [doc.id for doc in documents]

    def query(
        self,
        query_texts: List[str] | str,
        n_results: int = 10,
        where: dict = None,
        return_documents: bool = True,
        **kwargs,
    ) -> list[Document]:
        # Get embeddings for query
        query_embedding = create_embeddings(
            self.provider, query_texts, dimensions=self.dimensions
        )

        # Prepare filters if where clause exists
        filters = where if where else None

        # Query the collection
        results = self.collection.query(
            data=query_embedding,
            limit=n_results,
            filters=filters,
            include_metadata=True,
        )

        if not return_documents:
            return results

        # Convert results to Documents
        documents = []
        for r in results:
            documents.append(
                Document(page_content=r[1]["content"], metadata=r[1], id=r[0])
            )

        return documents

    def delete(self, ids: list[str] = None, where: dict = None):
        if ids:
            self.collection.delete(ids=ids)
        elif where:
            self.collection.delete(filters=where)

    def count(self) -> int:
        return len(self.collection.peek().ids)

    def reset_collection(self):
        conn = get_connection()
        try:
            conn.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection.create_index()

    def ok(self) -> bool:
        try:
            self.collection.peek()
            return True
        except Exception:
            return False

    def list_collections(self):
        return get_connection().list_collections()
