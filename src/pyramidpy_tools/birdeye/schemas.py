from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class SupportedChain(str, Enum):
    """Supported blockchain networks."""

    SOLANA = "solana"
    ETHEREUM = "ethereum"
    BSC = "bsc"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    AVALANCHE = "avalanche"


class BirdeyeAuth(BaseModel):
    """Authentication credentials for the Birdeye API."""

    api_key: str = Field(description="API key for Birdeye")


class TokenPriceRequest(BaseModel):
    """Request schema for multi-token price endpoint."""

    addresses: List[str] = Field(description="List of token addresses")
    chain: SupportedChain = Field(
        default=SupportedChain.SOLANA, description="Blockchain network"
    )


class HistoricalPriceParams(BaseModel):
    """Parameters for historical price endpoint."""

    address: str = Field(description="Token address")
    address_type: str = Field(description="Type of address (e.g., 'token')")
    type: str = Field(description="Time interval (e.g., '15m')")
    chain: SupportedChain = Field(
        default=SupportedChain.SOLANA, description="Blockchain network"
    )


class TransactionParams(BaseModel):
    """Parameters for transaction endpoints."""

    address: str = Field(description="Token or pair address")
    offset: int = Field(default=0, description="Pagination offset")
    limit: int = Field(default=50, description="Number of results per page")
    tx_type: str = Field(default="swap", description="Transaction type")
    sort_type: str = Field(default="desc", description="Sort direction")
    chain: SupportedChain = Field(
        default=SupportedChain.SOLANA, description="Blockchain network"
    )


class TokenInfo(BaseModel):
    """Token information schema."""

    address: str = Field(description="Token address")
    chain_id: str = Field(description="Chain ID (e.g., 'solana')")


class PriceData(BaseModel):
    """Price data response schema."""

    price: float
    timestamp: int
    volume_24h: Optional[float]
    price_change_24h: Optional[float]


class TokenMetadata(BaseModel):
    """Token metadata response schema."""

    symbol: str
    name: str
    decimals: int
    total_supply: Optional[float]
    market_cap: Optional[float]


class DexInfo(BaseModel):
    """DEX information schema."""

    name: str
    liquidity: float
    volume_24h: float
    price: float


class TokenOverviewParams(BaseModel):
    """Parameters for token overview endpoint."""

    address: str = Field(description="Token address")
    chain: SupportedChain = Field(
        default=SupportedChain.SOLANA, description="Blockchain network"
    )


class TokenPriceInfo(BaseModel):
    """Price information in token overview."""

    value: float = Field(description="Current price value")
    change_24h: Optional[float] = Field(None, description="24h price change percentage")
    change_7d: Optional[float] = Field(None, description="7d price change percentage")
    change_14d: Optional[float] = Field(None, description="14d price change percentage")
    change_30d: Optional[float] = Field(None, description="30d price change percentage")


class TokenVolumeInfo(BaseModel):
    """Volume information in token overview."""

    value: float = Field(description="Volume value")
    change_24h: Optional[float] = Field(
        None, description="24h volume change percentage"
    )


class TokenExtensions(BaseModel):
    """Token extension information."""

    coingeckoId: Optional[str] = None
    serumV3Usdc: Optional[str] = None
    serumV3Usdt: Optional[str] = None
    website: Optional[str] = None
    telegram: Optional[str] = None
    twitter: Optional[str] = None
    description: Optional[str] = None
    discord: Optional[str] = None
    medium: Optional[str] = None


class TokenOverviewData(BaseModel):
    """Token overview data from API."""

    address: str
    decimals: int
    symbol: str
    name: str
    extensions: TokenExtensions
    logoURI: Optional[str] = None
    liquidity: float
    lastTradeUnixTime: int
    lastTradeHumanTime: str
    price: float
    history30mPrice: float
    priceChange30mPercent: float
    history1hPrice: float
    priceChange1hPercent: float
    history2hPrice: float
    priceChange2hPercent: float
    history4hPrice: float
    priceChange4hPercent: float
    history6hPrice: float
    priceChange6hPercent: float
    history8hPrice: float
    priceChange8hPercent: float
    history12hPrice: float
    priceChange12hPercent: float
    history24hPrice: float
    priceChange24hPercent: float
    uniqueWallet30m: int
    uniqueWalletHistory30m: int
    uniqueWallet30mChangePercent: float
    uniqueWallet1h: int
    uniqueWalletHistory1h: int
    uniqueWallet1hChangePercent: float
    uniqueWallet2h: int
    uniqueWalletHistory2h: int
    uniqueWallet2hChangePercent: float
    uniqueWallet4h: int
    uniqueWalletHistory4h: int
    uniqueWallet4hChangePercent: float
    uniqueWallet8h: int
    uniqueWalletHistory8h: int
    uniqueWallet8hChangePercent: float
    uniqueWallet24h: int
    uniqueWalletHistory24h: int
    uniqueWallet24hChangePercent: float
    supply: float
    mc: float
    circulatingSupply: float
    realMc: float
    holder: int
    trade30m: int
    tradeHistory30m: int
    trade30mChangePercent: float
    sell30m: int
    sellHistory30m: int
    sell30mChangePercent: float
    buy30m: int
    buyHistory30m: int
    buy30mChangePercent: float
    v30m: float
    v30mUSD: float
    vHistory30m: float
    vHistory30mUSD: float
    v30mChangePercent: float
    vBuy30m: float
    vBuy30mUSD: float
    vBuyHistory30m: float
    vBuyHistory30mUSD: float
    vBuy30mChangePercent: float
    vSell30m: float
    vSell30mUSD: float
    vSellHistory30m: float
    vSellHistory30mUSD: float
    vSell30mChangePercent: float
    trade1h: int
    tradeHistory1h: int
    trade1hChangePercent: float
    sell1h: int
    sellHistory1h: int
    sell1hChangePercent: float
    buy1h: int
    buyHistory1h: int
    buy1hChangePercent: float
    v1h: float
    v1hUSD: float
    vHistory1h: float
    vHistory1hUSD: float
    v1hChangePercent: float
    vBuy1h: float
    vBuy1hUSD: float
    vBuyHistory1h: float
    vBuyHistory1hUSD: float
    vBuy1hChangePercent: float
    vSell1h: float
    vSell1hUSD: float
    vSellHistory1h: float
    vSellHistory1hUSD: float
    vSell1hChangePercent: float
    trade2h: int
    tradeHistory2h: int
    trade2hChangePercent: float
    sell2h: int
    sellHistory2h: int
    sell2hChangePercent: float
    buy2h: int
    buyHistory2h: int
    buy2hChangePercent: float
    v2h: float
    v2hUSD: float
    vHistory2h: float
    vHistory2hUSD: float
    v2hChangePercent: float
    vBuy2h: float
    vBuy2hUSD: float
    vBuyHistory2h: float
    vBuyHistory2hUSD: float
    vBuy2hChangePercent: float
    vSell2h: float
    vSell2hUSD: float
    vSellHistory2h: float
    vSellHistory2hUSD: float
    vSell2hChangePercent: float
    trade4h: int
    tradeHistory4h: int
    trade4hChangePercent: float
    sell4h: int
    sellHistory4h: int
    sell4hChangePercent: float
    buy4h: int
    buyHistory4h: int
    buy4hChangePercent: float
    v4h: float
    v4hUSD: float
    vHistory4h: float
    vHistory4hUSD: float
    v4hChangePercent: float
    vBuy4h: float
    vBuy4hUSD: float
    vBuyHistory4h: float
    vBuyHistory4hUSD: float
    vBuy4hChangePercent: float
    vSell4h: float
    vSell4hUSD: float
    vSellHistory4h: float
    vSellHistory4hUSD: float
    vSell4hChangePercent: float
    trade8h: int
    tradeHistory8h: int
    trade8hChangePercent: float
    sell8h: int
    sellHistory8h: int
    sell8hChangePercent: float
    buy8h: int
    buyHistory8h: int
    buy8hChangePercent: float
    v8h: float
    v8hUSD: float
    vHistory8h: float
    vHistory8hUSD: float
    v8hChangePercent: float
    vBuy8h: float
    vBuy8hUSD: float
    vBuyHistory8h: float
    vBuyHistory8hUSD: float
    vBuy8hChangePercent: float
    vSell8h: float
    vSell8hUSD: float
    vSellHistory8h: float
    vSellHistory8hUSD: float
    vSell8hChangePercent: float
    trade24h: int
    tradeHistory24h: int
    trade24hChangePercent: float
    sell24h: int
    sellHistory24h: int
    sell24hChangePercent: float
    buy24h: int
    buyHistory24h: int
    buy24hChangePercent: float
    v24h: float
    v24hUSD: float
    vHistory24h: float
    vHistory24hUSD: float
    v24hChangePercent: float
    vBuy24h: float
    vBuy24hUSD: float
    vBuyHistory24h: float
    vBuyHistory24hUSD: float
    vBuy24hChangePercent: float
    vSell24h: float
    vSell24hUSD: float
    vSellHistory24h: float
    vSellHistory24hUSD: float
    vSell24hChangePercent: float
    numberMarkets: int


class TokenOverviewResponse(BaseModel):
    """Full response from token overview endpoint."""

    data: TokenOverviewData
    success: bool


class SearchParams(BaseModel):
    """Parameters for search request"""

    chain: SupportedChain = SupportedChain.SOLANA
    keyword: str
    target: str = "all"  # all, token, pair
    sort_by: str = "volume_24h_usd"
    sort_type: str = "desc"
    offset: int = 0
    limit: int = 20


class SearchSortBy(str, Enum):
    """Sort by options"""

    VOLUME_24H_USD = "volume_24h_usd"
    PRICE = "price"
    MARKET_CAP = "market_cap"
    UNIQUE_WALLET_24H = "unique_wallet_24h"
    SELL_24H = "sell_24h"
    BUY_24H = "buy_24h"
    TRADE_24H = "trade_24h"
    LIQUIDITY = "liquidity"
