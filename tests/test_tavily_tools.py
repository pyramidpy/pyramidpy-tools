from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from controlflow.tools.tools import Tool

from pyramidpy_tools.tavily_search.tools import (
    get_tavily_api,
    tavily_toolkit,
)


def test_get_tavily_api_with_token():
    with patch(
        "app.settings.settings.tool_provider.tavily_api_key.get_secret_value",
        return_value="default-key",
    ):
        with patch("controlflow.flows.flow.get_flow") as mock_get_flow:
            mock_flow = MagicMock()
            mock_flow.context = {"tavily_api_key": "test-key"}
            mock_get_flow.return_value = mock_flow

            api = get_tavily_api()
            assert api.client.api_key == "test-key"


def test_get_tavily_api_without_token():
    with patch(
        "app.settings.settings.tool_provider.tavily_api_key.get_secret_value",
        return_value="default-key",
    ):
        with patch("controlflow.flows.flow.get_flow") as mock_get_flow:
            mock_get_flow.return_value = None

            api = get_tavily_api()
            assert api.client.api_key == "default-key"


def test_tools_are_properly_configured():
    """Test that all tools are properly configured in the toolkit"""
    assert isinstance(tavily_toolkit.tools[0], Tool)
    for tool in tavily_toolkit.tools:
        assert isinstance(tool, Tool)
        assert tool.name.startswith("tavily_")
        assert tool.description
        assert callable(tool.fn)


@pytest.fixture
def mock_api():
    with patch("pyramidpy_tools.tools.tavily.tools.get_tavily_api") as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.mark.asyncio
async def test_tavily_search_basic(mock_api):
    mock_api.search.return_value = {
        "results": [
            {
                "title": "Test Result",
                "url": "https://test.com",
                "content": "Test content",
            }
        ],
        "query": "test query",
    }

    search_tool = next(t for t in tavily_toolkit.tools if t.name == "tavily_search")
    result = await search_tool.run_async({"query": "test query"})

    assert "results" in result
    assert len(result["results"]) == 1
    assert result["results"][0]["title"] == "Test Result"
    mock_api.search.assert_called_once_with(
        query="test query",
    )


@pytest.mark.asyncio
async def test_tavily_search_with_options(mock_api):
    mock_api.search.return_value = {
        "results": [
            {
                "title": "Test Result",
                "url": "https://test.com",
                "content": "Test content",
                "image": "https://test.com/image.jpg",
            }
        ],
        "query": "test query",
        "answer": "Test answer",
    }

    search_tool = next(t for t in tavily_toolkit.tools if t.name == "tavily_search")
    result = await search_tool.run_async({"query": "test query"})

    assert "results" in result
    assert "answer" in result
    assert "image" in result["results"][0]
    mock_api.search.assert_called_once_with(
        query="test query",
    )


@pytest.mark.asyncio
async def test_tavily_get_search_context(mock_api):
    mock_api.get_search_context.return_value = {
        "context": "Test search context",
        "query": "test query",
        "token_count": 100,
    }

    get_context_tool = next(
        t for t in tavily_toolkit.tools if t.name == "tavily_get_search_context"
    )
    result = await get_context_tool.run_async(
        {"query": "test query", "max_tokens": 1000, "search_depth": "basic"}
    )

    assert isinstance(result, dict)
    assert "context" in result
    assert result["context"] == "Test search context"
    assert result["token_count"] == 100
    mock_api.get_search_context.assert_called_once_with(
        query="test query",
        max_tokens=1000,
        search_depth="basic",
        topic="general",
        max_results=5,
        include_domains=None,
        exclude_domains=None,
        days=None,
    )


@pytest.mark.asyncio
async def test_tavily_qna_search(mock_api):
    mock_api.qna_search.return_value = {
        "answer": "Test answer",
        "query": "test question",
        "sources": [{"title": "Source 1", "url": "https://test.com/1"}],
    }

    qna_tool = next(t for t in tavily_toolkit.tools if t.name == "tavily_qna_search")
    result = await qna_tool.run_async(
        {"query": "test question", "search_depth": "advanced", "topic": "technology"}
    )

    assert isinstance(result, dict)
    assert "answer" in result
    assert result["answer"] == "Test answer"
    assert "sources" in result
    mock_api.qna_search.assert_called_once_with(
        query="test question",
        search_depth="advanced",
        topic="technology",
        max_results=5,
        include_domains=None,
        exclude_domains=None,
        days=None,
    )


@pytest.mark.asyncio
async def test_tavily_search_error(mock_api):
    mock_api.search.side_effect = Exception("API Error")

    search_tool = next(t for t in tavily_toolkit.tools if t.name == "tavily_search")
    with pytest.raises(Exception) as exc_info:
        await search_tool.run_async({"query": "test query"})

    assert str(exc_info.value) == "API Error"
