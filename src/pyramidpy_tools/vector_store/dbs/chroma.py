from typing import Sequence

from chromadb import Client, HttpClient, Include
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from chromadb.api.models.Collection import Document as ChromaDocument
from chromadb.api.types import Embedding, OneOrMany, PyEmbedding, QueryResult
from chromadb.utils.batch_utils import create_batches
from langchain_core.documents import Document
from pyramidpy_tools.vector_store.dbs.base import BaseVectorStore
from pyramidpy_tools.settings import ChromaClientType, settings
from pyramidpy_tools.utilities.embeddings import (
    create_embeddings,
    OpenAIEmbeddingFunction,
)


def get_client(client_type: ChromaClientType) -> ClientAPI:
    if client_type == "base":
        return Client()
    elif client_type == "http":
        if not settings.storage.chroma_url:
            raise ValueError("Chroma URL is not set")
        if not settings.storage.chroma_server_authn_credentials:
            raise ValueError("Chroma API key is not set")
        return HttpClient(
            host=settings.storage.chroma_url,
            port=80,
            ssl=True,
            headers={
                "Authorization": f"Bearer {settings.storage.chroma_server_authn_credentials.get_secret_value()}"
            },
        )
    else:
        raise ValueError(f"Unknown client type: {client_type}")


class Chroma(BaseVectorStore):
    """A wrapper for chromadb.Client."""

    client_type: ChromaClientType = settings.storage.chroma_client_type
    collection_name: str = "docs"
    dimensions: int = settings.embeddings.dimensions
    provider: str = settings.embeddings.provider

    @property
    def client(self) -> ClientAPI:
        return get_client(self.client_type)

    @property
    def collection(self) -> Collection:
        return get_client(self.client_type).get_or_create_collection(
            name=self.collection_name,
            embedding_function=OpenAIEmbeddingFunction(dimensions=self.dimensions),
        )

    def _map_results_to_documents(self, results: QueryResult) -> list[Document]:
        """Map the results to documents.
        The results are returned in a format that is not directly usable as LangChain documents.
        """
        # check if results has embeddings
        documents = []
        if results.get("distances"):
            for idx, (docs, ids, distances, metadatas) in enumerate(
                zip(
                    results.get("documents"),
                    results.get("ids"),
                    results.get("distances"),
                    results.get("metadatas"),
                )
            ):
                metadata = metadatas[idx]
                metadata.update({"distance": distances[idx]})

                documents.append(
                    Document(page_content=docs[idx], id=ids[idx], metadata=metadata)
                )
        else:
            for idx, (docs, ids, metadatas) in enumerate(
                zip(
                    results.get("documents"),
                    results.get("ids"),
                    results.get("metadatas"),
                )
            ):
                documents.append(
                    Document(page_content=docs, id=ids, metadata=metadatas)
                )
        return documents

    def delete(
        self,
        ids: list[str] | None = None,
        where: dict | None = None,
        where_document: ChromaDocument | None = None,
    ):
        self.collection.delete(
            ids=ids,
            where=where,
            where_document=where_document,  # type: ignore
        )

    def add(self, documents: Sequence[Document]) -> list[str]:
        ids = [doc.id for doc in documents]
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        embeddings = create_embeddings(self.provider, texts, dimensions=self.dimensions)

        data = {
            "ids": ids,
            "documents": texts,
            "metadatas": metadatas,
            "embeddings": embeddings,
        }

        batched_data: list[tuple] = create_batches(
            get_client(self.client_type),
            **data,
        )

        for batch in batched_data:
            self.collection.add(*batch)

        get_result = self.collection.get(ids=ids)
        return get_result.get("documents") or []

    def query(
        self,
        query_embeddings: OneOrMany[Embedding] | OneOrMany[PyEmbedding] | None = None,
        query_texts: list[str] | None = None,
        n_results: int = 10,
        where: dict | None = None,
        where_document: dict | None = None,
        include: Include = ["metadatas", "documents", "distances"],  # type: ignore
        return_documents: bool = True,
        **kwargs,
    ) -> QueryResult:
        results = self.collection.query(
            query_embeddings=(
                create_embeddings(
                    self.provider, query_texts, dimensions=self.dimensions
                )
                if query_texts and not query_embeddings
                else query_embeddings
            ),
            query_texts=query_texts,
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=include,
            **kwargs,
        )
        documents = self._map_results_to_documents(results)
        if return_documents:
            return documents

        return "\n".join(
            [
                f"{doc.page_content} (distance: {doc.metadata.get('distance')})\n"
                for doc in documents
            ]
        )

    def count(self) -> int:
        return self.collection.count()

    def reset_collection(self):
        client = get_client(self.client_type)
        try:
            client.delete_collection(self.collection_name)
        except Exception:
            self.logger.warning_kv(
                "Collection not found",
                f"Creating a new collection {self.collection_name!r}",
            )
        client.create_collection(self.collection_name)

    def list_collections(self) -> list[str]:
        return self.client.list_collections()

    def ok(self) -> bool:
        try:
            version = get_client(self.client_type).get_version()
            self.logger.debug_kv("OK", f"Connected to Chroma {version!r}")
            return True
        except Exception as e:
            self.logger.error_kv("Connection error", f"Cannot connect to Chroma: {e}")
            return False
