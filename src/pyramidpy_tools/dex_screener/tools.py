from controlflow.tools.tools import tool

from pyramidpy_tools.dex_screener.base import DexScreenerAPI
from pyramidpy_tools.dex_screener.schemas import DexScreenerResult
from pyramidpy_tools.toolkit import Toolkit


@tool(
    name="dex_search_pairs",
    description="""
    Search for trading pairs on DEX Screener using a token address, symbol, or name
    Use this tool to find tolkens on DEX Screener.
    """,
    include_return_description=False,
)
def search_pairs(query: str) -> DexScreenerResult:
    """Search for trading pairs on DEX Screener.
    Args:
        query: Token address, symbol, or name to search for
    Returns:
        List of matching trading pairs with their information
    """
    return DexScreenerAPI().search_pairs(query)


@tool(
    name="dex_get_pair",
    description="Get detailed information about a specific trading pair on DEX Screener",
    include_return_description=False,
)
def get_pair(pair_address: str, chain_id: str) -> DexScreenerResult:
    """Get detailed information about a specific trading pair.
    Args:
        pair_address: The address of the trading pair
        chain_id: The chain ID where the pair exists (e.g., 'ethereum', 'bsc')
    Returns:
        Detailed information about the trading pair
    """
    return DexScreenerAPI().get_pair(pair_address, chain_id)


dex_screener_toolkit = Toolkit.create_toolkit(
    id="dex_screener_toolkit",
    tools=[search_pairs, get_pair],
    name="DEX Screener Toolkit",
    is_app_default=True,
    requires_config=False,
    description="Tools for searching and getting information about trading pairs on DEX Screener",
)
