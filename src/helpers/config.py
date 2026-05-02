from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    
    # --- Application Information ---
    APP_NAME: str
    APP_VERSION: str
    
    # --- File and Database Configurations ---
    FILE_ALLOWED_TYPES: List[str]
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    POSTGRES_USERNAME : str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_MAIN_DATABASE: str
    
    # --- AI Backends Selection ---
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str
    VECTOR_DB_BACKEND: str
    VECTOR_DB_PATH: str

    # --- API Keys and Model IDs (Optional to avoid startup errors) ---
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_URL: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None

    GENERATION_MODEL_ID: Optional[str] = None
    EMBEDDING_MODEL_ID: Optional[str] = None
    EMBEDDING_MODEL_SIZE: Optional[int] = None

    # --- Parameters with custom spelling (keeping current naming convention) ---
    INPUT_DAFULT_MAX_CHARACTERS: Optional[int] = 1000
    GENERATION_DAFAULT_MAX_TOKENS: Optional[int] = 500
    GENERATION_DAFAULT_TEMPERATURE: Optional[float] = 0.5
    
    # --- Vector Database Configurations ---
    VECTOR_DB_DISTANCE_METHOD: Optional[str] = "cosine"

    # --- Language Settings ---
    DEFAULT_LANGUAGE: str = "en"
    PRIMARY_LANGUAGE: str = "en"

    # --- Pydantic Configuration to read from .env file ---
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


def get_settings():
    """Returns an instance of the Settings class."""
    return Settings()