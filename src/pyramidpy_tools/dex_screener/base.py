import httpx
from .schemas import DexScreenerResult, PairInfo


class DexScreenerAPI:
    """Wrapper for DEX Screener API"""

    base_url = "https://api.dexscreener.com/latest"

    def search_pairs(self, search_query: str) -> DexScreenerResult:
        """Search for pairs by token address, symbol, or name"""
        try:
            url = f"{self.base_url}/dex/search?q={search_query}"
            response = httpx.get(url, timeout=30)
            if not response.ok:
                return DexScreenerResult(
                    error=f"HTTP error {response.status_code}", success=False
                )
            data = response.json().get("pairs", [])
            return DexScreenerResult(
                data=[PairInfo(**pair) for pair in data], success=True
            )
        except Exception as e:
            return DexScreenerResult(error=str(e), success=False)

    def get_pair(self, pair_address: str, chain_id: str) -> DexScreenerResult:
        """Get detailed information about a specific trading pair"""
        try:
            url = f"{self.base_url}/dex/pairs/{chain_id}/{pair_address}"
            response = httpx.get(url, timeout=30)
            if not response.ok:
                return DexScreenerResult(
                    error=f"HTTP error {response.status_code}", success=False
                )
            data = response.json().get("pair")
            if not data:
                return DexScreenerResult(error="Pair not found", success=False)
            return DexScreenerResult(data=PairInfo(**data), success=True)
        except Exception as e:
            return DexScreenerResult(error=str(e), success=False)
