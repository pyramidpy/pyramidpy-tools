from unittest.mock import Mock, patch

import pytest
from controlflow.tools.tools import Tool
from pyramidpy_tools.dex_screener.base import DexScreenerAPI
from pyramidpy_tools.dex_screener.schemas import DexScreenerResult, PairInfo
from pyramidpy_tools.dex_screener.tools import (
    dex_screener_toolkit,
    get_pair,
    search_pairs,
)


@pytest.fixture
def mock_response():
    mock = Mock()
    mock.ok = True
    return mock


@pytest.fixture
def sample_token_info():
    return {
        "name": "Test Token",
        "symbol": "TEST",
        "address": "0x123...",
        "priceUsd": "1.23",
        "priceChange24h": 5.67,
        "liquidity": {"usd": 1000000},
        "fdv": 10000000,
        "volume24h": 500000,
    }


@pytest.fixture
def sample_pair_info(sample_token_info):
    return {
        "chainId": "ethereum",
        "dexId": "uniswap",
        "url": "https://dexscreener.com/ethereum/0x123...",
        "pairAddress": "0x456...",
        "baseToken": sample_token_info,
        "quoteToken": sample_token_info,
        "priceUsd": "1.23",
        "priceChange24h": 5.67,
        "volume24h": 1000000,
        "txns24h": {"buys": 100, "sells": 50},
    }


class TestDexScreenerAPI:
    def test_init(self):
        api = DexScreenerAPI()
        assert api.base_url == "https://api.dexscreener.com/latest"

    @pytest.mark.asyncio
    async def test_search_pairs(self, mock_response):
        with patch("requests.get") as mock_get:
            mock_response.json.return_value = {"pairs": [{"chainId": "ethereum"}]}
            mock_get.return_value = mock_response

            api = DexScreenerAPI()
            result = api.search_pairs("TEST")

            assert isinstance(result, DexScreenerResult)
            mock_get.assert_called_once_with(
                "https://api.dexscreener.com/latest/dex/search?q=TEST"
            )

    @pytest.mark.asyncio
    async def test_search_pairs_error(self, mock_response):
        with patch("requests.get") as mock_get:
            mock_response.ok = False
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            api = DexScreenerAPI()
            result = api.search_pairs("TEST")

            assert isinstance(result, DexScreenerResult)
            assert result.success is False
            assert result.error == "HTTP error 404"

    @pytest.mark.asyncio
    async def test_get_pair(self, mock_response, sample_pair_info):
        with patch("requests.get") as mock_get:
            mock_response.json.return_value = {"pair": sample_pair_info}
            mock_get.return_value = mock_response

            api = DexScreenerAPI()
            result = api.get_pair("0x123...", "ethereum")

            assert isinstance(result, DexScreenerResult)
            assert isinstance(result.data, PairInfo)
            mock_get.assert_called_once_with(
                "https://api.dexscreener.com/latest/dex/pairs/ethereum/0x123..."
            )

    @pytest.mark.asyncio
    async def test_get_pair_not_found(self, mock_response):
        with patch("requests.get") as mock_get:
            mock_response.json.return_value = {"pair": None}
            mock_get.return_value = mock_response

            api = DexScreenerAPI()
            result = api.get_pair("0x123...", "ethereum")

            assert isinstance(result, DexScreenerResult)
            assert result.success is False
            assert result.error == "Pair not found"


@pytest.mark.asyncio
class TestDexScreenerTools:
    @pytest.fixture
    def mock_api(self):
        with patch("pyramidpy_tools.tools.dex_screener.tools.DexScreenerAPI") as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            yield mock_instance

    def test_tools_are_properly_configured(self):
        assert isinstance(search_pairs, Tool)
        assert isinstance(get_pair, Tool)
        assert "dex_search_pairs" == search_pairs.name
        assert "dex_get_pair" == get_pair.name

    async def test_search_pairs_tool(self, mock_api, sample_pair_info):
        mock_api.search_pairs.return_value = DexScreenerResult(
            data=[PairInfo(**sample_pair_info)]
        )

        result = await search_pairs.run_async({"query": "TEST"})
        assert isinstance(result, DexScreenerResult)
        mock_api.search_pairs.assert_called_once_with("TEST")

    async def test_get_pair_tool(self, mock_api, sample_pair_info):
        mock_api.get_pair.return_value = DexScreenerResult(
            data=PairInfo(**sample_pair_info)
        )

        result = await get_pair.run_async(
            {"pair_address": "0x123...", "chain_id": "ethereum"}
        )
        assert isinstance(result, DexScreenerResult)
        mock_api.get_pair.assert_called_once_with("0x123...", "ethereum")

    def test_toolkit_configuration(self):
        assert dex_screener_toolkit.id == "dex_screener_toolkit"
        assert len(dex_screener_toolkit.tools) == 2
        assert search_pairs in dex_screener_toolkit.tools
        assert get_pair in dex_screener_toolkit.tools
