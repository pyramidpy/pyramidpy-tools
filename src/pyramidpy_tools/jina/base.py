import os
from typing import Any, Dict, List, Optional

import httpx

from .schemas import (
    FetchPageRequest,
    FetchPageResponse,
    JinaSearchRequest,
    JinaSearchResponse,
    JinaSearchResult,
)


class JinaError(Exception):
    """Base exception for Jina API errors"""

    pass


class JinaAPI:
    """Client for interacting with Jina API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("JINA_API_KEY")
        if not self.api_key:
            raise JinaError(
                "Jina API key not found. Please set JINA_API_KEY environment variable or pass it to the constructor."
            )

        self.base_url = "https://api.jina.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to Jina API"""
        url = f"{self.base_url}/{endpoint}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=self.headers,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise JinaError(f"HTTP error occurred: {str(e)}")
            except Exception as e:
                raise JinaError(f"Error occurred: {str(e)}")

    async def search(
        self,
        query: str,
        limit: int = 10,
        domain_filters: Optional[List[str]] = None,
        language: Optional[str] = None,
        safe_search: bool = True,
        page_token: Optional[str] = None,
    ) -> JinaSearchResponse:
        """
        Search the web using Jina API

        Args:
            query: Search query
            limit: Number of results to return (max 50)
            domain_filters: List of domains to filter results by
            language: Language code for search results
            safe_search: Whether to enable safe search filtering
            page_token: Token for paginated results

        Returns:
            JinaSearchResponse containing search results
        """
        request = JinaSearchRequest(
            query=query,
            limit=min(limit, 50),  # Enforce max limit of 50
            domain_filters=domain_filters,
            language=language,
            safe_search=safe_search,
            page_token=page_token,
        )

        response = await self._make_request(
            method="POST", endpoint="search", json_data=request.dict(exclude_none=True)
        )

        # Transform raw results into JinaSearchResult objects
        results = [JinaSearchResult(**result) for result in response.get("results", [])]

        return JinaSearchResponse(
            results=results,
            total=response.get("total", 0),
            took_ms=response.get("took_ms", 0.0),
            next_page_token=response.get("next_page_token"),
        )

    async def fetch_page(
        self, url: str, include_html: bool = False, timeout: Optional[int] = 30
    ) -> FetchPageResponse:
        """
        Fetch and extract content from a web page using Jina API

        Args:
            url: URL of the page to fetch
            include_html: Whether to include raw HTML in response
            timeout: Timeout in seconds

        Returns:
            FetchPageResponse containing the page content
        """
        request = FetchPageRequest(url=url, include_html=include_html, timeout=timeout)

        response = await self._make_request(
            method="POST", endpoint="fetch", json_data=request.dict(exclude_none=True)
        )

        return FetchPageResponse(**response)
