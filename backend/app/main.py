"""create/configure fast api app"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router
from app.config import get_settings


def create_app() -> FastAPI:
    """create and configure fast api app"""
    settings = get_settings()
    app = FastAPI(title="Humm")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()
