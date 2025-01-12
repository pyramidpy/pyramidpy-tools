from typing import List, Optional

from pydantic import BaseModel, Field


class TokenInfo(BaseModel):
    """Token information from DEX Screener"""

    name: str | None = Field(description="Name of the token", default=None)
    symbol: str | None = Field(description="Symbol of the token", default=None)
    address: str | None = Field(description="Address of the token", default=None)
    priceUsd: str | None = Field(description="Price of the token in USD", default=None)
    priceChange24h: float | None = Field(
        description="Price change of the token in the last 24 hours", default=None
    )
    liquidity: dict | None = Field(description="Liquidity of the token", default=None)
    fdv: float | None = Field(
        description="Fully diluted valuation of the token", default=None
    )
    volume24h: float | None = Field(
        description="Volume of the token in the last 24 hours", default=None
    )


class PairInfo(BaseModel):
    """Trading pair information from DEX Screener"""

    chainId: str | None = Field(
        description="Chain ID of the trading pair", default=None
    )
    dexId: str | None = Field(description="DEX ID of the trading pair", default=None)
    url: str | None = Field(description="URL of the trading pair", default=None)
    pairAddress: str | None = Field(
        description="Address of the trading pair", default=None
    )
    baseToken: TokenInfo | None = Field(
        description="Base token of the trading pair", default=None
    )
    quoteToken: TokenInfo | None = Field(
        description="Quote token of the trading pair", default=None
    )
    priceUsd: str | None = Field(
        description="Price of the trading pair in USD", default=None
    )
    priceChange24h: float | None = Field(
        description="Price change of the trading pair in the last 24 hours",
        default=None,
    )
    volume24h: float | None = Field(
        description="Volume of the trading pair in the last 24 hours", default=None
    )
    txns24h: dict | None = Field(
        description="Transactions of the trading pair in the last 24 hours",
        default=None,
    )


class DexScreenerResult(BaseModel):
    """Result wrapper for DEX Screener API calls"""

    data: List[PairInfo] | PairInfo | None = Field(
        description="Data from DEX Screener", default=None
    )
    error: Optional[str] = Field(description="Error from DEX Screener", default=None)
    success: bool = Field(
        description="Success status of the DEX Screener API call", default=True
    )
