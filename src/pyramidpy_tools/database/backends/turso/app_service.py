import json
import shortuuid
from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from .client import TursoClient
from .database import TursoDatabase
from .types import CreateDatabaseInput, Database

client = TursoClient()
db_api = TursoDatabase(client)


class Groups:
    eu = "eu"
    us = "us"


def list_databases(organization_name: str) -> list[Database]:
    return db_api.list_databases(organization_name)


def create_database(
    organization_name: str, database_name: str, group, region="eu"
) -> Database:
    data = CreateDatabaseInput(name=database_name, group=region)
    return db_api.create_database(organization_name, data)


def delete_database(organization_name: str, database_name: str) -> None:
    return db_api.delete_database(organization_name, database_name)


def create_database_token(
    organization_name: str, database_name: str, expiration: str, authorization: str
) -> dict:
    return db_api.create_database_token(
        organization_name, database_name, expiration, authorization
    )


def setup_tenant_db(tenant_id: str, region="eu", is_test=False):
    database_name = "db-" + str(shortuuid.uuid(pad_length=10))
    database_name = database_name.lower()

    if is_test:
        database_name = "test-database-vanty"

    db = create_database("advantch", database_name, tenant_id)
    token = create_database_token("advantch", database_name, "52w", "full-access")
    url = f"sqlite+libsql://{db.hostname}/?authToken={token.get('jwt')}&secure=true"
    data = {"database": db.model_dump(), "token": token, "url": url}
    return data


def destroy_tenant_db(organization_name: str, database_name: str):
    delete_database(organization_name, database_name)


def list_tables(dbUrl: str):
    engine = create_engine(dbUrl, connect_args={"check_same_thread": False}, echo=True)
    return engine.table_names()


def get_table_columns(dbUrl: str, table_name: str):
    engine = create_engine(dbUrl, connect_args={"check_same_thread": False}, echo=True)
    inspector = inspect(engine)
    return inspector.get_columns(table_name)


def create_table(dbUrl: str, table_name: str, columns: list):
    engine = create_engine(dbUrl, connect_args={"check_same_thread": False}, echo=True)
    column_definitions = ", ".join([f"{col['name']} {col['type']}" for col in columns])
    sql = f"CREATE TABLE {table_name} ({column_definitions})"
    with engine.connect() as connection:
        connection.execute(text(sql))
        connection.commit()


def add_table_columns_from_json(dbUrl: str, table_name: str, json_data: str):
    engine = create_engine(dbUrl, connect_args={"check_same_thread": False}, echo=True)
    columns = json.loads(json_data)
    for column in columns:
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column['name']} {column['type']}"
        with engine.connect() as connection:
            connection.execute(text(sql))
            connection.commit()
