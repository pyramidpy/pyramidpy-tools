from abc import ABC, abstractmethod
from typing import Awaitable, Optional, Sequence, TypeVar

import anyio
from anyio import create_task_group
from langchain.docstore.document import Document

T = TypeVar("T")


async def run_concurrent_tasks(
    tasks: list[Awaitable[T]], max_concurrent: int = 5
) -> list[T]:
    """Run multiple tasks concurrently with a limit on concurrent execution.

    Args:
        tasks: List of awaitables to execute
        max_concurrent: Maximum number of tasks to run concurrently
    """
    semaphore = anyio.Semaphore(max_concurrent)
    results: list[T] = []

    async def _run_task(task: Awaitable[T]):
        async with semaphore:
            result = await task
            results.append(result)

    async with create_task_group() as tg:
        for task in tasks:
            tg.start_soon(_run_task, task)

    return results


class BaseVectorStore(ABC):
    """Abstract base class for vector stores."""

    collection_name: str = "raggy"
    dimensions: int = 1536  # Default OpenAI dimensions

    @abstractmethod
    def add(self, documents: Sequence[Document]) -> list[str]:
        """Add documents to the vector store."""
        pass

    @abstractmethod
    def query(
        self,
        query_texts: Optional[list[str]] = None,
        n_results: int = 10,
        where: dict = None,
        return_documents: bool = True,
        **kwargs,
    ) -> list[Document]:
        """Query documents from the vector store."""
        pass

    @abstractmethod
    def delete(self, ids: list[str] = None, where: dict = None):
        """Delete documents from the vector store."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Get the number of documents in the vector store."""
        pass

    @abstractmethod
    def reset_collection(self):
        """Reset/clear the collection."""
        pass

    @abstractmethod
    def ok(self) -> bool:
        """Check if the vector store is operational."""
        pass

    @abstractmethod
    def list_collections(self) -> list[str]:
        """List all collections in the vector store."""
        pass
