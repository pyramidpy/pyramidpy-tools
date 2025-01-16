from typing import List, Optional

from controlflow.flows.flow import get_flow
from controlflow.tools.tools import tool

from pyramidpy_tools.toolkit import Toolkit

from .base import TavilyAPI
from .schemas import TavilyAuthConfig


def get_tavily_api() -> TavilyAPI:
    """Get Tavily API instance with token from context if available"""
    flow = get_flow()
    if flow and flow.context:
        api_key = flow.context.get("auth", {}).get("tavily_api_key")
        if api_key:
            return TavilyAPI(api_key=api_key)
    return TavilyAPI()


@tool(
    name="tavily_search",
    description="Perform a web search using a fast web search(tavily)",
    include_return_description=False,
)
async def tavily_search(
    query: str,
):
    tavily = get_tavily_api()
    return await tavily.search(
        query=query,
    )


@tool(
    name="tavily_get_search_context",
    description="Get search context within token limit using Tavily API",
    include_return_description=False,
)
async def tavily_get_search_context(
    query: str,
    max_tokens: int = 4000,
    search_depth: str = "basic",
    topic: str = "general",
    max_results: int = 5,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    days: Optional[int] = None,
):
    tavily = get_tavily_api()
    return await tavily.get_search_context(
        query=query,
        max_tokens=max_tokens,
        search_depth=search_depth,
        topic=topic,
        max_results=max_results,
        include_domains=include_domains,
        exclude_domains=exclude_domains,
        days=days,
    )


@tool(
    name="tavily_qna_search",
    description="Perform a QnA search using",
    include_return_description=False,
)
async def tavily_qna_search(
    query: str,
    search_depth: str = "advanced",
    topic: str = "general",
    max_results: int = 5,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    days: Optional[int] = None,
):
    tavily = get_tavily_api()
    return await tavily.qna_search(
        query=query,
        search_depth=search_depth,
        topic=topic,
        max_results=max_results,
        include_domains=include_domains,
        exclude_domains=exclude_domains,
        days=days,
    )


tavily_toolkit = Toolkit.create_toolkit(
    id="tavily_toolkit",
    tools=[
        tavily_search,
        # tavily_get_search_context,
        # tavily_qna_search,
    ],
    auth_key="tavily_api_key",
    auth_config_schema=TavilyAuthConfig,
    requires_config=False,
    name="Search Toolkit(Tavily)",
    description="Tools for performing web searches using Tavily API",
    is_app_default=True,
)
