from typing import Any, Dict, List, Optional
import uuid

from apify_client import ApifyClient
from langchain_core.documents import Document
from langchain_community.utilities import ApifyWrapper
from pyramidpy_tools.settings import settings

from .schemas import (
    GoogleSearchResponse,
    WebScraperResponse,
)


class ApifyError(Exception):
    """Base exception for Apify API errors"""

    pass


class ApifyAPI:
    """Client for interacting with Apify API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.tool_provider.apify_api_key
        if not self.api_key:
            raise ApifyError(
                "Apify API key not found. Please set APIFY_API_KEY environment variable or pass it to the constructor."
            )

        self.client = ApifyClient(self.api_key)

   
    def web_loader(
        self,
        start_urls: list[str],
        collection: str | None = None,
        max_crawl_pages: int = 2,
    ) -> list[Document]:
        """Load the web for information relevant to the query."""
        apify = ApifyWrapper(
            apify_api_token=self.api_key
        )
        urls = [{"url": url} for url in start_urls]
        loader = apify.call_actor(
            actor_id="apify/website-content-crawler",
            run_input={"startUrls": urls, "maxCrawlPages": max_crawl_pages},
            dataset_mapping_function=lambda item: Document(
                page_content=item["text"] or "", metadata={"source": item["url"]}, id=item.get("id", str(uuid.uuid4()))
            ),
        )
        docs = loader.load()
        return docs
     

    async def web_scraper(
        self,
        urls: List[str],
        max_pages_per_domain: int = 1,
        page_function: Optional[str] = None,
        proxy_configuration: Optional[Dict[str, Any]] = None,
    ) -> WebScraperResponse:
        """
        Scrape web pages using Apify's web scraper

        Args:
            urls: List of URLs to scrape
            max_pages_per_domain: Maximum number of pages to scrape per domain
            page_function: Custom page function for scraping
            proxy_configuration: Proxy configuration for scraping

        Returns:
            WebScraperResponse containing scraped data
        """
        try:
            # Default page function to extract text content
            if not page_function:
                page_function = """
                async function pageFunction(context) {
                    const { page, request } = context;
                    return {
                        url: request.url,
                        title: await page.title(),
                        text: await page.evaluate(() => document.body.innerText),
                    };
                }
                """

            # Configure the run
            run_input = {
                "startUrls": [{"url": url} for url in urls],
                "maxPagesPerDomain": max_pages_per_domain,
                "pageFunction": page_function,
            }

            if proxy_configuration:
                run_input["proxyConfiguration"] = proxy_configuration

            # Run the web scraper actor
            run = await self.client.actor("apify/web-scraper").call(run_input=run_input)

            # Fetch and process the results
            items = []
            async for item in self.client.dataset(
                run["defaultDatasetId"]
            ).iterate_items():
                items.append(item)

            return WebScraperResponse(
                run_id=run["id"], status=run["status"], items=items
            )

        except Exception as e:
            raise ApifyError(f"Error running web scraper: {str(e)}")

    async def search_google(
        self,
        query: str,
        num_results: int = 10,
        language: str = "en",
        country: str = "US",
        max_age_days: Optional[int] = None,
    ) -> GoogleSearchResponse:
        """
        Search Google using Apify's Google Search Scraper

        Args:
            query: Search query
            num_results: Number of results to return (max 100)
            language: Language code for search results
            country: Country code for search results
            max_age_days: Maximum age of results in days

        Returns:
            GoogleSearchResponse containing search results
        """
        try:
            run_input = {
                "queries": [query],
                "maxPagesPerQuery": 1,
                "resultsPerPage": min(num_results, 100),  # Max 100 results per page
                "languageCode": language,
                "countryCode": country,
                "maxConcurrency": 1,
            }

            if max_age_days:
                run_input["maxAgeInDays"] = max_age_days

            # Run the Google Search actor
            run = await self.client.actor("apify/google-search-scraper").call(
                run_input=run_input
            )

            # Fetch and process the results
            items = []
            async for item in self.client.dataset(
                run["defaultDatasetId"]
            ).iterate_items():
                items.append(item)

            return GoogleSearchResponse(
                run_id=run["id"], status=run["status"], items=items
            )

        except Exception as e:
            raise ApifyError(f"Error running Google search: {str(e)}")
