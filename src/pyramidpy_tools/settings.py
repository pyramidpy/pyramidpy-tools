from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

VectorStoreType = Literal["pg_vector", "chroma"]
ChromaClientType = Literal["base", "http"] | str | None


class LoggingSettings(BaseSettings):
    level: str = "DEBUG"


class RedisSettings(BaseSettings):
    use_disk_cache: bool = True
    use_fake_redis: bool = False
    url: str | None = None


class StorageSettings(BaseSettings):
    """
    Settings for storage.
    """

    postgres_url: str | None = None
    pgvector_url: str | None = Field(
        default=None, description="The URL of the PGVector database"
    )
    default_vector_store: VectorStoreType = "pg_vector"

    chroma_url: str | None = None
    chroma_client_type: ChromaClientType = "base"
    chroma_server_authn_credentials: SecretStr | None = None
    # s3
    s3_bucket: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_region: str | None = None
    s3_endpoint_url: str | None = None

    redis: RedisSettings = RedisSettings()

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def validate(self):
        if (
            self.default_vector_store == "pg_vector"
            and self.pgvector_url is None
            and self.postgres_url
        ):
            self.pgvector_url = self.postgres_url
        elif self.default_vector_store == "chroma" and self.chroma_url is None:
            raise ValueError("chroma_url must be provided")
        return self


class ToolProviderSettings(BaseSettings):
    """
    Settings for tool providers.
    Configurable from flow context or db.
    """

    slack_api_token: str | None = None
    jina_api_key: str | None = None
    discord_api_token: str | None = None
    discord_bot_token: str | None = None
    discord_public_key: str | None = None
    apify_api_key: str | None = None
    tavily_api_key: str | None = None
    github_token: str | None = None
    telegram_bot_token: str | None = None
    telegram_webhook_base_url: str | None = None
    telegram_webhook_secret: str | None = "test_secret_changemeZZX"

    # twitter
    twitter_username: str | None = None
    twitter_password: str | None = None
    twitter_email: str | None = None
    twitter_cto: str | None = None
    twitter_auth_token: str | None = None
    twitter_twid: str | None = None

    twitter_bearer_token: str | None = None
    twitter_consumer_key: str | None = None
    twitter_consumer_secret_key: str | None = None
    twitter_access_token: str | None = None
    twitter_access_token_secret: str | None = None

    birdeye_api_key: str | None = None
    e2b_api_key: str | None = None
    # storage
    storage: StorageSettings = StorageSettings()

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class LLMProviderSettings(BaseSettings):
    """
    Settings for LLM providers.
    """

    openai_api_key: str | None = None
    openai_api_base: str | None = None

    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    groq_api_key: str | None = None
    ollama_api_key: str | None = None
    together_api_key: str | None = None
    deepseek_api_key: str | None = None

    # default model
    default_model: str = "openai/gpt-4o-mini"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class EmbeddingSettings(BaseSettings):
    provider: str = "openai"
    dimensions: int = 1536

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    tool_provider: ToolProviderSettings = ToolProviderSettings()
    storage: StorageSettings = StorageSettings()
    llm: LLMProviderSettings = LLMProviderSettings()
    logging: LoggingSettings = LoggingSettings()
    embeddings: EmbeddingSettings = EmbeddingSettings()


settings = Settings()
