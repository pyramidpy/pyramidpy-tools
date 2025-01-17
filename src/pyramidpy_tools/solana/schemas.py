from typing import Optional
from pydantic import BaseModel, Field


# Base Response
class SolanaResponse(BaseModel):
    success: bool
    error: Optional[str] = None


# Balance Related
class GetBalanceRequest(BaseModel):
    token_address: Optional[str] = Field(
        None,
        description="Optional SPL token mint address. If not provided, returns SOL balance",
    )


class BalanceResponse(SolanaResponse):
    balance: float
    token_address: Optional[str] = None
    decimals: Optional[int] = None


# Token Related
class DeployTokenRequest(BaseModel):
    name: str = Field(..., description="Token name")
    symbol: str = Field(..., description="Token symbol")
    decimals: int = Field(..., description="Number of decimals for the token")
    initial_supply: float = Field(..., description="Initial token supply")


class TokenDeployResponse(SolanaResponse):
    mint_address: str
    token_account: str
    transaction_signature: str


class BurnAndCloseRequest(BaseModel):
    token_address: str = Field(..., description="Token mint address to burn and close")
    token_account: str = Field(..., description="Token account to burn from and close")


class BurnAndCloseResponse(SolanaResponse):
    transaction_signature: str


# DEX Trading
class TradeRequest(BaseModel):
    pair_address: str = Field(..., description="DEX pair address")
    amount: float = Field(..., description="Amount to trade")
    slippage: int = Field(5, description="Slippage tolerance in percentage")
    percentage: Optional[int] = Field(
        None, description="Percentage of balance to trade (for sells)"
    )


class TradeResponse(SolanaResponse):
    transaction_signature: str
    amount_in: float
    amount_out: float
    price_impact: Optional[float] = None


# Moonshot Trading
class MoonshotTradeRequest(BaseModel):
    mint_address: str = Field(..., description="Token mint address")
    collateral_amount: Optional[float] = Field(
        0.01, description="Amount of SOL to spend"
    )
    token_amount: Optional[float] = Field(None, description="Amount of tokens to sell")
    slippage_bps: int = Field(500, description="Slippage tolerance in basis points")


class MoonshotTradeResponse(SolanaResponse):
    transaction_signature: str
    amount: float


# Meteora DLMM
class CreateDLMMPoolRequest(BaseModel):
    token_a: str = Field(..., description="First token address")
    token_b: str = Field(..., description="Second token address")
    amount_a: float = Field(..., description="Amount of first token")
    amount_b: float = Field(..., description="Amount of second token")
    fee_rate: float = Field(..., description="Fee rate in percentage")


class CreateDLMMPoolResponse(SolanaResponse):
    pool_address: str
    transaction_signature: str


# Price Data
class PriceRequest(BaseModel):
    token_address: str = Field(..., description="Token address to get price for")
    vs_currency: str = Field("usd", description="Currency to get price in")


class PriceResponse(SolanaResponse):
    price: float
    vs_currency: str
    timestamp: int


# Token Data
class TokenDataRequest(BaseModel):
    token_address: str = Field(..., description="Token address to get data for")


class TokenDataResponse(SolanaResponse):
    name: str
    symbol: str
    decimals: int
    total_supply: float
    holder_count: Optional[int] = None
    market_cap: Optional[float] = None
