"""
Knowledge base tools for RAG
"""

from controlflow.tools.tools import tool
from langchain_core.documents import Document

from pyramidpy_tools.toolkit import Toolkit

from .base import get_vectorstore


@tool(
    name="search_knowledge_base",
    description="Search the knowledge base for information relevant to the query.",
)
async def search_knowledge_base(
    query: str, collection: str = "adam_docs"
) -> list[Document]:
    """Search documentation for information relevant to the query."""
    try:
        store = get_vectorstore(collection)
        docs = store.query(query_texts=[query], n_results=10, return_documents=True)
        return docs
    except Exception as e:
        return f"Error querying knowledge base: {e}. Report this to the admin."


@tool(
    name="add_to_knowledge_base",
    description="Add text to the knowledge base.",
)
def add_to_knowledge_base(text: str, collection: str = "adam_docs"):
    """Add text to the knowledge base."""
    store = get_vectorstore(collection)
    store.upsert([Document(page_content=text)])
    return "Text added to the knowledge base."


@tool(
    name="list_collections",
    description="List all collections in the knowledge base",
)
def list_collections():
    store = get_vectorstore("raggy")  # collection name doesn't matter for listing
    data = store.list_collections()
    return data


knowledge_base_toolkit = Toolkit.create_toolkit(
    id="knowledge_base_toolkit",
    name="knowledge base",
    is_app_default=True,
    requires_config=False,
    description="Tools for searching and adding to the knowledge base",
    tools=[list_collections, search_knowledge_base, add_to_knowledge_base],
)
