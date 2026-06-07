"""
Configuration Management for Fraud Resolution System

This module handles all environment-based configuration using pydantic-settings.
Settings are loaded from:
1. Environment variables
2. .env file (for local development)
3. /var/run/secrets (for Kubernetes secrets)

Configuration Categories:
- Redis: Connection settings for session storage and vector search
- AWS: Region and credentials for Bedrock access
- Auth: Cognito settings for JWT validation
- MLflow: Tracking URI for experiment logging
- Dev: Development mode toggles

Author: Fraud Prevention Team
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via environment variables or .env file.
    Secrets should be stored in /var/run/secrets/ (Kubernetes) or AWS Secrets Manager.
    """
    
    # ==================== Redis Configuration ====================
    REDIS_HOST: str  # Redis server hostname (e.g., "localhost" or "redis-service")
    REDIS_TLS_PORT: int = 6379  # Redis port (6379 for non-TLS, 6380 for TLS)
    REDIS_PASSWORD: str = ""  # Optional: Redis password (required for Redis Cloud)
    REDIS_TLS_CERT: str = ""  # Optional: Client certificate for TLS (PEM format)
    REDIS_TLS_KEY: str = ""  # Optional: Client private key for TLS (PEM format)
    REDIS_CA_CERT: str = ""  # Optional: CA certificate for TLS verification (PEM format)

    # ==================== AWS Configuration ====================
    AWS_REGION: str = "us-east-1"  # AWS region for Bedrock and other services

    # ==================== Authentication Configuration ====================
    COGNITO_USER_POOL_ID: str  # AWS Cognito User Pool ID (e.g., "us-east-1_XXXXXXX")
    COGNITO_CLIENT_ID: str  # Cognito App Client ID for JWT validation
    ALLOWED_ORIGINS: list[str] = ["https://portal.internal.bank.com"]  # CORS allowed origins

    # ==================== MLflow Configuration ====================
    MLFLOW_TRACKING_URI: str  # MLflow tracking server URI
    # Examples:
    #   Local dev: "sqlite:///mlflow.db"
    #   Kubernetes: "http://mlflow.fraud-system.svc.cluster.local:5000"
    #   Remote: "https://mlflow.example.com"

    # ==================== Development Mode ====================
    DEV_MODE: bool = False  # Enable development mode
    # When True:
    #   - Disables JWT authentication (returns mock customer/analyst IDs)
    #   - Enables OpenAPI docs at /docs and /redoc
    #   - Allows insecure Redis connections (no TLS)
    #   - Adds verbose logging
    # WARNING: Never set to True in production!

    model_config = SettingsConfigDict(
        env_file=".env",  # Load from .env file if present
        env_file_encoding="utf-8",
        secrets_dir="/var/run/secrets",  # Kubernetes secrets mount point
        case_sensitive=True,  # Environment variables are case-sensitive
    )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses @lru_cache to ensure settings are only loaded once per application lifecycle.
    This improves performance and ensures consistent configuration.
    
    Returns:
        Settings: Configured settings instance
    """
    return Settings()


# Global settings instance
# Import this in other modules: from app.config import settings
settings = get_settings()