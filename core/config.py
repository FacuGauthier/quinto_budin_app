from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Gestión de Pedidos"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./emprendimiento.db"
    SECRET_KEY: str = "cambia-esta-clave-en-produccion"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
