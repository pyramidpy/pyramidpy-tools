from typing import List, Optional

from apps.common.schema import BaseSchemaConfig
from ninja import Schema
from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


class CreateDatabaseInput(BaseModel):
    name: str
    group: str
    seed: Optional[dict] = None
    size_limit: Optional[str] = None
    is_schema: Optional[bool] = None
    schema: Optional[str] = None


class CreateDatabaseOutput(BaseModel):
    db_id: str
    hostname: str
    name: str


class Database(BaseModel):
    name: str
    db_id: str
    hostname: str
    block_reads: bool
    block_writes: bool
    allow_attach: bool
    regions: List[str]
    primary_region: str
    type: str | None = None
    version: str | None = None
    group: str | None = None
    is_schema: bool | None = None
    schema: str | None = None
    sleeping: bool | None = None


class TursoDatabase(Schema):
    name: str
    db_id: str
    hostname: str
    block_reads: bool
    block_writes: bool
    allow_attach: bool
    regions: List[str]
    primary_region: str

    # type: str | None = None
    # version: str | None = None
    # group: str | None = None
    # is_schema: bool
    # schema: str
    # sleeping: bool
    class Config(BaseSchemaConfig):
        extra = "allow"


class DeleteDatabasesInput(BaseModel):
    db_ids: List[str]


class DatabaseStatsOutput(BaseModel):
    query: str
    rows_read: int
    rows_written: int


class DatabaseUsageObject(BaseModel):
    rows_read: int
    rows_written: int
    storage_bytes: int


class DatabaseUsageOutput(BaseModel):
    uuid: str
    instances: List[dict]
    total: DatabaseUsageObject


class DatabaseConfigurationInput(BaseModel):
    name: str
    group: str
    seed: Optional[dict] = None
    size_limit: Optional[str] = None
    is_schema: Optional[bool] = None
    schema: Optional[str] = None


class DatabaseConfigurationResponse(BaseModel):
    db_id: str
    hostname: str
    name: str
