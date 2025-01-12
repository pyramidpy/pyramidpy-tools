from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ToolProviderSettings(BaseSettings):
    """
    Settings for tool providers.
    Configurable from flow context or db.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    slack_api_token: SecretStr | None = None
    jina_api_key: SecretStr | None = None
    discord_api_token: SecretStr | None = None
    discord_bot_token: SecretStr | None = None
    discord_public_key: str | None = None
    apify_api_key: SecretStr | None = None
    tavily_api_key: SecretStr | None = None
    github_token: SecretStr | None = None
    telegram_bot_token: SecretStr | None = None

    # twitter
    twitter_username: str | None = None
    twitter_password: str | None = None
    twitter_email: str | None = None
    twitter_cto: str | None = None
    twitter_auth_token: str | None = None
    twitter_twid: str | None = None


class Settings(BaseSettings):
    tool_provider: ToolProviderSettings = ToolProviderSettings()

settings = Settings()
