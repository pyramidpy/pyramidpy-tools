from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class JinaSearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    score: float
    domain: str
    timestamp: Optional[str] = None
    language: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class JinaSearchResponse(BaseModel):
    results: List[JinaSearchResult]
    total: int
    took_ms: float
    next_page_token: Optional[str] = None


class JinaSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(10, description="Number of results to return (max 50)")
    domain_filters: Optional[List[str]] = Field(
        None, description="List of domains to filter results by"
    )
    language: Optional[str] = Field(
        None, description="Language code for search results"
    )
    safe_search: bool = Field(
        True, description="Whether to enable safe search filtering"
    )
    page_token: Optional[str] = Field(None, description="Token for paginated results")


class FetchPageRequest(BaseModel):
    url: str = Field(..., description="URL of the page to fetch")
    include_html: bool = Field(
        False, description="Whether to include raw HTML in response"
    )
    timeout: Optional[int] = Field(30, description="Timeout in seconds")


class FetchPageResponse(BaseModel):
    url: str
    title: str
    text: str
    html: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
