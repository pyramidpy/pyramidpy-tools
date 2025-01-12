"""
Base functionality for knowledge base operations
"""

import re

from langchain_core.documents import Document

from pyramidpy_tools.settings import settings
from app.vectorstores.chroma import Chroma
from app.vectorstores.pg_vector import PGVector


def get_vectorstore(collection: str):
    if settings.storage.default_vector_store == "chroma":
        return Chroma(
            collection_name=collection, client_type=settings.storage.chroma_client_type
        )
    else:
        return PGVector(collection_name=collection)


def convert_md_links_to_slack(text) -> str:
    md_link_pattern = r"\[(?P<text>[^\]]+)]\((?P<url>[^\)]+)\)"

    def to_slack_link(match):
        return f'<{match.group("url")}|{match.group("text")}>'

    return re.sub(
        r"\*\*(.*?)\*\*", r"*\1*", re.sub(md_link_pattern, to_slack_link, text)
    )
