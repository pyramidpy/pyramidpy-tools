from typing import Optional

from pydantic import BaseModel


class TokenInsights(BaseModel):
    summary: Optional[str] = None
    catalysts: Optional[str] = None
    twitter: Optional[str] = None
    github: Optional[str] = None


class Token(BaseModel):
    symbol: str
    supply: str
    liq: str
    mc: str
    volume: str
    price: str
    time: str
    contract_address: str
    insights: Optional[TokenInsights] = None

    class Config:
        from_attributes = True
