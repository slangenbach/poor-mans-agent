"""Configuration."""

from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Configuration."""

    model_config = SettingsConfigDict(env_file=".env")

    ai_model_base_url: str = "https://openrouter.ai/api/v1"
    ai_model_name: str = "openrouter/mistralai/mistral-small-3.1-24b-instruct:free"
    ai_model_key: SecretStr
    jina_ai_key: SecretStr
    anthropic_key: SecretStr | None = None
    tool_call_timeout: int = 30

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


def get_config() -> Config:
    """Get config."""
    return Config()  # type: ignore[missing-argument]
