"""Configuración de la aplicación"""
from pydantic import BaseSettings  # ✅ Cambiado de pydantic_settings


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # API
    API_TITLE: str = "ME FALTA UNO API"
    API_VERSION: str = "2.0.0"
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    # Database (para futura implementación)
    DATABASE_URL: str = "sqlite:///./mefaltauno.db"
    
    # Seguridad (para futura implementación)
    SECRET_KEY: str = "your-secret-key-here"
    
    class Config:
        env_file = ".env"


# Instancia global de configuración
settings = Settings()