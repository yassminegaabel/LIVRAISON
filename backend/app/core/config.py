
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Réglages de l'application, lus depuis les variables d'environnement / .env."""

    app_name: str = "Delivery Platform API"
    environment: str = "development"
    debug: bool = False

    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
