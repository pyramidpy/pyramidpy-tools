from typing import Dict, Optional

import httpx

from .schemas import (
    BirdeyeAuth,
    HistoricalPriceParams,
    SearchParams,
    SupportedChain,
    TokenOverviewParams,
    TokenOverviewResponse,
    TokenPriceRequest,
    TransactionParams,
)


class BirdeyeAPI:
    """API client for interacting with the Birdeye API."""

    def __init__(self, auth: BirdeyeAuth):
        """Initialize the API client with authentication."""
        self.auth = auth
        self.base_url = "https://public-api.birdeye.so"
        self.client = httpx.AsyncClient()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        chain: SupportedChain = SupportedChain.SOLANA,
    ) -> Dict:
        """Make HTTP request to the API."""
        headers = {
            "X-API-KEY": self.auth.api_key,
            "accept": "application/json",
            "x-chain": chain.value,
            "content-type": "application/json",
        }
        url = f"{self.base_url}/{endpoint}"

        response = await self.client.request(
            method=method, url=url, params=params, json=json, headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def get_multi_price(self, request: TokenPriceRequest) -> Dict:
        """
        Get prices for multiple tokens.

        Args:
            request: TokenPriceRequest containing list of token addresses and chain

        Returns:
            Dict containing price data for requested tokens
        """
        response = await self._make_request(
            method="POST",
            endpoint="defi/multi_price",
            json={"list_address": ",".join(request.addresses)},
            chain=request.chain,
        )
        return response

    async def get_history_price(self, params: HistoricalPriceParams) -> Dict:
        """
        Get historical price data for a token.

        Args:
            params: Parameters for historical price request

        Returns:
            Dict containing historical price data
        """
        request_params = params.model_dump()
        chain = request_params.pop("chain")
        response = await self._make_request(
            method="GET",
            endpoint="defi/history_price",
            params=request_params,
            chain=chain,
        )
        return response

    async def get_token_transactions(self, params: TransactionParams) -> Dict:
        """
        Get token transactions.

        Args:
            params: Parameters for token transaction request

        Returns:
            Dict containing token transactions
        """
        request_params = params.model_dump()
        chain = request_params.pop("chain")
        response = await self._make_request(
            method="GET", endpoint="defi/txs/token", params=request_params, chain=chain
        )
        return response

    async def get_pair_transactions(self, params: TransactionParams) -> Dict:
        """
        Get pair transactions.

        Args:
            params: Parameters for pair transaction request

        Returns:
            Dict containing pair transactions
        """
        request_params = params.model_dump()
        chain = request_params.pop("chain")
        response = await self._make_request(
            method="GET", endpoint="defi/txs/pair", params=request_params, chain=chain
        )
        return response

    async def get_token_overview(
        self, params: TokenOverviewParams
    ) -> TokenOverviewResponse:
        """
        Get comprehensive overview data for a token.

        Args:
            params: Parameters for token overview request

        Returns:
            TokenOverviewResponse: Comprehensive token data including price, volume, and market metrics
        """
        request_params = params.model_dump()
        chain = request_params.pop("chain")
        response = await self._make_request(
            method="GET",
            endpoint="defi/token_overview",
            params=request_params,
            chain=chain,
        )
        return response["data"]

    async def search(self, params: SearchParams) -> Dict:
        """
        Search for tokens or pairs.

        Args:
            params: Parameters for search request

        Returns:
            Dict containing search results
        """
        request_params = params.model_dump()
        chain = request_params.pop("chain")
        response = await self._make_request(
            method="GET", endpoint="defi/v3/search", params=request_params, chain=chain
        )
        return response

    async def close(self):
        """Close the HTTP client session."""
        await self.client.aclose()
