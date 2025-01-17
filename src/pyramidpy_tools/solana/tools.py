from typing import Optional

from controlflow.flows.flow import get_flow
from controlflow.tools.tools import tool

from pyramidpy_tools.toolkit import Toolkit

from .base import SolanaAPI
from .schemas import (
    BalanceResponse,
    TokenDeployResponse,
    BurnAndCloseResponse,
    TradeResponse,
    MoonshotTradeResponse,
    CreateDLMMPoolResponse,
    PriceResponse,
    TokenDataResponse,
)


def get_solana_api() -> SolanaAPI:
    """Get Solana API instance with config from context if available"""
    flow = get_flow()
    if flow and flow.context:
        rpc_url = flow.context.get("auth", {}).get("solana_rpc_url")
        if rpc_url:
            return SolanaAPI(rpc_url=rpc_url)
    return SolanaAPI()


@tool(
    name="solana_get_balance",
    description="Get the balance of SOL or an SPL token for the wallet",
    include_return_description=False,
)
async def get_balance(token_address: Optional[str] = None) -> BalanceResponse:
    solana = get_solana_api()
    return await solana.get_balance(token_address)


@tool(
    name="solana_deploy_token",
    description="Deploy a new SPL token with initial supply",
    include_return_description=False,
)
async def deploy_token(
    name: str, symbol: str, decimals: int, initial_supply: float
) -> TokenDeployResponse:
    solana = get_solana_api()
    return await solana.deploy_token(
        name=name, symbol=symbol, decimals=decimals, initial_supply=initial_supply
    )


@tool(
    name="solana_burn_and_close",
    description="Burn all tokens and close the token account",
    include_return_description=False,
)
async def burn_and_close(
    token_address: str, token_account: str
) -> BurnAndCloseResponse:
    solana = get_solana_api()
    return await solana.burn_and_close(
        token_address=token_address, token_account=token_account
    )


@tool(
    name="solana_trade_raydium",
    description="Execute a trade on Raydium DEX",
    include_return_description=False,
)
async def trade_raydium(
    pair_address: str,
    amount: float,
    is_buy: bool = True,
    slippage: int = 5,
    percentage: Optional[int] = None,
) -> TradeResponse:
    solana = get_solana_api()
    return await solana.trade_with_raydium(
        pair_address=pair_address,
        amount=amount,
        is_buy=is_buy,
        slippage=slippage,
        percentage=percentage,
    )


@tool(
    name="solana_trade_moonshot",
    description="Execute a trade on Moonshot DEX",
    include_return_description=False,
)
async def trade_moonshot(
    mint_address: str,
    is_buy: bool = True,
    collateral_amount: Optional[float] = 0.01,
    token_amount: Optional[float] = None,
    slippage_bps: int = 500,
) -> MoonshotTradeResponse:
    solana = get_solana_api()
    return await solana.trade_with_moonshot(
        mint_address=mint_address,
        is_buy=is_buy,
        collateral_amount=collateral_amount,
        token_amount=token_amount,
        slippage_bps=slippage_bps,
    )


@tool(
    name="solana_create_meteora_pool",
    description="Create a Meteora DLMM pool",
    include_return_description=False,
)
async def create_meteora_pool(
    token_a: str, token_b: str, amount_a: float, amount_b: float, fee_rate: float
) -> CreateDLMMPoolResponse:
    solana = get_solana_api()
    return await solana.create_meteora_pool(
        token_a=token_a,
        token_b=token_b,
        amount_a=amount_a,
        amount_b=amount_b,
        fee_rate=fee_rate,
    )


@tool(
    name="solana_get_token_price",
    description="Get token price from various sources",
    include_return_description=False,
)
async def get_token_price(
    token_address: str, vs_currency: str = "usd"
) -> PriceResponse:
    solana = get_solana_api()
    return await solana.get_token_price(
        token_address=token_address, vs_currency=vs_currency
    )


@tool(
    name="solana_get_token_data",
    description="Get detailed token data",
    include_return_description=False,
)
async def get_token_data(token_address: str) -> TokenDataResponse:
    solana = get_solana_api()
    return await solana.get_token_data(token_address)


solana_toolkit = Toolkit.create_toolkit(
    id="solana_toolkit",
    tools=[
        get_balance,
        deploy_token,
        burn_and_close,
        trade_raydium,
        trade_moonshot,
        create_meteora_pool,
        get_token_price,
        get_token_data,
    ],
    auth_key="solana_auth",
    requires_config=True,
    name="Solana Toolkit",
    description="Tools for interacting with Solana blockchain",
)
