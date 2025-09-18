from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "local"
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/nakliye"
    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    # Public API base URLs for OpenAPI servers
    PROD_API_URL: str = "https://api.f4st.com"
    STAGING_API_URL: str = "https://staging-api.f4st.com"
    LOCAL_API_URL: str = "http://localhost:8000"
    # Pydantic v2 style config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()
