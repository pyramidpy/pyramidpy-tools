from typing import Optional, Tuple, Dict, Any

from fastapi.logger import logger
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey  # type: ignore
from solders.keypair import Keypair  # type: ignore
from solana.rpc.async_api import AsyncClient
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.async_client import AsyncToken

from pyramidpy_tools.settings import settings
from .schemas import (
    BalanceResponse,
    TokenDeployResponse,
    BurnAndCloseResponse,
    TradeResponse,
    MoonshotTradeResponse,
    CreateDLMMPoolResponse,
    PriceResponse,
    TokenDataResponse,
    SolanaResponse
)

LAMPORTS_PER_SOL = 1_000_000_000

class SolanaAPI:
    def __init__(
        self,
        rpc_url: Optional[str] = None,
        keypair: Optional[Keypair] = None,
    ):
        self.rpc_url = rpc_url or settings.tool_provider.solana_rpc_url.get_secret_value()
        self.connection = AsyncClient(self.rpc_url, commitment=Confirmed)
        self.keypair = keypair or Keypair()
        self.wallet_address = self.keypair.pubkey()

    async def get_balance(
        self, token_address: Optional[str] = None
    ) -> BalanceResponse:
        """Get the balance of SOL or an SPL token for the wallet."""
        try:
            if not token_address:
                response = await self.connection.get_balance(
                    self.wallet_address, commitment=Confirmed
                )
                return BalanceResponse(
                    success=True,
                    balance=response.value / LAMPORTS_PER_SOL
                )

            token_pubkey = Pubkey.from_string(token_address)
            token = AsyncToken(
                self.connection,
                token_pubkey,
                TOKEN_PROGRAM_ID,
                self.keypair
            )
            
            response = await token.get_balance(self.wallet_address)
            return BalanceResponse(
                success=True,
                balance=response.value,
                token_address=token_address,
                decimals=token.decimals
            )

        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}")
            return BalanceResponse(
                success=False,
                error=str(e),
                balance=0
            )

    async def deploy_token(
        self,
        name: str,
        symbol: str,
        decimals: int,
        initial_supply: float
    ) -> TokenDeployResponse:
        """Deploy a new SPL token with initial supply."""
        try:
            # Create mint account
            mint_keypair = Keypair()
            token = await AsyncToken.create_mint(
                self.connection,
                self.keypair,
                self.wallet_address,
                decimals,
                mint_keypair
            )

            # Create token account
            token_account = await token.create_account(self.wallet_address)
            
            # Mint initial supply
            mint_tx = await token.mint_to(
                token_account,
                self.wallet_address,
                int(initial_supply * (10 ** decimals))
            )

            return TokenDeployResponse(
                success=True,
                mint_address=str(mint_keypair.pubkey()),
                token_account=str(token_account),
                transaction_signature=mint_tx.value
            )

        except Exception as e:
            logger.error(f"Failed to deploy token: {str(e)}")
            return TokenDeployResponse(
                success=False,
                error=str(e),
                mint_address="",
                token_account="",
                transaction_signature=""
            )

    async def burn_and_close(
        self,
        token_address: str,
        token_account: str
    ) -> BurnAndCloseResponse:
        """Burn all tokens and close the token account."""
        try:
            token_pubkey = Pubkey.from_string(token_address)
            token = AsyncToken(
                self.connection,
                token_pubkey,
                TOKEN_PROGRAM_ID,
                self.keypair
            )
            
            # Get current balance
            balance = await token.get_balance(Pubkey.from_string(token_account))
            
            # Burn tokens if any exist
            if balance.value > 0:
                await token.burn(
                    Pubkey.from_string(token_account),
                    self.wallet_address,
                    balance.value
                )
            
            # Close account
            close_tx = await token.close_account(
                Pubkey.from_string(token_account),
                self.wallet_address,
                self.wallet_address
            )

            return BurnAndCloseResponse(
                success=True,
                transaction_signature=close_tx.value
            )

        except Exception as e:
            logger.error(f"Failed to burn and close: {str(e)}")
            return BurnAndCloseResponse(
                success=False,
                error=str(e),
                transaction_signature=""
            )

    async def trade_with_raydium(
        self,
        pair_address: str,
        amount: float,
        is_buy: bool = True,
        slippage: int = 5,
        percentage: Optional[int] = None
    ) -> TradeResponse:
        """Execute a trade on Raydium DEX."""
        from .utils.raydium import RaydiumManager
        try:
            if is_buy:
                success = await RaydiumManager.buy_with_raydium(
                    self, pair_address, amount, slippage
                )
            else:
                success = await RaydiumManager.sell_with_raydium(
                    self, pair_address, percentage or 100, slippage
                )
            
            return TradeResponse(
                success=success,
                transaction_signature="",  # TODO: Get actual signature
                amount_in=amount,
                amount_out=0  # TODO: Calculate actual amount out
            )
        except Exception as e:
            logger.error(f"Failed to trade on Raydium: {str(e)}")
            return TradeResponse(
                success=False,
                error=str(e),
                transaction_signature="",
                amount_in=0,
                amount_out=0
            )

    async def trade_with_moonshot(
        self,
        mint_address: str,
        is_buy: bool = True,
        collateral_amount: Optional[float] = 0.01,
        token_amount: Optional[float] = None,
        slippage_bps: int = 500
    ) -> MoonshotTradeResponse:
        """Execute a trade on Moonshot DEX."""
        from .utils.moonshot import MoonshotManager
        try:
            if is_buy:
                await MoonshotManager.buy(
                    self, mint_address, collateral_amount, slippage_bps
                )
            else:
                await MoonshotManager.sell(
                    self, mint_address, token_amount, slippage_bps
                )
            
            return MoonshotTradeResponse(
                success=True,
                transaction_signature="",  # TODO: Get actual signature
                amount=collateral_amount or token_amount or 0
            )
        except Exception as e:
            logger.error(f"Failed to trade on Moonshot: {str(e)}")
            return MoonshotTradeResponse(
                success=False,
                error=str(e),
                transaction_signature="",
                amount=0
            )

    async def create_meteora_pool(
        self,
        token_a: str,
        token_b: str,
        amount_a: float,
        amount_b: float,
        fee_rate: float
    ) -> CreateDLMMPoolResponse:
        """Create a Meteora DLMM pool."""
        from .utils.meteora import MeteoraManager
        try:
            result = await MeteoraManager.create_pool(
                self, token_a, token_b, amount_a, amount_b, fee_rate
            )
            return CreateDLMMPoolResponse(
                success=True,
                pool_address=result["pool_address"],
                transaction_signature=result["signature"]
            )
        except Exception as e:
            logger.error(f"Failed to create Meteora pool: {str(e)}")
            return CreateDLMMPoolResponse(
                success=False,
                error=str(e),
                pool_address="",
                transaction_signature=""
            )

    async def get_token_price(
        self,
        token_address: str,
        vs_currency: str = "usd"
    ) -> PriceResponse:
        """Get token price from various sources."""
        from .utils.price import get_token_price
        try:
            price_data = await get_token_price(token_address, vs_currency)
            return PriceResponse(
                success=True,
                price=price_data["price"],
                vs_currency=vs_currency,
                timestamp=price_data["timestamp"]
            )
        except Exception as e:
            logger.error(f"Failed to get token price: {str(e)}")
            return PriceResponse(
                success=False,
                error=str(e),
                price=0,
                vs_currency=vs_currency,
                timestamp=0
            )

    async def get_token_data(
        self,
        token_address: str
    ) -> TokenDataResponse:
        """Get detailed token data."""
        from .utils.token_data import get_token_data
        try:
            data = await get_token_data(token_address)
            return TokenDataResponse(
                success=True,
                **data
            )
        except Exception as e:
            logger.error(f"Failed to get token data: {str(e)}")
            return TokenDataResponse(
                success=False,
                error=str(e),
                name="",
                symbol="",
                decimals=0,
                total_supply=0
            ) 