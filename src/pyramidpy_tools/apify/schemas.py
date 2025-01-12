from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProxyConfiguration(BaseModel):
    proxy_urls: Optional[List[str]] = None
    groups: Optional[List[str]] = None
    country_code: Optional[str] = None


class ScrapedContent(BaseModel):
    url: str
    title: str
    text: str
    html: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class WebScraperResponse(BaseModel):
    run_id: str
    status: str
    items: List[ScrapedContent]


class WebScraperRequest(BaseModel):
    urls: List[str] = Field(..., description="List of URLs to scrape")
    max_pages_per_domain: int = Field(
        1, description="Maximum number of pages to scrape per domain"
    )
    page_function: Optional[str] = Field(
        None, description="Custom page function for scraping"
    )
    proxy_configuration: Optional[ProxyConfiguration] = Field(
        None, description="Proxy configuration for scraping"
    )


class GoogleSearchResult(BaseModel):
    title: str
    url: str
    description: str
    position: Optional[int] = None
    displayed_url: Optional[str] = None
    sitelinks: Optional[List[Dict[str, str]]] = None


class GoogleSearchResponse(BaseModel):
    run_id: str
    status: str
    items: List[GoogleSearchResult]


class GoogleSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    num_results: int = Field(10, description="Number of results to return (max 100)")
    language: str = Field("en", description="Language code for search results")
    country: str = Field("US", description="Country code for search results")
    max_age_days: Optional[int] = Field(
        None, description="Maximum age of results in days"
    )
