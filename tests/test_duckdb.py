from unittest.mock import AsyncMock, Mock, call, patch

import duckdb
import pandas as pd
import pytest
from controlflow.tools.tools import Tool

from pyramidpy_tools.duckdb.base import DuckDBAPI
from pyramidpy_tools.duckdb.schemas import QueryResult, S3Config, TableSchema
from pyramidpy_tools.duckdb.tools import (
    duckdb_create_table_from_s3,
    duckdb_execute_query,
    duckdb_export_to_s3,
    duckdb_list_tables,
    duckdb_toolkit,
)


def normalize_sql(sql: str) -> str:
    """Normalize SQL string by removing extra whitespace and newlines"""
    return " ".join(sql.split())


@pytest.fixture
def mock_duckdb_connection():
    with patch("duckdb.connect") as mock_connect:
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        yield mock_conn


@pytest.fixture
def mock_s3_config():
    return S3Config(
        bucket_name="test-bucket",
        access_key_id="test-key",
        secret_access_key="test-secret",
        region="test-region",
    )


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        {"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]}
    )


class TestDuckDBAPI:
    def test_init_with_s3_config(self, mock_duckdb_connection, mock_s3_config):
        api = DuckDBAPI(s3_config=mock_s3_config)
        assert api.s3_config == mock_s3_config

        expected_sql = normalize_sql(f"""
            SET s3_region='{mock_s3_config.region}';
            SET s3_access_key_id='{mock_s3_config.access_key_id}';
            SET s3_secret_access_key='{mock_s3_config.secret_access_key}';
        """)

        actual_calls = [
            normalize_sql(call.args[0])
            for call in mock_duckdb_connection.execute.call_args_list
        ]
        assert expected_sql in actual_calls

    @pytest.mark.asyncio
    async def test_execute_query(self, mock_duckdb_connection, sample_dataframe):
        mock_duckdb_connection.execute.return_value.fetchdf.return_value = (
            sample_dataframe
        )

        api = DuckDBAPI(s3_config=Mock())
        result = await api.execute_query("SELECT * FROM test_table")

        assert isinstance(result, QueryResult)
        assert result.columns == ["id", "name", "age"]
        assert len(result.data) == 3
        assert result.data[0] == [1, "Alice", 25]

    @pytest.mark.asyncio
    async def test_list_tables(self, mock_duckdb_connection):
        schema_df = pd.DataFrame(
            {
                "table_name": ["table1", "table1", "table2"],
                "column_name": ["id", "name", "value"],
                "data_type": ["INTEGER", "VARCHAR", "FLOAT"],
            }
        )
        mock_duckdb_connection.execute.return_value.fetchdf.return_value = schema_df

        api = DuckDBAPI(s3_config=Mock())
        result = await api.list_tables()

        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], TableSchema)
        assert result[0].name == "table1"
        assert len(result[0].columns) == 2

    @pytest.mark.asyncio
    async def test_create_table_from_s3(self, mock_duckdb_connection, mock_s3_config):
        schema_df = pd.DataFrame(
            {
                "table_name": ["new_table"],
                "column_name": ["id"],
                "data_type": ["INTEGER"],
            }
        )
        mock_duckdb_connection.execute.return_value.fetchdf.return_value = schema_df

        api = DuckDBAPI(s3_config=mock_s3_config)
        result = await api.create_table_from_s3("new_table", "data/file.parquet")

        assert isinstance(result, TableSchema)
        assert result.name == "new_table"

        expected_sql = normalize_sql("""
            CREATE TABLE new_table AS 
            SELECT * FROM read_parquet('s3://test-bucket/data/file.parquet')
        """)

        actual_calls = [
            normalize_sql(call.args[0])
            for call in mock_duckdb_connection.execute.call_args_list
        ]
        assert expected_sql in actual_calls

    @pytest.mark.asyncio
    async def test_export_to_s3(self, mock_duckdb_connection, mock_s3_config):
        api = DuckDBAPI(s3_config=mock_s3_config)
        result = await api.export_to_s3(
            "SELECT * FROM test_table", "exports/data.parquet"
        )

        assert result == "s3://test-bucket/exports/data.parquet"

        expected_sql = normalize_sql("""
            COPY (SELECT * FROM test_table) 
            TO 's3://test-bucket/exports/data.parquet' (FORMAT 'parquet')
        """)

        actual_calls = [
            normalize_sql(call.args[0])
            for call in mock_duckdb_connection.execute.call_args_list
        ]
        assert expected_sql in actual_calls


@pytest.mark.asyncio
class TestDuckDBTools:
    @pytest.fixture
    def mock_api(self):
        with patch("pyramidpy_tools.tools.duckdb.tools.get_duckdb_api") as mock:
            mock_instance = AsyncMock(spec=DuckDBAPI)
            mock.return_value = mock_instance
            yield mock_instance

    def test_tools_are_properly_configured(self):
        """Test that all tools are properly configured in the toolkit"""
        assert isinstance(duckdb_toolkit.tools[0], Tool)
        for tool in duckdb_toolkit.tools:
            assert isinstance(tool, Tool)
            assert tool.name.startswith("duckdb_")
            assert tool.description
            assert callable(tool.fn)

    async def test_execute_query_tool(self, mock_api):
        query = "SELECT * FROM test"
        expected_result = QueryResult(columns=["id"], data=[[1]])
        mock_api.execute_query.return_value = expected_result

        # Get the tool from the toolkit
        execute_query_tool = next(
            t for t in duckdb_toolkit.tools if t.name == "duckdb_execute_query"
        )

        # Test using tool.run
        result = await execute_query_tool.run_async({"query": query})
        assert result == expected_result
        mock_api.execute_query.assert_called_once_with(query, None)
        mock_api.close.assert_called_once()

    async def test_list_tables_tool(self, mock_api):
        expected_tables = [
            TableSchema(name="test", columns=[{"name": "id", "type": "INTEGER"}])
        ]
        mock_api.list_tables.return_value = expected_tables

        # Get the tool from the toolkit
        list_tables_tool = next(
            t for t in duckdb_toolkit.tools if t.name == "duckdb_list_tables"
        )

        # Test using tool.run
        result = await list_tables_tool.run_async({"schema": "main"})
        assert result == expected_tables
        mock_api.list_tables.assert_called_once_with("main")
        mock_api.close.assert_called_once()

    async def test_create_table_from_s3_tool(self, mock_api):
        expected_schema = TableSchema(
            name="new_table", columns=[{"name": "id", "type": "INTEGER"}]
        )
        mock_api.create_table_from_s3.return_value = expected_schema

        # Get the tool from the toolkit
        create_table_tool = next(
            t for t in duckdb_toolkit.tools if t.name == "duckdb_create_table_from_s3"
        )

        # Test using tool.run
        result = await create_table_tool.run_async(
            {
                "table_name": "new_table",
                "s3_path": "data/file.parquet",
                "file_format": "parquet",
            }
        )
        assert result == expected_schema
        mock_api.create_table_from_s3.assert_called_once_with(
            "new_table", "data/file.parquet", "parquet"
        )
        mock_api.close.assert_called_once()

    async def test_export_to_s3_tool(self, mock_api):
        expected_url = "s3://bucket/path/file.parquet"
        mock_api.export_to_s3.return_value = expected_url

        # Get the tool from the toolkit
        export_tool = next(
            t for t in duckdb_toolkit.tools if t.name == "duckdb_export_to_s3"
        )

        # Test using tool.run
        result = await export_tool.run_async(
            {
                "query": "SELECT * FROM test",
                "s3_path": "path/file.parquet",
                "file_format": "parquet",
            }
        )
        assert result == expected_url
        mock_api.export_to_s3.assert_called_once_with(
            "SELECT * FROM test", "path/file.parquet", "parquet", None
        )
        mock_api.close.assert_called_once()

    async def test_error_handling_in_tool(self, mock_api):
        mock_api.execute_query.side_effect = Exception("Test error")

        # Get the tool from the toolkit
        execute_query_tool = next(
            t for t in duckdb_toolkit.tools if t.name == "duckdb_execute_query"
        )

        with pytest.raises(Exception) as exc_info:
            await execute_query_tool.run_async({"query": "SELECT * FROM test"})

        assert str(exc_info.value) == "Test error"
        mock_api.close.assert_called_once()
