from fastapi import FastAPI

app = FastAPI(title="Delivery Platform API", version="0.1.0")


@app.get("/health", tags=["system"])
def health() -> dict:
    """Vérifie que l'API est en vie."""
    return {"status": "ok"}