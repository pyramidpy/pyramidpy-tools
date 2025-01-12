from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    url: str
    title: str
    content: str
    score: float
    images: Optional[List[str]] = None
    published_date: Optional[str] = None
    author: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    answer: Optional[str] = None
    raw_content: Optional[List[Dict[str, Any]]] = None


class SearchRequest(BaseModel):
    query: str = Field(..., description="The search query")
    # search_depth: str = Field(
    #     "basic", description="Search depth: 'basic' or 'advanced'"
    # )
    # topic: str = Field("general", description="Topic category for the search")
    # max_results: int = Field(5, description="Maximum number of results to return")
    # include_images: bool = Field(
    #     False, description="Whether to include images in results"
    # )
    # include_answer: bool = Field(
    #     False, description="Whether to include an AI-generated answer"
    # )
    # include_raw_content: bool = Field(
    #     False, description="Whether to include raw content"
    # )
    # include_domains: Optional[List[str]] = Field(
    #     None, description="List of domains to include"
    # )
    # exclude_domains: Optional[List[str]] = Field(
    #     None, description="List of domains to exclude"
    # )
    # days: Optional[int] = Field(None, description="Number of days to look back")


class SearchContextRequest(BaseModel):
    query: str = Field(..., description="The search query")
    max_tokens: int = Field(
        4000, description="Maximum number of tokens in the response"
    )
    search_depth: str = Field(
        "basic", description="Search depth: 'basic' or 'advanced'"
    )
    topic: str = Field("general", description="Topic category for the search")
    max_results: int = Field(5, description="Maximum number of results to return")
    include_domains: Optional[List[str]] = Field(
        None, description="List of domains to include"
    )
    exclude_domains: Optional[List[str]] = Field(
        None, description="List of domains to exclude"
    )
    days: Optional[int] = Field(None, description="Number of days to look back")


class QnASearchRequest(BaseModel):
    query: str = Field(..., description="The question to answer")
    search_depth: str = Field(
        "advanced", description="Search depth: 'basic' or 'advanced'"
    )
    topic: str = Field("general", description="Topic category for the search")
    max_results: int = Field(5, description="Maximum number of results to return")
    include_domains: Optional[List[str]] = Field(
        None, description="List of domains to include"
    )
    exclude_domains: Optional[List[str]] = Field(
        None, description="List of domains to exclude"
    )
    days: Optional[int] = Field(None, description="Number of days to look back")


class TavilyAuthConfig(BaseModel):
    api_key: str = Field(..., description="Tavily API key")
