"""
Configuration module for the Todo Backend Application.

Loads settings from environment variables using Pydantic Settings.
"""
import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field
from pydantic import field_validator



class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database configuration
    DATABASE_URL: str = Field(default="postgresql://neondb_owner:npg_3bWDrjmIqat7@ep-lucky-bush-ah80vgjx-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require", description="Database URL. Defaults to Neon Database, can be overridden for different environments")

    # Authentication configuration
    SECRET_KEY: str = Field(default="your-jwt-secret-key-minimum-32-characters-long", description="JWT Secret key. Should be set as an environment variable in production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Server configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = Field(default=7860)

    # AI Configuration
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API key for AI chatbot")

    DEBUG: bool = False

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v):
        """Ensure DATABASE_URL is never empty or invalid."""
        # Default NeonDB URL
        default_url = "postgresql://neondb_owner:npg_3bWDrjmIqat7@ep-lucky-bush-ah80vgjx-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        
        # If value is None, empty string, or whitespace-only, return default
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return default_url
        
        return v

    @field_validator("API_PORT", mode="before")
    @classmethod
    def validate_api_port(cls, v):
        if v is None or v == "" or v is False:
            return 7860
        try:
            port = int(v)
            if port <= 0:
                return 7860  # Return default if port is invalid
            return port
        except (ValueError, TypeError):
            # If conversion fails, return default port
            return 7860

    @field_validator("ALGORITHM", mode="before")
    @classmethod
    def validate_algorithm(cls, v):
        """Ensure ALGORITHM is never empty."""
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return "HS256"
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }



@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Using lru_cache ensures that settings are only loaded once
    and reused across all imports.

    Returns:
        Settings: Application settings singleton.
    """
    return Settings()


# Global settings instance
settings = get_settings()
