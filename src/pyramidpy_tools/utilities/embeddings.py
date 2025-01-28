from typing import List
from chromadb import Documents, EmbeddingFunction, Embeddings
from langchain_community.embeddings import OpenAIEmbeddings, FastEmbedEmbeddings

from pyramidpy_tools.settings import settings


def get_embeddings_client(provider: str, **kwargs):
    if provider == "openai":
        api_key = kwargs.get("api_key", settings.llm.openai_api_key)
        return OpenAIEmbeddings(openai_api_key=api_key)
    elif provider == "fastembed":
        return FastEmbedEmbeddings(**kwargs)
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")


def create_embeddings(provider: str, texts: List[str], **kwargs):
    embeddings = get_embeddings_client(provider, **kwargs)
    return embeddings.embed_documents(texts)


class OpenAIEmbeddingFunction(EmbeddingFunction):
    """
    Chroma Embedding Function
    """

    def __init__(self, dimensions: int = settings.embeddings.dimensions):
        self.dimensions = dimensions

    def __call__(self, input: Documents) -> Embeddings:
        return create_embeddings(input, dimensions=self.dimensions)
