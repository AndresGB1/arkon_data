"""
Servicio de lógica de negocio para puntos WiFi.
Enfoque funcional: funciones puras, composición, inmutabilidad.
"""
from sqlalchemy.orm import Session

from app.models.wifi_point import WifiPoint
from app.repositories import wifi_repository as repo
from app.schemas.wifi_point import (
    WifiPointResponse,
    WifiPointWithDistance,
    PaginatedResponse,
    PaginationMeta,
)
from app.config import settings


def calculate_pages(total: int, limit: int) -> int:
    """Calcula el número total de páginas."""
    return (total + limit - 1) // limit if limit > 0 else 0


def max_limit(limit: int) -> int:
    """Limita el valor de limit al máximo permitido."""
    return min(limit, settings.max_page_size)


def to_response(point: WifiPoint) -> WifiPointResponse:
    """Transforma un WifiPoint a WifiPointResponse."""
    return WifiPointResponse.model_validate(point)


def to_response_with_distance(point: WifiPoint, distance: float) -> WifiPointWithDistance:
    """Transforma un WifiPoint a WifiPointWithDistance."""
    return WifiPointWithDistance(
        id=point.id,
        programa=point.programa,
        latitud=point.latitud,
        longitud=point.longitud,
        alcaldia=point.alcaldia,
        created_at=point.created_at,
        updated_at=point.updated_at,
        distancia_metros=round(distance, 2)
    )


def build_pagination(page: int, limit: int, total: int) -> PaginationMeta:
    """Construye metadata de paginación."""
    return PaginationMeta(
        page=page,
        limit=limit,
        total=total,
        pages=calculate_pages(total, limit)
    )


def get_by_id(db: Session, wifi_id: str) -> WifiPointResponse | None:
    """Obtiene un punto WiFi por su ID."""
    point = repo.get_by_id(db, wifi_id)
    return to_response(point) if point else None


def get_all(
    db: Session, 
    page: int = 1, 
    limit: int = settings.default_page_size
) -> PaginatedResponse[WifiPointResponse]:
    """Obtiene lista paginada de todos los puntos WiFi."""
    limit = max_limit(limit)
    points, total = repo.get_all(db, page, limit)
    
    data = list(map(to_response, points))
    
    return PaginatedResponse(
        data=data,
        pagination=build_pagination(page, limit, total)
    )


def get_by_alcaldia(
    db: Session, 
    alcaldia: str, 
    page: int = 1, 
    limit: int = settings.default_page_size
) -> PaginatedResponse[WifiPointResponse]:
    """Obtiene puntos WiFi filtrados por alcaldía."""
    limit = max_limit(limit)
    points, total = repo.get_by_alcaldia(db, alcaldia, page, limit)
    
    data = list(map(to_response, points))
    
    return PaginatedResponse(
        data=data,
        pagination=build_pagination(page, limit, total)
    )


def get_nearby(
    db: Session, 
    lat: float, 
    lng: float, 
    page: int = 1, 
    limit: int = settings.default_page_size
) -> PaginatedResponse[WifiPointWithDistance]:
    """Obtiene puntos WiFi ordenados por proximidad."""
    limit = max_limit(limit)
    results, total = repo.get_nearby(db, lat, lng, page, limit)
    
    data = [to_response_with_distance(point, distance) for point, distance in results]
    
    return PaginatedResponse(
        data=data,
        pagination=build_pagination(page, limit, total)
    )