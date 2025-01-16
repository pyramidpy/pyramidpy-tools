from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class QueryResult(BaseModel):
    columns: List[str]
    data: List[List[Any]]


class TableSchema(BaseModel):
    name: str
    columns: List[Dict[str, str]]


class S3Config(BaseModel):
    bucket_name: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    region: Optional[str] = None


class QueryOptions(BaseModel):
    query: str
    parameters: Optional[Dict[str, Any]] = None
