import asyncio
import aiohttp
from datetime import datetime
import logging
from typing import Optional

from .schema import Token, TokenInsights
import marvin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@marvin.fn(model_kwargs={"model": "gpt-4o-mini"})
def gen_insights(cg_data: dict) -> str:
    """Generate insights based on CoinGecko the provided token data"""


class TokenDataFetcher:
    def __init__(self):
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        self.dexscreener_api = "https://api.dexscreener.com/latest/dex"

    async def fetch_dexscreener(self, contract_address: str) -> dict:
        """Fetch token data from DexScreener"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.dexscreener_api}/tokens/{contract_address}"
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
            except Exception as e:
                logger.error(f"DexScreener API error: {e}")
        return None

    async def fetch_coingecko(self, contract_address: str) -> dict:
        """Fetch token data from CoinGecko"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.coingecko_api}/coins/ethereum/contract/{contract_address}"
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
            except Exception as e:
                logger.error(f"CoinGecko API error: {e}")
        return None

    def format_number(self, num: float) -> str:
        """Format numbers to match frontend display"""
        if num >= 1_000_000:
            return f"{num / 1_000_000:.2f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.2f}K"
        return f"{num:.2f}"

    async def combine_data(self, contract_address: str) -> Optional[Token]:
        """Fetch and combine data from both sources"""
        dex_data = await self.fetch_dexscreener(contract_address)
        cg_data = await self.fetch_coingecko(contract_address)

        if not dex_data and not cg_data:
            logger.error(f"No data available for {contract_address}")
            return None

        try:
            # Prioritize DexScreener for real-time DEX data
            if dex_data and dex_data.get("pairs"):
                pair = dex_data["pairs"][0]  # Get most liquid pair
                price = float(pair.get("priceUsd", 0))
                liquidity = float(pair.get("liquidity", {}).get("usd", 0))
                volume_24h = float(pair.get("volume", {}).get("h24", 0))
                symbol = pair.get("baseToken", {}).get("symbol", "")
            else:
                # Fallback to CoinGecko data
                price = (
                    cg_data.get("market_data", {})
                    .get("current_price", {})
                    .get("usd", 0)
                )
                liquidity = cg_data.get("market_data", {}).get("total_liquidity", 0)
                volume_24h = (
                    cg_data.get("market_data", {}).get("total_volume", {}).get("usd", 0)
                )
                symbol = cg_data.get("symbol", "").upper()

            # Calculate market cap
            supply = (
                float(cg_data.get("market_data", {}).get("total_supply", 0))
                if cg_data
                else 0
            )
            market_cap = price * supply if supply else 0

            # Get GitHub data if available
            github_data = cg_data.get("developer_data", {}) if cg_data else {}

            # Get social data
            social_data = cg_data.get("community_data", {}) if cg_data else {}

            return Token(
                symbol=symbol,
                supply=self.format_number(supply),
                liq=f"${self.format_number(liquidity)}",
                mc=f"${self.format_number(market_cap)}",
                volume=self.format_number(volume_24h),
                price=self.format_number(price),
                time=datetime.now().strftime("%I:%M %p"),
                contract_address=contract_address,
                insights=TokenInsights(
                    summary=f"{'Bullish' if volume_24h > 0 else 'Neutral'} momentum with "
                    f"${self.format_number(volume_24h)} 24h volume",
                    catalysts=self._generate_catalysts(cg_data) if cg_data else None,
                    twitter=self._generate_twitter_insights(social_data),
                    github=self._generate_github_insights(github_data),
                ),
            )
        except Exception as e:
            logger.error(f"Error processing data for {contract_address}: {e}")
            return None

    def _generate_catalysts(self, cg_data: dict) -> str:
        """Generate catalysts based on CoinGecko data"""
        catalysts = []
        if (
            cg_data.get("market_data", {})
            .get("ath_change_percentage", {})
            .get("usd", 0)
            > -20
        ):
            catalysts.append("• Near all-time high price levels")
        if cg_data.get("market_data", {}).get("price_change_percentage_24h", 0) > 5:
            catalysts.append("• Strong 24h price performance")
        if cg_data.get("community_score", 0) > 70:
            catalysts.append("• High community engagement")
        return "\n".join(catalysts) if catalysts else "No significant catalysts"

    def _generate_twitter_insights(self, social_data: dict) -> str:
        """Generate Twitter insights from social data"""
        followers = social_data.get("twitter_followers", 0)
        status_updates = social_data.get("twitter_status_updates", 0)

        insights = []
        if followers > 0:
            insights.append(f"• {self.format_number(followers)} Twitter followers")
        if status_updates > 0:
            insights.append(f"• {status_updates} recent updates")

        return "\n".join(insights) if insights else "No Twitter data available"

    def _generate_github_insights(self, github_data: dict) -> str:
        """Generate GitHub insights from developer data"""
        insights = []

        commits = github_data.get("commit_count_4_weeks", 0)
        if commits > 0:
            insights.append(f"• {commits} commits in last 4 weeks")

        contributors = github_data.get("contributors", 0)
        if contributors > 0:
            insights.append(f"• {contributors} contributors")

        stars = github_data.get("stars", 0)
        if stars > 0:
            insights.append(f"• {stars} GitHub stars")

        return "\n".join(insights) if insights else "No GitHub activity data"


async def run_update_job():
    """Main job to update token data"""
    fetcher = TokenDataFetcher()

    # Your list of contract addresses
    contract_addresses = []

    while True:
        for address in contract_addresses:
            try:
                token_data = await fetcher.combine_data(address)
                if token_data:
                    logger.info(f"Updated data for {address}")
            except Exception as e:
                logger.error(f"Error updating {address}: {e}")

        await asyncio.sleep(300)  # 5 minutes


if __name__ == "__main__":
    asyncio.run(run_update_job())
