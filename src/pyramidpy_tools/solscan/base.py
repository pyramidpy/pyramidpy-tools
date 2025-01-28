from typing import Any, Dict, Optional

import aiohttp

from .schemas import AccountTransferParams, SolscanAuth


class SolscanAPI:
    """Solscan API client for interacting with Solana blockchain data."""

    BASE_URL = "https://public-api.solscan.io"
    PRO_BASE_URL = "https://pro-api.solscan.io/v2.0"

    def __init__(self, auth: Optional[SolscanAuth] = None):
        self.auth = auth
        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        is_pro: bool = False,
    ) -> dict:
        """Make a request to the Solscan API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            is_pro: Whether to use pro API endpoint

        Returns:
            API response as dictionary
        """
        base_url = self.PRO_BASE_URL if is_pro else self.BASE_URL
        url = f"{base_url}{endpoint}"

        headers = {}
        if is_pro and self.auth and self.auth.api_key:
            headers["token"] = self.auth.api_key

        async with self.session.request(
            method, url, params=params, headers=headers
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def get_chain_info(self) -> dict:
        """Get Solana chain information."""
        return await self._request("GET", "/chaininfo")

    async def get_account_transactions(
        self, address: str, before: Optional[int] = None, limit: int = 10
    ) -> dict:
        """Get transactions for a Solana account address.

        Args:
            address: Account address
            before: Get transactions before this signature
            limit: Number of transactions to return (max 50)
        """
        params = {"account": address, "limit": min(limit, 50)}
        if before:
            params["before"] = before
        return await self._request("GET", "/account/transactions", params)

    async def get_token_holders(
        self, token: str, offset: int = 0, limit: int = 10
    ) -> dict:
        """Get token holders for a Solana SPL token.

        Args:
            token: Token mint address
            offset: Pagination offset
            limit: Number of holders to return (max 50)
        """
        params = {"tokenAddress": token, "offset": offset, "limit": min(limit, 50)}
        return await self._request("GET", "/token/holders", params)

    async def get_token_meta(self, token: str) -> dict:
        """Get metadata for a Solana SPL token.

        Args:
            token: Token mint address
        """
        params = {"tokenAddress": token}
        return await self._request("GET", "/token/meta", params)

    async def get_account_tokens(self, address: str) -> dict:
        """Get token balances for a Solana account.

        Args:
            address: Account address
        """
        params = {"account": address}
        return await self._request("GET", "/account/tokens", params)

    async def get_account_stake(self, address: str) -> dict:
        """Get stake accounts info for a Solana account.

        Args:
            address: Account address
        """
        params = {"account": address}
        return await self._request("GET", "/account/stake", params)

    async def get_account_transfer_history(self, params: AccountTransferParams) -> dict:
        """Get transfer history for a Solana account (Pro API).

        Args:
            params: Account transfer parameters
        """
        # Convert params to dict and remove None values
        query_params = {k: v for k, v in params.model_dump().items() if v is not None}
        return await self._request(
            "GET", "/account/transfer", query_params, is_pro=True
        )
