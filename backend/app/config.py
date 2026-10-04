# app configuration file
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application default settings"""

    cors_origins: str = "http://localhost:5173"
    max_upload_mb: int = 5
    index_path: str = "data/index.npz"
    catalog_path: str = "data/catalog.json"
    ffmpeg_timeout_s: float = 10.0

    @property
    def cors_origins_list(self) -> list[str]:
        """returns allowed origins in list format"""
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def max_upload_bytes(self) -> int:
        """the upload limit in bytes"""
        return self.max_upload_mb * 1_000_000


@lru_cache
def get_settings() -> Settings:
    return Settings()
