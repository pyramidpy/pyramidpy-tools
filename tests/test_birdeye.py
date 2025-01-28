from unittest.mock import patch

import pytest
from controlflow.flows.flow import Flow, get_flow

from pyramidpy_tools.birdeye.base import BirdeyeAPI
from pyramidpy_tools.birdeye.schemas import (
    HistoricalPriceParams,
    TokenOverviewParams,
    TokenPriceRequest,
    TransactionParams,
)
from pyramidpy_tools.birdeye.tools import (
    SupportedChain,
    get_birdeye_api,
)
from pyramidpy_tools.settings import settings

# Test constants - using real Solana addresses
WSOL_ADDRESS = "So11111111111111111111111111111111111111112"
USDC_ADDRESS = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
RAYDIUM_WSOL_USDC_PAIR = "58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2"


def auth_callback(key, context):
    if key == "birdeye_api_key":
        return {"api_key": settings.tool_provider.birdeye_api_key}
    return None


@pytest.fixture
def api_key():
    """Get API key from environment variable."""
    flow = get_flow() or Flow()
    flow.context["auth"] = auth_callback
    return flow


@pytest.fixture
def api() -> BirdeyeAPI:
    """Create an authenticated API client."""
    with patch("pyramidpy_tools.birdeye.tools.get_flow") as mock_get_flow:
        # Setup mock flow with proper context structure
        flow = Flow()
        flow.context = {"auth": auth_callback}
        mock_get_flow.return_value = flow
        birdeye_api = get_birdeye_api()
    return birdeye_api


@pytest.mark.asyncio
async def test_get_multi_token_price(api: BirdeyeAPI):
    """Test getting prices for multiple tokens."""

    result = await api.get_multi_price(
        TokenPriceRequest(
            addresses=[WSOL_ADDRESS, USDC_ADDRESS], chain=SupportedChain.SOLANA
        )
    )

    assert result is not None
    assert "data" in result

    # Check WSOL price data
    wsol_data = result["data"].get(WSOL_ADDRESS)
    assert wsol_data is not None
    assert "value" in wsol_data
    assert wsol_data["value"] > 0

    # Check USDC price data
    usdc_data = result["data"].get(USDC_ADDRESS)
    assert usdc_data is not None
    assert "value" in usdc_data
    assert abs(usdc_data["value"] - 1.0) < 0.1  # USDC should be close to $1


@pytest.mark.asyncio
async def test_get_token_price_history(api: BirdeyeAPI):
    """Test getting historical price data."""
    result = await api.get_history_price(
        HistoricalPriceParams(
            address=WSOL_ADDRESS,
            address_type="token",
            type="15m",
            chain=SupportedChain.SOLANA,
        )
    )

    assert result is not None, result
    assert "data" in result
    assert "items" in result["data"]


@pytest.mark.asyncio
async def test_get_token_transactions(api: BirdeyeAPI):
    """Test getting token transactions."""
    result = await api.get_token_transactions(
        TransactionParams(address=WSOL_ADDRESS, limit=10, chain=SupportedChain.SOLANA)
    )

    assert result is not None
    assert "data" in result
    assert "items" in result["data"]

    items = result["data"]["items"]
    assert len(items) > 0
    assert len(items) <= 10  # Check limit is respected

    # Check first transaction
    first_tx = items[0]
    quote = first_tx["quote"]
    assert "address" in quote
    assert "blockUnixTime" in first_tx
    assert "owner" in first_tx


@pytest.mark.asyncio
async def test_get_pair_transactions(api: BirdeyeAPI):
    """Test getting pair transactions."""
    result = await api.get_pair_transactions(
        TransactionParams(
            address=RAYDIUM_WSOL_USDC_PAIR, limit=10, chain=SupportedChain.SOLANA
        )
    )

    assert result is not None
    assert "data" in result
    assert "items" in result["data"]

    items = result["data"]["items"]
    assert len(items) > 0
    assert len(items) <= 10  # Check limit is respected

    # Check first transaction
    first_tx = items[0]
    assert "address" in first_tx
    assert "blockUnixTime" in first_tx
    assert "owner" in first_tx


@pytest.mark.asyncio
async def test_chain_support(api: BirdeyeAPI):
    """Test API support for different chains."""
    # Test Ethereum chain
    eth_usdc = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  # USDC on Ethereum
    result = await api.get_multi_price(
        TokenPriceRequest(addresses=[eth_usdc], chain=SupportedChain.ETHEREUM)
    )

    assert result is not None
    assert "data" in result

    # Check USDC price data
    usdc_data = result["data"].get(eth_usdc)
    assert usdc_data is not None
    assert "value" in usdc_data
    assert abs(usdc_data["value"] - 1.0) < 0.1  # USDC should be close to $1


@pytest.mark.asyncio
async def test_get_token_overview(api: BirdeyeAPI):
    """Test getting token overview data."""
    result = await api.get_token_overview(
        TokenOverviewParams(address=WSOL_ADDRESS, chain=SupportedChain.SOLANA)
    )

    assert result is not None
    assert result.success is True

    data = result.data
    assert data.address == WSOL_ADDRESS
    assert data.symbol == "SOL"
    assert data.name == "Wrapped SOL"
    assert data.decimals == 9

    # Check extensions
    assert data.extensions is not None
    assert data.extensions.coingeckoId == "solana"

    # Check price and volume data
    assert data.price > 0
    assert data.liquidity > 0
    assert data.v24h > 0
    assert data.v24hUSD > 0

    # Check market metrics
    assert data.supply > 0
    assert data.mc > 0
    assert data.circulatingSupply > 0
    assert data.realMc > 0
    assert data.holder > 0
    assert data.numberMarkets > 0

    # Check trade data exists
    assert data.trade24h > 0
    assert data.sell24h > 0
    assert data.buy24h > 0
