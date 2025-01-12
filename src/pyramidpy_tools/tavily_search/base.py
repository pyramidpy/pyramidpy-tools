from typing import Any, Dict, List, Optional

from fastapi.logger import logger
from tavily import (
    InvalidAPIKeyError,
    MissingAPIKeyError,
    TavilyClient,
    UsageLimitExceededError,
)

from app.settings import settings


class TavilyAPI:
    def __init__(self, api_key: str | None = None):
        self.client = TavilyClient(
            api_key=api_key or settings.tool_provider.tavily_api_key.get_secret_value()
        )

    async def search(
        self,
        query: str,
    ) -> Dict[str, Any]:
        """
        Performs a Tavily Search query and returns the response.
        """
        try:
            return self.client.search(
                query=query,
            )
        except (MissingAPIKeyError, InvalidAPIKeyError) as e:
            logger.error(f"API key error: {e}")
            raise
        except UsageLimitExceededError as e:
            logger.error(f"Usage limit exceeded: {e}")
            raise
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            raise

    async def get_search_context(
        self,
        query: str,
        max_tokens: int = 4000,
        search_depth: str = "basic",
        topic: str = "general",
    ) -> Dict[str, Any]:
        """
        Gets search context within token limit.
        """
        try:
            return self.client.get_search_context(
                query=query,
                max_tokens=max_tokens,
                search_depth=search_depth,
                topic=topic,
            )
        except (MissingAPIKeyError, InvalidAPIKeyError) as e:
            logger.error(f"API key error: {e}")
            raise
        except UsageLimitExceededError as e:
            logger.error(f"Usage limit exceeded: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting search context: {e}")
            raise

    async def qna_search(
        self,
        query: str,
        search_depth: str = "advanced",
        topic: str = "general",
    ) -> Dict[str, Any]:
        """
        Performs a QnA search and returns an answer.
        """
        try:
            return self.client.qna_search(
                query=query,
                search_depth=search_depth,
                topic=topic,
            )
        except (MissingAPIKeyError, InvalidAPIKeyError) as e:
            logger.error(f"API key error: {e}")
            raise
        except UsageLimitExceededError as e:
            logger.error(f"Usage limit exceeded: {e}")
            raise
        except Exception as e:
            logger.error(f"Error performing QnA search: {e}")
            raise
