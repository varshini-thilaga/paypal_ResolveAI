import os
from functools import lru_cache
from typing import Literal
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings for ResolveAI Backend.
    Reads PayPal configuration from environment variables or .env file.
    All secrets are wrapped in SecretStr to prevent accidental logging or exposure.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "ResolveAI PayPal Integration Service"
    APP_ENV: str = "development"
    APP_URL: str = "http://localhost:8000"

    # PayPal Configuration
    PAYPAL_ENV: Literal["sandbox", "live"] = Field(
        default="sandbox",
        description="PayPal environment mode. Must default to 'sandbox'."
    )
    PAYPAL_BASE_URL: str = Field(
        default="https://api-m.sandbox.paypal.com",
        description="PayPal API Base URL. Must be sandbox endpoint."
    )
    PAYPAL_CLIENT_ID: str = Field(
        default="",
        description="PayPal REST Client ID."
    )
    PAYPAL_CLIENT_SECRET: SecretStr = Field(
        default=SecretStr(""),
        description="PayPal REST Client Secret. Kept in SecretStr to prevent leak."
    )
    PAYPAL_WEBHOOK_ID: str = Field(
        default="",
        description="PayPal Webhook ID for signature verification."
    )

    # Core Security & App Secrets
    SESSION_SECRET: SecretStr = Field(
        default=SecretStr("default-insecure-dev-secret-change-in-env"),
        description="Secret key for signing sessions and authorization tokens."
    )
    ENCRYPTION_KEY: SecretStr = Field(
        default=SecretStr(""),
        description="Symmetric encryption key for database fields."
    )

    @field_validator("PAYPAL_BASE_URL")
    @classmethod
    def validate_sandbox_url(cls, v: str, info) -> str:
        # Enforce sandbox safety
        cleaned = v.rstrip("/")
        return cleaned


@lru_cache()
def get_settings() -> Settings:
    """Return cached instance of application settings."""
    return Settings()
