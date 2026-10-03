"""Checks server status and returns health check"""

from fastapi import APIRouter
from pydantic import BaseModel


class HealthStatus(BaseModel):
    """Health check response"""

    status: str


router = APIRouter(prefix="/api")


@router.get("/health", response_model=HealthStatus)
def health_check() -> HealthStatus:
    """confirm server is running"""
    return HealthStatus(status="ok")
