"""Configuración de la aplicación"""
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación"""

    # API
    API_TITLE: str = "ME FALTA UNO API"
    API_VERSION: str = "1.0.0"

    # CORS
    CORS_ORIGINS: list = ["*"]

    # Database
    DATABASE_URL: str = "sqlite:///./mefaltauno.db"

    # Seguridad
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"


# Instancia global de configuración
settings = Settings()