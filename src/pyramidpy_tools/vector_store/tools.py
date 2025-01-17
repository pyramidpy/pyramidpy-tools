from typing import List, Dict, Optional
from controlflow.tools.tools import tool
from pyramidpy_tools.toolkit import Toolkit
from langchain.docstore.document import Document
from .base import VectorStore, VectorStoreConfig


@tool(name="add_documents", description="Add documents to a vector store collection")
def add_documents(collection_name: str, documents: List[Dict], config: Dict):
    """Add documents to a vector store collection

    Args:
        collection_name: Name of the collection
        documents: List of documents with {content, metadata, embeddings}
        config: Vector store configuration with pg_vector_url
    """
    store = VectorStore(VectorStoreConfig(**config))
    docs = [
        Document(
            page_content=doc["content"],
            metadata={"embeddings": doc["embeddings"], **doc.get("metadata", {})},
        )
        for doc in documents
    ]
    return store.add_documents(collection_name, docs)


@tool(name="query_documents", description="Query documents by vector similarity")
def query_documents(
    collection_name: str,
    query_embedding: List[float],
    n_results: int = 10,
    where: Optional[Dict] = None,
    config: Dict = None,
):
    """Query documents by vector similarity

    Args:
        collection_name: Name of the collection
        query_embedding: Query embedding vector
        n_results: Number of results to return
        where: Optional filters
        config: Vector store configuration
    """
    store = VectorStore(VectorStoreConfig(**config))
    docs = store.query(collection_name, query_embedding, n_results, where)
    return [
        {"id": doc.id, "content": doc.page_content, "metadata": doc.metadata}
        for doc in docs
    ]


@tool(name="delete_documents", description="Delete documents from a collection")
def delete_documents(
    collection_name: str,
    ids: Optional[List[str]] = None,
    where: Optional[Dict] = None,
    config: Dict = None,
):
    """Delete documents from a collection

    Args:
        collection_name: Name of the collection
        ids: Optional list of document IDs to delete
        where: Optional filters for deletion
        config: Vector store configuration
    """
    store = VectorStore(VectorStoreConfig(**config))
    store.delete(collection_name, ids, where)
    return "Documents deleted successfully"


@tool(name="list_collections", description="List all vector store collections")
def list_collections(config: Dict):
    """List all vector store collections

    Args:
        config: Vector store configuration
    """
    store = VectorStore(VectorStoreConfig(**config))
    return store.list_collections()


vector_store_toolkit = Toolkit.create_toolkit(
    id="vector_store_toolkit",
    tools=[add_documents, query_documents, delete_documents, list_collections],
    description="Tools for managing vector store collections and documents",
    requires_config=True,
    name="Vector Store Toolkit",
)
