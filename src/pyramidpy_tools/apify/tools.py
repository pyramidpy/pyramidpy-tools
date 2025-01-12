from typing import Any, Dict, List, Optional

from controlflow.flows.flow import get_flow
from controlflow.tools.tools import tool

from pyramidpy_tools.toolkit import Toolkit
from pyramidpy_tools.types import ApiKeyAuthConfig

from .base import ApifyAPI

AUTH_PREFIX = "apify_api_key"

def get_apify_api() -> ApifyAPI:
    """Get Apify API instance with token from context if available"""
    flow = get_flow()
    if flow and flow.context:
        api_key = flow.context.get('auth').get(AUTH_PREFIX)
        if api_key:
            return ApifyAPI(api_key=api_key)
    return ApifyAPI()


@tool(
    name="apify_web_scraper",
    description="Scrape web pages using Apify's web scraper",
    include_return_description=False,
)
async def apify_web_scraper(
    urls: List[str],
    max_pages_per_domain: int = 1,
    page_function: Optional[str] = None,
    proxy_configuration: Optional[Dict[str, Any]] = None,
):
    apify = get_apify_api()
    return await apify.web_scraper(
        urls=urls,
        max_pages_per_domain=max_pages_per_domain,
        page_function=page_function,
        proxy_configuration=proxy_configuration,
    )


@tool(
    name="apify_google_search",
    description="Search Google using Apify's Google Search Scraper",
    include_return_description=False,
)
async def apify_google_search(
    query: str,
    num_results: int = 10,
    language: str = "en",
    country: str = "US",
    max_age_days: Optional[int] = None,
):
    apify = get_apify_api()
    return await apify.search_google(
        query=query,
        num_results=num_results,
        language=language,
        country=country,
        max_age_days=max_age_days,
    )

@tool(
    name="apify_web_loader",
    description="Load LLM friendly web pages using Apify's web loader",
    include_return_description=False,
)
async def apify_web_loader(
    urls: List[str],
    max_crawl_pages: int = 2,
    collection: str | None = None,
):
    apify = get_apify_api()
    return await apify.web_loader(
        urls=urls,
        max_crawl_pages=max_crawl_pages,
        collection=collection,
    )

apify_toolkit = Toolkit.create_toolkit(
    id="apify_toolkit",
    tools=[
        apify_web_scraper,
        apify_google_search,
        apify_web_loader,
    ],
    auth_config_schema=ApiKeyAuthConfig,
    auth_key=AUTH_PREFIX,
    name="Apify Platform Toolkit",
    is_app_default=True,
    requires_config=False,
    description="Tools for web scraping and searching using Apify API",
)
