from typing import List, Dict, Any, Literal
from controlflow.tools.tools import tool
from controlflow.flows.flow import get_flow
from pyramidpy_tools.utilities.auth import get_auth_from_context
from pyramidpy_tools.settings import settings
from pyramidpy_tools.toolkit import Toolkit

from .base import BirdeyeAPI
from .schemas import (
    BirdeyeAuth,
    TokenPriceRequest,
    HistoricalPriceParams,
    TransactionParams,
    SupportedChain,
    TokenOverviewParams,
    TokenOverviewResponse,
    SearchParams,
    SearchSortBy,
)

AUTH_KEY = "birdeye_api_key"


def get_birdeye_api() -> BirdeyeAPI:
    """Get an authenticated Birdeye API client instance."""

    flow = get_flow()
    auth_data = get_auth_from_context(flow.context, AUTH_KEY)
    print(auth_data)
    if auth_data:
        return BirdeyeAPI(BirdeyeAuth(**auth_data))

    if settings.tool_provider.birdeye_api_key:
        return BirdeyeAPI(BirdeyeAuth(api_key=settings.tool_provider.birdeye_api_key))

    raise ValueError("No authentication found for Birdeye API")


@tool(
    name="get_multi_token_price",
    description="Get prices for multiple tokens",
    instructions="Provide a list of token addresses and optionally specify the chain",
)
async def get_multi_token_price(
    addresses: List[str], chain: SupportedChain = SupportedChain.SOLANA
) -> Dict[str, Any]:
    """
    Get prices for multiple tokens.

    Args:
        addresses: List of token addresses
        chain: Blockchain network (defaults to Solana)

    Returns:
        Dict containing price data for requested tokens
    """
    api = get_birdeye_api()
    request = TokenPriceRequest(addresses=addresses, chain=chain)
    return await api.get_multi_price(request)


@tool(
    name="get_token_price_history",
    description="Get historical price data for a token",
    instructions="Provide token address and time interval (e.g., '15m', '1h', '4h', '1d')",
)
async def get_token_price_history(
    address: str,
    interval: str,
    address_type: str = "token",
    chain: SupportedChain = SupportedChain.SOLANA,
) -> Dict[str, Any]:
    """
    Get historical price data.

    Args:
        address: Token address
        interval: Time interval
        address_type: Type of address (defaults to 'token')
        chain: Blockchain network (defaults to Solana)

    Returns:
        Dict containing historical price data
    """
    api = get_birdeye_api()
    params = HistoricalPriceParams(
        address=address, address_type=address_type, type=interval, chain=chain
    )
    return await api.get_history_price(params)


@tool(
    name="get_token_transactions",
    description="Get token transactions",
    instructions="Provide token address and optional pagination parameters",
)
async def get_token_transactions(
    address: str,
    offset: int = 0,
    limit: int = 50,
    tx_type: str = "swap",
    sort_type: str = "desc",
    chain: SupportedChain = SupportedChain.SOLANA,
) -> Dict[str, Any]:
    """
    Get token transactions.

    Args:
        address: Token address
        offset: Pagination offset
        limit: Number of results per page
        tx_type: Transaction type
        sort_type: Sort direction
        chain: Blockchain network (defaults to Solana)

    Returns:
        Dict containing token transactions
    """
    api = get_birdeye_api()
    params = TransactionParams(
        address=address,
        offset=offset,
        limit=limit,
        tx_type=tx_type,
        sort_type=sort_type,
        chain=chain,
    )
    return await api.get_token_transactions(params)


@tool(
    name="get_pair_transactions",
    description="Get pair transactions",
    instructions="Provide pair address and optional pagination parameters",
    include_return_description=False,
    include_param_descriptions=False,
)
async def get_pair_transactions(
    address: str,
    offset: int = 0,
    limit: int = 50,
    tx_type: str = "swap",
    sort_type: str = "desc",
    chain: SupportedChain = SupportedChain.SOLANA,
) -> Dict[str, Any]:
    """
    Get pair transactions.

    Args:
        address: Pair address
        offset: Pagination offset
        limit: Number of results per page
        tx_type: Transaction type
        sort_type: Sort direction
        chain: Blockchain network (defaults to Solana)

    Returns:
        Dict containing pair transactions
    """
    api = get_birdeye_api()
    params = TransactionParams(
        address=address,
        offset=offset,
        limit=limit,
        tx_type=tx_type,
        sort_type=sort_type,
        chain=chain,
    )
    return await api.get_pair_transactions(params)


@tool(
    name="get_token_overview",
    description="Get comprehensive overview data for a token including price, volume, and market metrics",
    instructions="""
    Provide the token address to get detailed token information.
    Use the exact contract address that the user provided. Do not make up your own address or modify it.
    """,
    include_return_description=False,
    include_param_descriptions=False,
)
async def get_token_overview(
    address: str, chain: SupportedChain = SupportedChain.SOLANA
) -> TokenOverviewResponse:
    """
    Get comprehensive token overview data.

    Args:
        address: Token address
        chain: Blockchain network (defaults to Solana)

    Returns:
        TokenOverviewResponse containing comprehensive token data including price, volume, and market metrics
    """
    api = get_birdeye_api()
    params = TokenOverviewParams(address=address, chain=chain)
    result = await api.get_token_overview(params)
    return result


@tool(
    name="search_tokens",
    description="Search for tokens or pairs on Birdeye",
    instructions="""
    Search for tokens or pairs using a keyword.
    You can search for tokens, pairs, or both.
    Results are sorted by 24h volume by default.
    """,
)
async def search_tokens(
    keyword: str,
    target: Literal["token", "market", "all"] = "all",
    sort_by: SearchSortBy = SearchSortBy.VOLUME_24H_USD,
    sort_type: Literal["asc", "desc"] = "desc",
    offset: int = 0,
    limit: int = 20,
    chain: SupportedChain = SupportedChain.SOLANA,
) -> Dict[str, Any]:
    """
    Search for tokens or pairs.

    Args:
        keyword: Search keyword
        target: Search target (all, token, pair)
        sort_by: Sort field
        sort_type: Sort direction (asc, desc)
        offset: Pagination offset
        limit: Number of results
        chain: Blockchain network

    Returns:
        Dict containing search results
    """
    api = get_birdeye_api()
    params = SearchParams(
        keyword=keyword,
        target=target,
        sort_by=sort_by,
        sort_type=sort_type,
        offset=offset,
        limit=limit,
        chain=chain,
    )
    return await api.search(params)


birdeye_toolkit = Toolkit.create_toolkit(
    tools=[
        get_multi_token_price,
        get_token_price_history,
        get_token_transactions,
        get_pair_transactions,
        get_token_overview,
        search_tokens,
    ],
    description="Birdeye API tools",
    name="Birdeye Toolkit",
    id="birdeye_toolkit",
    is_app_default=True,
    auth_key=AUTH_KEY,
    requires_config=True,
    auth_config_schema=BirdeyeAuth,
)
