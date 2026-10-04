"""create/configure fast api app"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, recognize
from app.config import get_settings
from matching.catalog import load_catalog
from matching.index import MelodyIndex

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("humm")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """runs on startup"""
    settings = get_settings()

    catalog = {}
    for entry in load_catalog(Path(settings.catalog_path)):
        catalog[entry.song_id] = entry
    app.state.catalog = catalog

    app.state.index = MelodyIndex.load(Path(settings.index_path))
    logger.info("Loaded %d songs.", len(app.state.index.contours))
    yield


def create_app() -> FastAPI:
    """create and configure fast api app"""
    settings = get_settings()
    app = FastAPI(title="Humm", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(recognize.router)
    return app


app = create_app()
