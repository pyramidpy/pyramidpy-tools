from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class SolscanAuth(BaseModel):
    """Authentication schema for Solscan API."""

    api_key: Optional[str] = Field(
        None, description="Solscan API key for authenticated endpoints"
    )


class AccountTransferParams(BaseModel):
    """Parameters for account transfer history endpoint."""

    address: str = Field(..., description="Solana wallet address")
    activity_type: Optional[
        List[
            Literal[
                "ACTIVITY_SPL_TRANSFER",
                "ACTIVITY_SPL_BURN",
                "ACTIVITY_SPL_MINT",
                "ACTIVITY_SPL_CREATE_ACCOUNT",
            ]
        ]
    ] = None
    token_account: Optional[str] = Field(
        None, description="Filter transfers for a specific token account"
    )
    from_address: Optional[str] = Field(
        None, description="Filter transfer data with direction from an address"
    )
    to_address: Optional[str] = Field(
        None, description="Filter transfers from a specific address"
    )
    token: Optional[str] = Field(None, description="Filter by token address")
    amount: Optional[List[float]] = Field(None, description="Filter by amount range")
    block_time: Optional[List[int]] = Field(
        None, description="Filter by block time range (Unix timestamp)"
    )
    exclude_amount_zero: Optional[bool] = Field(
        None, description="Exclude transfers with zero amount"
    )
    flow: Optional[Literal["in", "out"]] = Field(
        None, description="Filter by transfer direction"
    )
    page: Optional[int] = Field(None, description="Page number for pagination")
    page_size: Optional[Literal[10, 20, 30, 40, 60, 100]] = Field(
        None, description="Number of items per page"
    )
    sort_by: Optional[Literal["block_time"]] = Field(None, description="Sort field")
    sort_order: Optional[Literal["asc", "desc"]] = Field(None, description="Sort order")
