# app configuration file
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application default settings"""

    database_url: str = "sqlite:///./test.db"
    cors_origins: str = "http://localhost:5173"
    max_upload_mb: int = 5
    index_path: str = "data/index.npz"

    @property
    def cors_origins_list(self) -> list[str]:
        """returns allowed origins in list format"""
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
