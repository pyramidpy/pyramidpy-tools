import traceback
from typing import Any, Dict, List, Literal

from controlflow.flows import get_flow
from controlflow.tools.tools import tool
from pydantic import BaseModel, Field, model_validator

from pyramidpy_tools.toolkit import Toolkit

from .base import SQLDatabase


class Query(BaseModel):
    query: str = Field(description="The SQL query to execute")
    time_series_query: str | None = Field(
        description="The SQL query to execute for time series data if possible"
    )
    type: Literal["query"] = Field(
        description="The type of the result", default="query"
    )
    title: str = Field(description="Title to be used in charts and reports")
    description: str = Field(description="Description to be used in charts and reports")
    chart_type: Literal["bar", "line", "pie", "scatter", "area"] = Field(
        description="Type of chart to be used in reports"
    )
    x_axis: str = Field(description="X axis to be used in charts")
    y_axis: str = Field(description="Y axis to be used in charts")
    categories: List[str] = Field(
        description="Categories to be used in chart. Usually a date field."
    )


class QueryResult(BaseModel):
    data: List[Dict[str, Any]] = Field(description="The result data of the query")
    headers: List[str] = Field(description="The column headers of the result")
    message: str = Field(description="Additional message about the query execution")
    type: Literal["query_result"] = Field(
        description="The type of the result", default="query_result"
    )
    metadata: Dict[str, Any] | None = Field(
        description="Metadata about the query result", default=None
    )


class TableList(BaseModel):
    tables: List[str] = Field(description="List of available tables in the database")
    type: Literal["table_list"] = Field(
        description="The type of the result", default="table_list"
    )


class TableDescription(BaseModel):
    description: List[str] | str = Field(
        description="CREATE TABLE statements for the specified tables"
    )
    type: Literal["table_description"] = Field(
        description="The type of the result", default="table_description"
    )


class TableCreateColumn(BaseModel):
    table_name: str | None = None
    name: str = Field(description="The name of the column")
    column_type: str = Field(description="The type of the column")
    is_primary_key: bool = Field(
        description="Whether the column is a primary key", default=False
    )
    auto_increment: bool = Field(
        description="Whether the column is an auto increment column", default=False
    )
    type: Literal["table_create_column"] = Field(
        description="The type of the result", default="table_create_column"
    )


class TableCreate(BaseModel):
    table_name: str = Field(
        description="The name of the table to create.Include at a minimum a primary key column named id"
    )
    columns: List[TableCreateColumn] | List[str] = Field(
        description="The columns of the table"
    )
    type: Literal["table_create"] = Field(
        description="The type of the result", default="table_create"
    )

    @model_validator(mode="after")
    def validate_columns(self):
        """Add primary key and auto increment to columns if not specified"""
        has_primary_key = False
        for column in self.columns:
            if isinstance(column, TableCreateColumn):
                if column.is_primary_key:
                    has_primary_key = True
                    if not column.auto_increment:
                        column.auto_increment = True

        if not has_primary_key:
            self.columns.append(
                TableCreateColumn(
                    name="id",
                    column_type="INTEGER",
                    is_primary_key=True,
                    auto_increment=True,
                )
            )
        return self


class RowData(BaseModel):
    values: Dict[str, Any] = Field(
        description="Dictionary of column names and their values"
    )
    type: Literal["row_data"] = Field(
        description="The type of the result", default="row_data"
    )


class RowCondition(BaseModel):
    condition: str = Field(description="SQL condition for identifying the row(s)")
    type: Literal["row_condition"] = Field(
        description="The type of the result", default="row_condition"
    )


class RowUpdate(BaseModel):
    updates: Dict[str, Any] = Field(
        description="Dictionary of column names and their new values"
    )
    condition: str = Field(
        description="SQL condition for identifying the row(s) to update"
    )
    type: Literal["row_update"] = Field(
        description="The type of the result", default="row_update"
    )


class ColumnDefinition(BaseModel):
    name: str = Field(description="Name of the column")
    type: str = Field(description="SQL type of the column")


class TableDataRequest(BaseModel):
    table_name: str = Field(description="The name of the table")
    limit: int = Field(description="The number of rows to return", default=1000)
    type: Literal["table_data_request"] = Field(
        description="The type of the result", default="table_data_request"
    )


class Config(BaseModel):
    database: str = Field(description="The name of the database", default="default")
    url: str = Field(description="The URL of the database", default="")
    use_default_database: bool = Field(
        description="Whether to use the default database", default=True
    )
    readonly: bool = Field(
        description="Whether the database is readonly", default=False
    )


SQL_READ_BLACKLIST = (
    "COMMIT",
    "DELETE",
    "MERGE",
    "REPLACE",
    "ROLLBACK",
    "SET",
    "START",
    "UPDATE",
    "UPSERT",
    "ALTER",
    "CREATE",
    "DROP",
    "RENAME",
    "TRUNCATE",
    "GRANT",
    "REVOKE",
)

CONFIG_KEYS = ["database", "default_database", "admin_database"]


def db_connection(url):
    # if db is neon then add options endpoint
    engine_args = {}
    if "postgresql" in url:
        url = url.replace("postgresql", "postgresql+psycopg")
    if "neon.tech" in url and "options=endpoint" not in url:
        ex = url.split("@")[1]
        endpoint = ex.split(".")[0]
        url = url + f"&options=endpoint%3D{endpoint}"
    if "sqlite" in url:
        engine_args = {"connect_args": {"check_same_thread": False}}
    return SQLDatabase.from_uri(url, engine_args=engine_args)


@tool(
    name="db_query",
    description="Query database table and receive the result",
    config=Config().model_json_schema(),
    takes_ctx=True,
)
async def db_query(query: str, **kwargs) -> QueryResult:
    flow = get_flow()
    url = flow.get("auth").get("database_url", "sqlite:///:memory:")
    flow.get("auth").get("database_readonly", False)
    try:
        connection = db_connection(url)
        result = connection.run(query)
        if result.data:
            return QueryResult(
                data=result.data,
                headers=result.headers,
                message="Success: Query executed.",
            )
        else:
            return QueryResult(data=[], headers=[], message="Success: Query executed.")
    except Exception as e:
        traceback.print_exc()
        return QueryResult(data=[], headers=[], message=f"Error: {str(e)}")


@tool(
    name="db_table_data",
    description="Get the data from the specified table",
    config=Config().model_json_schema(),
    takes_ctx=True,
)
async def db_table_data(input_data: TableDataRequest, **kwargs) -> QueryResult:
    flow = get_flow()
    flow.get("auth").get("database_url", "sqlite:///:memory:")
    flow.get("auth").get("database_readonly", True)
    query = f"SELECT * FROM {input_data.table_name} LIMIT {input_data.limit}"
    return await db_query(query)


@tool(
    name="db_list_tables",
    description="Lists the available tables in the database",
    config=Config().model_json_schema(),
    takes_ctx=True,
)
async def db_list_tables(filter: str = "all", **kwargs) -> TableList:
    flow = get_flow()
    url = flow.get("auth").get("database_url", "sqlite:///:memory:")
    try:
        connection = db_connection(url)
        tables = connection.get_usable_table_names()
        return TableList(tables=tables)
    except Exception as e:
        return TableList(tables=[], message=f"Error: {str(e)}")


@tool(
    name="db_describe_tables",
    description="Describes the specified tables in the database",
    config=Config().model_json_schema(),
    takes_ctx=True,
)
async def db_describe_tables(tables: List[str], **kwargs) -> TableDescription:
    flow = get_flow()
    url = flow.get("auth").get("database_url", "sqlite:///:memory:")
    try:
        connection = db_connection(url)
        definition = connection.get_table_info(tables)
        return TableDescription(description=definition.table_statements())
    except Exception as e:
        return TableDescription(description=f"Error: {str(e)}")


@tool(
    name="db_update_table",
    description="Updates the specified table in the database",
    config=Config().model_json_schema(),
    takes_ctx=True,
)
async def db_update_table(table: str, columns: List[str], **kwargs) -> TableDescription:
    flow = get_flow()
    url = flow.get("auth").get("database_url", "sqlite:///:memory:")
    allow_update = not flow.get("auth").get("database_readonly", False)
    if not allow_update:
        return TableDescription(description="Error: Update is not allowed.")
    try:
        connection = db_connection(url)
        connection.run(f"UPDATE {table} SET {', '.join(columns)}")
        return TableDescription(description=f"Table {table} updated successfully.")
    except Exception as e:
        return TableDescription(description=f"Error: {str(e)}")


@tool(
    name="db_create_table",
    description="Creates a new table in the database",
    config=Config().model_json_schema(),
    takes_ctx=True,
)
async def db_create_table(table: TableCreate, **kwargs) -> TableDescription:
    flow = get_flow()
    url = flow.get("auth").get("database_url", "sqlite:///:memory:")
    allow_create = not flow.get("auth").get("database_readonly", False)
    if isinstance(table, dict):
        table = TableCreate(**table)

    if not allow_create:
        return TableDescription(description="Error: Create is not allowed.")
    try:
        connection = db_connection(url)
        column_definitions = []
        for col in table.columns:
            if isinstance(col, BaseModel):
                col_str = f"{col.name} {col.column_type}"
                if col.is_primary_key:
                    col_str += " PRIMARY KEY"
                if col.auto_increment:
                    col_str += " AUTOINCREMENT"
                column_definitions.append(col_str)
            else:
                column_definitions.append(col)
        connection.run(
            f"CREATE TABLE {table.table_name} ({', '.join(column_definitions)})"
        )
        return TableDescription(
            description=f"Table {table.table_name} created successfully."
        )
    except Exception as e:
        traceback.print_exc()
        return TableDescription(description=f"Error:db_create_table: {str(e)}")


@tool(
    name="db_drop_table",
    description="Drops the specified table from the database",
    config=Config().model_json_schema(),
    takes_ctx=True,
)
async def db_drop_table(table: str, **kwargs) -> TableDescription:
    flow = get_flow()
    url = flow.get("auth").get("database_url", "sqlite:///:memory:")
    allow_drop = not flow.get("auth").get("database_readonly", False)
    if not allow_drop:
        return TableDescription(description="Error: Drop is not allowed.")
    try:
        connection = db_connection(url)
        connection.run(f"DROP TABLE {table}")
        return TableDescription(description=f"Table {table} dropped successfully.")
    except Exception as e:
        return TableDescription(description=f"Error: {str(e)}")


@tool(
    name="db_add_row",
    description="Adds a new row to the specified table",
    config=Config().model_json_schema(),
    takes_ctx=True,
)
async def db_add_row(table: str, row: RowData, **kwargs) -> TableDescription:
    flow = get_flow()
    url = flow.get("auth").get("database_url", "sqlite:///:memory:")
    allow_add = not flow.get("auth").get("database_readonly", False)
    if not allow_add:
        return TableDescription(
            description="Error: Add row is not allowed in readonly mode."
        )
    if isinstance(row, dict):
        row = RowData.model_validate(row)
    try:
        connection = db_connection(url)
        columns = ", ".join(row.values.keys())
        placeholders = ", ".join(["?"] * len(row.values))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        connection.run(query, list(row.values.values()))
        return TableDescription(description=f"Row added to {table} successfully.")
    except Exception as e:
        return TableDescription(description=f"Error: {str(e)}")


@tool(
    name="db_remove_row",
    description="Removes a row from the specified table based on a condition",
    config=Config().model_json_schema(),
    takes_ctx=True,
)
async def db_remove_row(
    table: str, condition: RowCondition, **kwargs
) -> TableDescription:
    flow = get_flow()
    url = flow.get("auth").get("database_url", "sqlite:///:memory:")
    allow_remove = not flow.get("auth").get("database_readonly", False)
    if not allow_remove:
        return TableDescription(
            description="Error: Remove row is not allowed in readonly mode."
        )

    if isinstance(condition, dict):
        condition = RowCondition.model_validate(condition)
    try:
        connection = db_connection(url)
        query = f"DELETE FROM {table} WHERE {condition.condition}"
        connection.run(query)
        return TableDescription(
            description=f"Row(s) removed from {table} successfully."
        )
    except Exception as e:
        return TableDescription(description=f"Error: {str(e)}")


@tool(
    name="db_edit_row",
    description="Edits a row in the specified table based on a condition",
    config=Config().model_json_schema(),
    takes_ctx=True,
)
async def db_edit_row(table: str, update: RowUpdate, **kwargs) -> TableDescription:
    flow = get_flow()
    url = flow.get("auth").get("database_url", "sqlite:///:memory:")
    allow_edit = not flow.get("auth").get("database_readonly", False)
    if not allow_edit:
        return TableDescription(
            description="Error: Edit row is not allowed in readonly mode."
        )
    if isinstance(update, dict):
        update = RowUpdate.model_validate(update)
    try:
        connection = db_connection(url)
        set_clause = ", ".join([f"{k} = %s" for k in update.updates.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {update.condition}"
        connection.run(query, list(update.updates.values()))
        return TableDescription(description=f"Row(s) in {table} updated successfully.")
    except Exception as e:
        return TableDescription(description=f"Error: {str(e)}")


@tool(
    name="db_add_column",
    description="Adds a new column to the specified table",
    config=Config().model_json_schema(),
    takes_ctx=True,
)
async def db_add_column(
    table: str, column: ColumnDefinition, **kwargs
) -> TableDescription:
    flow = get_flow()
    url = flow.get("auth").get("database_url", "sqlite:///:memory:")
    allow_add = not flow.get("auth").get("database_readonly", False)
    if not allow_add:
        return TableDescription(
            description="Error: Add column is not allowed in readonly mode."
        )
    if isinstance(column, dict):
        column = ColumnDefinition.model_validate(column)
    try:
        connection = db_connection(url)
        query = f"ALTER TABLE {table} ADD COLUMN {column.name} {column.type}"

        connection.run(query)
        return TableDescription(
            description=f"Column {column.name} added to {table} successfully."
        )
    except Exception as e:
        return TableDescription(description=f"Error: {str(e)}")


@tool(
    name="db_remove_column",
    description="Removes a column from the specified table",
    config=Config().model_json_schema(),
    takes_ctx=True,
)
async def db_remove_column(table: str, column_name: str, **kwargs) -> TableDescription:
    flow = get_flow()
    url = flow.get("auth").get("database_url", "sqlite:///:memory:")
    allow_remove = not flow.get("auth").get("database_readonly", False)
    if not allow_remove:
        return TableDescription(
            description="Error: Remove column is not allowed in readonly mode."
        )
    try:
        connection = db_connection(url)
        query = f"ALTER TABLE {table} DROP COLUMN {column_name}"
        connection.run(query)
        return TableDescription(
            description=f"Column {column_name} removed from {table} successfully."
        )
    except Exception as e:
        return TableDescription(description=f"Error: {str(e)}")


@tool(
    name="db_query_checker",
    description="Checks the SQL query for common mistakes",
    takes_ctx=True,
)
async def db_query_checker(query: str, dialect: str, **kwargs) -> str:
    flow = get_flow()
    flow.get("auth").get("database_url", "sqlite:///:memory:")
    flow.get("auth").get("database_readonly", True)
    template = f"""
    {query}
        Double check the {dialect} query above for common mistakes, including:
        - Using NOT IN with NULL values
        - Using UNION when UNION ALL should have been used
        - Using BETWEEN for exclusive ranges
        - Data type mismatch in predicates
        - Properly quoting identifiers
        - Using the correct number of arguments for functions
        - Casting to the correct data type
        - Using the proper columns for joins

        If there are any of the above mistakes, rewrite the query.
        If there are no mistakes, just reproduce the original query.
        Use the format below:

        ```sql
        the query
        ```
    """
    return template


database_toolkit = Toolkit.create_toolkit(
    name="database",
    id="database",
    description="A toolkit for interacting with the database",
    tools=[
        db_query,
        db_table_data,
        db_list_tables,
        db_describe_tables,
        db_update_table,
        db_create_table,
        db_drop_table,
    ],
    config_schema=Config().model_json_schema(),
    requires_config=True,
    icon="Database",
)
