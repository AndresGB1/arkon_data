"""
Schemas Pydantic para validación de datos y respuestas de la API.
Aquí definimos el tipado fuerte de la aplicación.
"""
from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, ConfigDict


# TypeVar para paginación genérica
T = TypeVar("T")


class WifiPointBase(BaseModel):
    """Campos base de un punto WiFi."""
    id: str = Field(..., description="Identificador único del punto WiFi")
    programa: str = Field(..., description="Programa al que pertenece (ej: Aeropuerto, MiCalle)")
    latitud: Decimal = Field(..., description="Latitud en grados decimales")
    longitud: Decimal = Field(..., description="Longitud en grados decimales")
    alcaldia: str = Field(..., description="Alcaldía donde se ubica el punto")


class WifiPointResponse(WifiPointBase):
    """Schema para respuesta de un punto WiFi."""
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)


class WifiPointWithDistance(WifiPointResponse):
    """Schema para respuesta con distancia (usado en búsqueda por proximidad)."""
    distancia_metros: float = Field(..., description="Distancia en metros al punto de referencia")


class PaginationMeta(BaseModel):
    """Metadata de paginación."""
    page: int = Field(..., description="Página actual")
    limit: int = Field(..., description="Elementos por página")
    total: int = Field(..., description="Total de elementos")
    pages: int = Field(..., description="Total de páginas")


class PaginatedResponse(BaseModel, Generic[T]):
    """Respuesta paginada genérica."""
    data: list[T]
    pagination: PaginationMeta


class ImportError(BaseModel):
    """Detalle de un error durante la importación."""
    row: int = Field(..., description="Número de fila con error")
    id: str | None = Field(None, description="ID del registro si está disponible")
    reason: str = Field(..., description="Motivo del error")


class ImportResponse(BaseModel):
    """Respuesta de la importación de datos."""
    status: str = Field(..., description="Estado: 'success', 'partial', 'failed'")
    imported: int = Field(..., description="Registros importados exitosamente")
    skipped: int = Field(..., description="Registros omitidos")
    errors: list[ImportError] = Field(default_factory=list, description="Lista de errores")