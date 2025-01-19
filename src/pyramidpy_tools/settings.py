from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageSettings(BaseSettings):
    """
    Settings for storage.
    """

    postgres_url: str | None = None
    chroma_url: str | None = None
    pgvector_url: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class ToolProviderSettings(BaseSettings):
    """
    Settings for tool providers.
    Configurable from flow context or db.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    slack_api_token: str | None = None
    jina_api_key: str | None = None
    discord_api_token: str | None = None
    discord_bot_token: str | None = None
    discord_public_key: str | None = None
    apify_api_key: str | None = None
    tavily_api_key: str | None = None
    github_token: str | None = None
    telegram_bot_token: str | None = None

    # twitter
    twitter_username: str | None = None
    twitter_password: str | None = None
    twitter_email: str | None = None
    twitter_cto: str | None = None
    twitter_auth_token: str | None = None
    twitter_twid: str | None = None

    # storage
    storage: StorageSettings = StorageSettings()


class LLMProviderSettings(BaseSettings):
    """
    Settings for LLM providers.
    """

    openai_api_key: SecretStr | None = None
    anthropic_api_key: SecretStr | None = None
    google_api_key: SecretStr | None = None
    groq_api_key: SecretStr | None = None
    ollama_api_key: SecretStr | None = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    tool_provider: ToolProviderSettings = ToolProviderSettings()
    storage: StorageSettings = StorageSettings()
    llm: LLMProviderSettings = LLMProviderSettings()


settings = Settings()
