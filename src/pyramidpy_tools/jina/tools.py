from typing import List, Optional

from controlflow.flows.flow import get_flow
from controlflow.tools.tools import tool

from pyramidpy_tools.settings import settings
from pyramidpy_tools.toolkit import Toolkit

from .base import JinaAPI


def get_jina_api() -> JinaAPI:
    """Get Jina API instance with token from context if available"""
    flow = get_flow()
    if flow and flow.context:
        api_key = flow.context.get("auth", {}).get("jina_api_key")
        if api_key:
            return JinaAPI(api_key=api_key)
    return JinaAPI(api_key=settings.tool_provider.jina_api_key)


@tool(
    name="jina_search",
    description="Search the web using Jina's neural search engine",
    include_return_description=False,
)
async def jina_search(
    query: str,
    limit: int = 10,
    domain_filters: Optional[List[str]] = None,
    language: Optional[str] = None,
    safe_search: bool = True,
    page_token: Optional[str] = None,
):
    jina = get_jina_api()
    return await jina.search(
        query=query,
        limit=limit,
        domain_filters=domain_filters,
        language=language,
        safe_search=safe_search,
        page_token=page_token,
    )


@tool(
    name="jina_fetch_page",
    description="Fetch and extract content from a web page using Jina's content extractor",
    include_return_description=False,
)
async def jina_fetch_page(
    url: str, include_html: bool = False, timeout: Optional[int] = 30
):
    jina = get_jina_api()
    return await jina.fetch_page(url=url, include_html=include_html, timeout=timeout)


jina_toolkit = Toolkit.create_toolkit(
    id="jina_toolkit",
    tools=[jina_search, jina_fetch_page],
    name="Jina Toolkit",
    description="Tools for web search and content extraction using Jina's neural search engine",
    is_app_default=True,
    requires_config=False,
)
