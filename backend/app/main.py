from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers

app = FastAPI(title=settings.app_name, version="0.1.0", debug=settings.debug)

register_exception_handlers(app)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health() -> dict:
    """Vérifie que l'API est en vie."""
    return {"status": "ok", "environment": settings.environment}
