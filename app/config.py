import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación usando variables de entorno."""
    
    # Base de datos
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/wifi_cdmx"
    )
    
    # API
    api_title: str = "WiFi CDMX API"
    api_version: str = "1.0.0"
    api_description: str = "API para consultar puntos de acceso WiFi en la Ciudad de México"
    
    # Paginación
    default_page_size: int = 20
    max_page_size: int = 100


# Instancia global de configuración
settings = Settings()