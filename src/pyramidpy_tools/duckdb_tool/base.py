from typing import Any, Dict, List, Optional

import duckdb
from pyramidpy_tools.settings import settings

from .schemas import QueryResult, S3Config, TableSchema


class DuckDBAPI:
    def __init__(
        self,
        s3_config: Optional[S3Config] = None,
    ):
        self.s3_config = s3_config or S3Config(
            bucket_name=settings.storage.s3_bucket_name,
            access_key_id=settings.storage.s3_access_key_id,
            secret_access_key=settings.storage.s3_secret_access_key,
            region=settings.storage.s3_region,
        )
        self.conn = self._create_connection()

    def _create_connection(self) -> duckdb.DuckDBPyConnection:
        """Create a DuckDB connection with S3 configuration"""
        conn = duckdb.connect(database=":memory:")

        if self.s3_config.access_key_id and self.s3_config.secret_access_key:
            conn.execute(f"""
                SET s3_region='{self.s3_config.region}';
                SET s3_access_key_id='{self.s3_config.access_key_id}';
                SET s3_secret_access_key='{self.s3_config.secret_access_key}';
            """)

        return conn

    async def execute_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> QueryResult:
        """Execute a SQL query and return the results"""
        try:
            if parameters:
                result = self.conn.execute(query, parameters).fetchdf()
            else:
                result = self.conn.execute(query).fetchdf()

            return QueryResult(
                columns=list(result.columns), data=result.values.tolist()
            )
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")

    async def list_tables(self, schema: str = "main") -> List[TableSchema]:
        """List all tables in the specified schema"""
        query = f"""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = '{schema}'
            ORDER BY table_name, ordinal_position
        """

        result = self.conn.execute(query).fetchdf()

        tables = {}
        for _, row in result.iterrows():
            table_name = row["table_name"]
            if table_name not in tables:
                tables[table_name] = []

            tables[table_name].append(
                {"name": row["column_name"], "type": row["data_type"]}
            )

        return [
            TableSchema(name=name, columns=columns) for name, columns in tables.items()
        ]

    async def create_table_from_s3(
        self, table_name: str, s3_path: str, file_format: str = "parquet"
    ) -> TableSchema:
        """Create a table from an S3 file"""
        bucket = self.s3_config.bucket_name
        s3_url = f"s3://{bucket}/{s3_path}"

        query = f"""
            CREATE TABLE {table_name} AS 
            SELECT * FROM read_{file_format}('{s3_url}')
        """

        try:
            self.conn.execute(query)
            tables = await self.list_tables()
            return next(t for t in tables if t.name == table_name)
        except Exception as e:
            raise Exception(f"Failed to create table from S3: {str(e)}")

    async def export_to_s3(
        self,
        query: str,
        s3_path: str,
        file_format: str = "parquet",
        parameters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Export query results to S3"""
        bucket = self.s3_config.bucket_name
        s3_url = f"s3://{bucket}/{s3_path}"

        export_query = f"""
            COPY ({query}) TO '{s3_url}' (FORMAT '{file_format}')
        """

        try:
            if parameters:
                self.conn.execute(export_query, parameters)
            else:
                self.conn.execute(export_query)
            return s3_url
        except Exception as e:
            raise Exception(f"Failed to export to S3: {str(e)}")

    def close(self):
        """Close the DuckDB connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
