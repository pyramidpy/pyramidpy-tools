from unittest.mock import Mock, patch

import pytest
from controlflow.tools.tools import Tool
from pyramidpy_tools.dex_screener.base import DexScreenerAPI
from pyramidpy_tools.dex_screener.schemas import DexScreenerResult, PairInfo, TokenInfo
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


class TestSchemas:
    def test_token_info_validation(self, sample_token_info):
        token = TokenInfo(**sample_token_info)
        assert token.name == sample_token_info["name"]
        assert token.symbol == sample_token_info["symbol"]
        assert token.priceUsd == sample_token_info["priceUsd"]
        assert token.liquidity == sample_token_info["liquidity"]

        # Test optional fields
        minimal_token = TokenInfo(name="Test")
        assert minimal_token.symbol is None
        assert minimal_token.address is None

    def test_pair_info_validation(self, sample_pair_info):
        pair = PairInfo(**sample_pair_info)
        assert pair.chainId == sample_pair_info["chainId"]
        assert pair.dexId == sample_pair_info["dexId"]
        assert isinstance(pair.baseToken, TokenInfo)
        assert isinstance(pair.quoteToken, TokenInfo)

        # Test optional fields
        minimal_pair = PairInfo(chainId="ethereum")
        assert minimal_pair.baseToken is None
        assert minimal_pair.priceUsd is None

    def test_dex_screener_result_validation(self, sample_pair_info):
        # Test with single pair
        result = DexScreenerResult(data=PairInfo(**sample_pair_info))
        assert isinstance(result.data, PairInfo)
        assert result.success is True
        assert result.error is None

        # Test with multiple pairs
        result = DexScreenerResult(data=[PairInfo(**sample_pair_info)])
        assert isinstance(result.data, list)
        assert isinstance(result.data[0], PairInfo)

        # Test error case
        error_result = DexScreenerResult(error="Test error", success=False)
        assert error_result.data is None
        assert error_result.success is False
        assert error_result.error == "Test error"


class TestDexScreenerAPI:
    def test_init(self):
        api = DexScreenerAPI()
        assert api.base_url == "https://api.dexscreener.com/latest"

    @pytest.mark.asyncio
    async def test_search_pairs(self, mock_response, sample_pair_info):
        with patch("httpx.get") as mock_get:
            mock_response.json.return_value = {"pairs": [sample_pair_info]}
            mock_get.return_value = mock_response

            api = DexScreenerAPI()
            result = api.search_pairs("TEST")

            assert isinstance(result, DexScreenerResult)
            assert result.success is True
            assert isinstance(result.data[0], PairInfo)
            mock_get.assert_called_once_with(
                "https://api.dexscreener.com/latest/dex/search?q=TEST", timeout=30
            )

    @pytest.mark.asyncio
    async def test_search_pairs_error_handling(self, mock_response):
        with patch("httpx.get") as mock_get:
            # Test HTTP error
            mock_response.ok = False
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            api = DexScreenerAPI()
            result = api.search_pairs("TEST")

            assert isinstance(result, DexScreenerResult)
            assert result.success is False
            assert result.error == "HTTP error 404"

            # Test network error
            mock_get.side_effect = Exception("Network error")
            result = api.search_pairs("TEST")

            assert result.success is False
            assert result.error == "Network error"

    @pytest.mark.asyncio
    async def test_get_pair(self, mock_response, sample_pair_info):
        with patch("httpx.get") as mock_get:
            mock_response.json.return_value = {"pair": sample_pair_info}
            mock_get.return_value = mock_response

            api = DexScreenerAPI()
            result = api.get_pair("0x123...", "ethereum")

            assert isinstance(result, DexScreenerResult)
            assert result.success is True
            assert isinstance(result.data, PairInfo)
            mock_get.assert_called_once_with(
                "https://api.dexscreener.com/latest/dex/pairs/ethereum/0x123...",
                timeout=30,
            )

    @pytest.mark.asyncio
    async def test_get_pair_error_handling(self, mock_response):
        with patch("httpx.get") as mock_get:
            # Test pair not found
            mock_response.ok = True
            mock_response.json.return_value = {"pair": None}
            mock_get.return_value = mock_response

            api = DexScreenerAPI()
            result = api.get_pair("0x123...", "ethereum")

            assert isinstance(result, DexScreenerResult)
            assert result.success is False
            assert result.error == "Pair not found"

            # Test HTTP error
            mock_response.ok = False
            mock_response.status_code = 500
            mock_get.return_value = mock_response

            result = api.get_pair("0x123...", "ethereum")
            assert result.success is False
            assert result.error == "HTTP error 500"

            # Test network error
            mock_get.side_effect = Exception("Network error")
            result = api.get_pair("0x123...", "ethereum")

            assert result.success is False
            assert result.error == "Network error"


@pytest.mark.asyncio
class TestDexScreenerTools:
    @pytest.fixture
    def mock_api(self):
        with patch("pyramidpy_tools.dex_screener.tools.DexScreenerAPI") as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            yield mock_instance

    def test_tools_configuration(self):
        assert isinstance(search_pairs, Tool)
        assert isinstance(get_pair, Tool)
        assert search_pairs.name == "dex_search_pairs"
        assert get_pair.name == "dex_get_pair"
        assert "token address, symbol, or name" in search_pairs.description.lower()
        assert "specific trading pair" in get_pair.description.lower()

    async def test_search_pairs_tool(self, mock_api, sample_pair_info):
        mock_api.search_pairs.return_value = DexScreenerResult(
            data=[PairInfo(**sample_pair_info)]
        )

        result = await search_pairs.run_async({"query": "TEST"})

        assert isinstance(result, DexScreenerResult)
        assert result.success is True
        assert isinstance(result.data[0], PairInfo)
        mock_api.search_pairs.assert_called_once_with("TEST")

    async def test_get_pair_tool(self, mock_api, sample_pair_info):
        mock_api.get_pair.return_value = DexScreenerResult(
            data=PairInfo(**sample_pair_info)
        )

        result = await get_pair.run_async(
            {"pair_address": "0x123...", "chain_id": "ethereum"}
        )

        assert isinstance(result, DexScreenerResult)
        assert result.success is True
        assert isinstance(result.data, PairInfo)
        mock_api.get_pair.assert_called_once_with("0x123...", "ethereum")

    def test_toolkit_configuration(self):
        assert dex_screener_toolkit.id == "dex_screener_toolkit"
        assert len(dex_screener_toolkit.tools) == 2
        assert search_pairs in dex_screener_toolkit.tools
        assert get_pair in dex_screener_toolkit.tools
        assert dex_screener_toolkit.is_app_default is True
        assert dex_screener_toolkit.requires_config is False
        assert "dex screener" in dex_screener_toolkit.description.lower()
