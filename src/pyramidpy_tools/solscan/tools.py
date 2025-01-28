from typing import List, Optional

from controlflow.flows.flow import get_flow
from controlflow.tools.tools import tool

from pyramidpy_tools.toolkit import Toolkit

from .base import SolscanAPI
from .schemas import AccountTransferParams, SolscanAuth

AUTH_KEY = "solscan_token"


def get_solscan_api() -> SolscanAPI:
    """Get Solscan API instance with token from context if available"""
    flow = get_flow()
    if flow and flow.context:
        auth = flow.context.get("auth", {}).get(AUTH_KEY)
        if auth:
            try:
                auth = SolscanAuth(api_key=auth)
                return SolscanAPI(auth=auth)
            except Exception as e:
                raise ValueError(f"Invalid Solscan token: {e}")
    return SolscanAPI()


@tool(
    name="solscan_get_chain_info",
    description="Get Solana chain information including current slot, block height, etc.",
    include_return_description=False,
)
async def solscan_get_chain_info():
    async with get_solscan_api() as api:
        return await api.get_chain_info()


@tool(
    name="solscan_get_account_transactions",
    description="Get transactions for a Solana account address",
    include_return_description=False,
)
async def solscan_get_account_transactions(
    address: str, before: Optional[int] = None, limit: int = 10
):
    async with get_solscan_api() as api:
        return await api.get_account_transactions(address, before, limit)


@tool(
    name="solscan_get_token_holders",
    description="Get token holders for a Solana SPL token",
    include_return_description=False,
)
async def solscan_get_token_holders(token: str, offset: int = 0, limit: int = 10):
    async with get_solscan_api() as api:
        return await api.get_token_holders(token, offset, limit)


@tool(
    name="solscan_get_token_meta",
    description="Get metadata for a Solana SPL token",
    include_return_description=False,
)
async def solscan_get_token_meta(token: str):
    async with get_solscan_api() as api:
        return await api.get_token_meta(token)


@tool(
    name="solscan_get_account_tokens",
    description="Get token balances for a Solana account",
    include_return_description=False,
)
async def solscan_get_account_tokens(address: str):
    async with get_solscan_api() as api:
        return await api.get_account_tokens(address)


@tool(
    name="solscan_get_account_stake",
    description="Get stake accounts info for a Solana account",
    include_return_description=False,
)
async def solscan_get_account_stake(address: str):
    async with get_solscan_api() as api:
        return await api.get_account_stake(address)


@tool(
    name="solscan_get_account_transfer_history",
    description="""Get transfer history for a Solana account (Pro API - requires API key).
    Example:
    {
        "address": "FZp6uNgE4WgWANs8EX63pnC8eKo1P6is3SdVbBnFCKtT",
        "activity_type": ["ACTIVITY_SPL_TRANSFER"],
        "token": "So11111111111111111111111111111111111111112",
        "page": 1,
        "page_size": 20,
        "sort_by": "block_time",
        "sort_order": "desc"
    }""",
    include_return_description=False,
)
async def solscan_get_account_transfer_history(
    address: str,
    activity_type: Optional[List[str]] = None,
    token_account: Optional[str] = None,
    from_address: Optional[str] = None,
    to_address: Optional[str] = None,
    token: Optional[str] = None,
    amount: Optional[List[float]] = None,
    block_time: Optional[List[int]] = None,
    exclude_amount_zero: Optional[bool] = None,
    flow: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
):
    params = AccountTransferParams(
        address=address,
        activity_type=activity_type,
        token_account=token_account,
        from_address=from_address,
        to_address=to_address,
        token=token,
        amount=amount,
        block_time=block_time,
        exclude_amount_zero=exclude_amount_zero,
        flow=flow,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    async with get_solscan_api() as api:
        return await api.get_account_transfer_history(params)


solscan_toolkit = Toolkit.create_toolkit(
    id="solscan_toolkit",
    tools=[
        solscan_get_chain_info,
        solscan_get_account_transactions,
        solscan_get_token_holders,
        solscan_get_token_meta,
        solscan_get_account_tokens,
        solscan_get_account_stake,
        solscan_get_account_transfer_history,
    ],
    auth_key=AUTH_KEY,
    requires_config=False,  # API key is optional
    auth_config_schema=SolscanAuth,
    is_app_default=True,
    name="Solscan Toolkit",
    description="Tools for interacting with Solscan API to fetch Solana blockchain data",
)
