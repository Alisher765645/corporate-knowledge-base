from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://kb:kb@localhost:5432/kb"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 8

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    chat_model: str = "gpt-4o-mini"

    max_query_chars: int = 5000
    chunk_size_chars: int = 1500
    chunk_overlap_chars: int = 200
    search_top_k: int = 8


@lru_cache
def get_settings() -> Settings:
    return Settings()
