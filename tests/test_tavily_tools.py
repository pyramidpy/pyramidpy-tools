from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from controlflow.tools.tools import Tool

from pyramidpy_tools.tavily_search.tools import (
    get_tavily_api,
    tavily_toolkit,
)


@pytest.fixture
def mock_search_response():
    return {
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


class TestTavilyAPI:
    def test_get_tavily_api_with_token(self):
        with patch(
            "pyramidpy_tools.settings.settings.tool_provider.tavily_api_key"
        ) as mock_key:
            mock_key.return_value = "test-key"
            with patch("pyramidpy_tools.tavily_search.tools.get_flow") as mock_get_flow:
                mock_flow = MagicMock()
                mock_flow.context = {"auth": {"api_key": "test-key"}}
                mock_get_flow.return_value = mock_flow

                api = get_tavily_api()
                assert api.client.api_key == "test-key"


@pytest.mark.asyncio
class TestTavilyTools:
    @pytest.fixture
    def mock_api(self):
        with patch("pyramidpy_tools.tavily_search.tools.get_tavily_api") as mock:
            mock_instance = AsyncMock()
            mock.return_value = mock_instance
            yield mock_instance

    def test_tools_configuration(self):
        """Test that all tools are properly configured in the toolkit"""
        assert isinstance(tavily_toolkit.tools[0], Tool)
        for tool in tavily_toolkit.tools:
            assert isinstance(tool, Tool)
            assert tool.name.startswith("tavily_")
            assert tool.description
            assert callable(tool.fn)

        assert tavily_toolkit.id == "tavily_toolkit"
        assert tavily_toolkit.is_app_default is True
        assert tavily_toolkit.requires_config is False
        assert "tavily" in tavily_toolkit.description.lower()

    async def test_tavily_search(self, mock_api, mock_search_response):
        mock_api.search.return_value = mock_search_response

        search_tool = next(t for t in tavily_toolkit.tools if t.name == "tavily_search")
        result = await search_tool.run_async(
            {
                "query": "test query",
            }
        )

        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Test Result"
        assert result["results"][0]["image"] == "https://test.com/image.jpg"
        assert result["answer"] == "Test answer"
        mock_api.search.assert_called_once_with(
            query="test query",
        )

    async def test_tavily_search_error(self, mock_api):
        mock_api.search.side_effect = Exception("API Error")

        search_tool = next(t for t in tavily_toolkit.tools if t.name == "tavily_search")
        with pytest.raises(Exception) as exc_info:
            await search_tool.run_async({"query": "test query"})
        assert "API Error" in str(exc_info.value)
