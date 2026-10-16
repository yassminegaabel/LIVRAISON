from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)


@app.get("/health", tags=["system"])
def health() -> dict:
    """Vérifie que l'API est en vie."""
    return {
        "status": "ok",
        "environment": settings.environment,
    }
