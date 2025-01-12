from typing import Any, Dict, List, Optional

from controlflow.flows.flow import get_flow
from controlflow.tools.tools import tool

from pyramidpy_tools.toolkit import Toolkit

from .base import DuckDBAPI
from .schemas import QueryResult, S3Config, TableSchema


def get_duckdb_api() -> DuckDBAPI:
    """Get DuckDB API instance with S3 config from context if available"""
    flow = get_flow()
    if flow and flow.context:
        s3_config = S3Config(
            bucket_name=flow.context.get("s3_bucket_name"),
            access_key_id=flow.context.get("s3_access_key_id"),
            secret_access_key=flow.context.get("s3_secret_access_key"),
            region=flow.context.get("s3_region"),
        )
        return DuckDBAPI(s3_config=s3_config)
    return DuckDBAPI()


@tool(
    name="duckdb_execute_query",
    description="Execute a SQL query using DuckDB and return the results",
    include_return_description=False,
)
async def duckdb_execute_query(
    query: str, parameters: Optional[Dict[str, Any]] = None
) -> QueryResult:
    duckdb = get_duckdb_api()
    try:
        result = await duckdb.execute_query(query, parameters)
        duckdb.close()
        return result
    except Exception as e:
        duckdb.close()
        raise e


@tool(
    name="duckdb_list_tables",
    description="List all tables in the DuckDB database",
    include_return_description=False,
)
async def duckdb_list_tables(schema: str = "main") -> List[TableSchema]:
    duckdb = get_duckdb_api()
    try:
        result = await duckdb.list_tables(schema)
        duckdb.close()
        return result
    except Exception as e:
        duckdb.close()
        raise e


@tool(
    name="duckdb_create_table_from_s3",
    description="Create a new table in DuckDB from an S3 file",
    include_return_description=False,
)
async def duckdb_create_table_from_s3(
    table_name: str,
    s3_path: str,
    file_format: str = "parquet",
) -> TableSchema:
    duckdb = get_duckdb_api()
    try:
        result = await duckdb.create_table_from_s3(table_name, s3_path, file_format)
        duckdb.close()
        return result
    except Exception as e:
        duckdb.close()
        raise e


@tool(
    name="duckdb_export_to_s3",
    description="Export query results to an S3 file",
    include_return_description=False,
)
async def duckdb_export_to_s3(
    query: str,
    s3_path: str,
    file_format: str = "parquet",
    parameters: Optional[Dict[str, Any]] = None,
) -> str:
    duckdb = get_duckdb_api()
    try:
        result = await duckdb.export_to_s3(query, s3_path, file_format, parameters)
        duckdb.close()
        return result
    except Exception as e:
        duckdb.close()
        raise e


duckdb_toolkit = Toolkit.create_toolkit(
    id="duckdb_toolkit",
    tools=[
        duckdb_execute_query,
        duckdb_list_tables,
        duckdb_create_table_from_s3,
        duckdb_export_to_s3,
    ],
    auth_key="s3_access_key_id",
    name="DuckDB Toolkit",
    description="Tools for working with DuckDB and S3 data",
)
