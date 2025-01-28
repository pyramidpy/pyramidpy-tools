"""
Vector stores.
"""

from pyramidpy_tools.settings import settings
from pyramidpy_tools.vector_store.dbs.chroma import Chroma
from pyramidpy_tools.vector_store.dbs.pg_vector import PGVector


def get_vectorstore(collection: str = "docs"):
    if settings.storage.default_vector_store == "chroma":
        return Chroma(
            collection_name=collection, client_type=settings.storage.chroma_client_type
        )
    else:
        return PGVector(collection_name=collection)
