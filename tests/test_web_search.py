from unittest.mock import MagicMock, patch

import pytest

from pyramidpy_tools.web_search import (
    JinaSearchAPIWrapper,
    JinaUrlFetchResult,
    JinaWebQueryResult,
    JinaWebSearchResult,
    web_fetch_url,
    web_loader,
    web_search,
)


@pytest.fixture
def mock_search_response():
    return {
        "data": [
            {
                "title": "Test Result",
                "url": "https://test.com",
                "description": "Test description",
                "content": "Test content",
                "images": None,
                "usage": None,
                "warnings": None,
            }
        ]
    }


@pytest.fixture
def mock_fetch_response():
    return {
        "data": {
            "title": "Test Page",
            "url": "https://test.com/page",
            "description": "Test page description",
            "content": "Test page content",
            "images": None,
            "usage": None,
            "warnings": None,
        }
    }


def test_web_search_success(mock_search_response):
    with patch("requests.get") as mock_get:
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = mock_search_response

        result = web_search("test query")

        assert result.success == True
        assert isinstance(result, JinaWebQueryResult)
        assert len(result.data) == 1
        assert isinstance(result.data[0], JinaWebSearchResult)
        assert result.data[0].title == "Test Result"
        assert result.data[0].url == "https://test.com"


def test_web_search_api_error():
    with patch("requests.get") as mock_get:
        mock_get.return_value.ok = False
        mock_get.return_value.status_code = 500

        result = web_search("test query")

        assert result.success == False
        assert result.error == "HTTP error 500"
        assert result.data is None


def test_web_fetch_url_success(mock_fetch_response):
    with patch("requests.get") as mock_get:
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = mock_fetch_response

        result = web_fetch_url("https://test.com")

        assert result.success == True
        assert isinstance(result, JinaUrlFetchResult)
        assert isinstance(result.data, JinaWebSearchResult)
        assert result.data.title == "Test Page"
        assert result.data.url == "https://test.com/page"


def test_web_fetch_url_api_error():
    with patch("requests.get") as mock_get:
        mock_get.return_value.ok = False
        mock_get.return_value.status_code = 404

        result = web_fetch_url("https://test.com")

        assert result.success == False
        assert result.error == "HTTP error 404"
        assert result.data is None


@pytest.mark.asyncio
async def test_web_loader():
    with patch("pyramidpy_tools.tools.web_search._web_loader") as mock_loader:
        mock_loader.return_value = []

        result = await web_loader(["https://test.com"])

        assert (
            result
            == "Web loader task started. Collection will be searchable using the kb tool."
        )
        mock_loader.assert_called_once_with(["https://test.com"], "adam_docs", 2)


def test_jina_search_api_wrapper_no_api_key():
    with patch("app.settings.settings") as mock_settings:
        mock_settings.tool_provider.jina_api_key = None

        wrapper = JinaSearchAPIWrapper()
        result = wrapper.search_web("test")

        assert result.success == False
        assert result.error == "Jina API key is not set"
        assert result.data is None


def test_jina_search_api_wrapper_exception():
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("Test error")

        wrapper = JinaSearchAPIWrapper()
        result = wrapper.search_web("test")

        assert result.success == False
        assert result.error == "Test error"
        assert result.data is None
