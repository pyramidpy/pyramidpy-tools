# flake8: noqa E501
from typing import List
from .types import (
    CreateDatabaseInput,
    CreateDatabaseOutput,
    Database,
    DatabaseStatsOutput,
    DatabaseUsageOutput,
    DatabaseConfigurationInput,
    DatabaseConfigurationResponse,
)
import humps


class TursoDatabase:
    def __init__(self, api_client):
        self.api_client = api_client

    def list_databases(self, organization_name: str) -> List[Database]:
        url = f"/v1/organizations/{organization_name}/databases"
        response = self.api_client.get(url)
        return [Database(**humps.decamelize(db)) for db in response["databases"]]

    def create_database(
        self, organization_name: str, input_data: CreateDatabaseInput
    ) -> CreateDatabaseOutput:
        url = f"/v1/organizations/{organization_name}/databases"
        response = self.api_client.post(url, json=input_data.model_dump())
        return CreateDatabaseOutput(**humps.decamelize(response.get("database")))

    def get_database(self, organization_name: str, database_name: str) -> Database:
        url = f"/v1/organizations/{organization_name}/databases/{database_name}"
        response = self.api_client.get(url)
        return Database(**humps.decamelize(response))

    def delete_database(self, organization_name: str, database_name: str) -> None:
        url = f"/v1/organizations/{organization_name}/databases/{database_name}"
        self.api_client.delete(url)

    def get_database_stats(
        self, organization_name: str, database_name: str
    ) -> DatabaseStatsOutput:
        url = f"/v1/organizations/{organization_name}/databases/{database_name}/stats"
        response = self.api_client.get(url)
        return DatabaseStatsOutput(**humps.decamelize(response))

    def get_database_usage(
        self, organization_name: str, database_name: str
    ) -> DatabaseUsageOutput:
        url = f"/v1/organizations/{organization_name}/databases/{database_name}/usage"
        response = self.api_client.get(url)
        return DatabaseUsageOutput(**humps.decamelize(response))

    def upload_database_dump(self, organization_name: str, file_path: str) -> str:
        url = f"/v1/organizations/{organization_name}/databases/dumps"
        files = {"file": open(file_path, "rb")}
        response = self.api_client.post(url, files=files)
        return response["url"]

    def update_database_configuration(
        self,
        organization_name: str,
        database_name: str,
        input_data: DatabaseConfigurationInput,
    ) -> DatabaseConfigurationResponse:
        url = f"/v1/organizations/{organization_name}/databases/{database_name}/configuration"
        response = self.api_client.patch(url, json=input_data.model_dump())
        return DatabaseConfigurationResponse(**humps.decamelize(response))

    def create_database_token(
        self,
        organization_name: str,
        database_name: str,
        expiration: str,
        authorization: str,
    ) -> dict:
        url = f"/v1/organizations/{organization_name}/databases/{database_name}/auth/tokens"
        params = {
            "expiration": expiration,
            "authorization": authorization,
        }
        response = self.api_client.post(url, params=params)
        return response

    def rotate_database_credentials(
        self, organization_name: str, database_name: str
    ) -> None:
        url = f"/v1/organizations/{organization_name}/databases/{database_name}/auth/rotate"
        self.api_client.post(url)
