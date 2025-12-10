from sqlalchemy import func
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_SetSRID, ST_MakePoint, ST_DistanceSphere

from app.models.wifi_point import WifiPoint


def get_by_id(db: Session, wifi_id: str) -> WifiPoint | None:
    return db.query(WifiPoint).filter(WifiPoint.id == wifi_id).first() 


def get_all(db: Session, page: int, limit: int) -> tuple[list[WifiPoint], int]:
    """
    Obtiene lista paginada de puntos WiFi.
    
    Args:
        db: Sesión de base de datos
        page: Número de página (1-indexed)
        limit: Elementos por página
        
    Returns:
        Tupla con (lista de puntos, total de registros)
    """
    offset = (page - 1) * limit
    
    total = db.query(func.count(WifiPoint.id)).scalar()
    points = (
        db.query(WifiPoint)
        .order_by(WifiPoint.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return points, total


def get_by_alcaldia(db: Session, alcaldia: str, page: int, limit: int) -> tuple[list[WifiPoint], int]:
    """
    Obtiene puntos WiFi filtrados por alcaldía.
    
    Args:
        db: Sesión de base de datos
        alcaldia: Nombre de la alcaldía
        page: Número de página
        limit: Elementos por página
        
    Returns:
        Tupla con (lista de puntos, total de registros en esa alcaldía)
    """
    offset = (page - 1) * limit
    
    base_query = db.query(WifiPoint).filter(
        func.lower(WifiPoint.alcaldia) == func.lower(alcaldia)
    )
    
    total = base_query.count()
    points = (
        base_query
        .order_by(WifiPoint.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return points, total


def get_nearby(
    db: Session, 
    lat: float, 
    lng: float, 
    page: int, 
    limit: int
) -> tuple[list[tuple[WifiPoint, float]], int]:
    """
    Obtiene puntos WiFi ordenados por proximidad a una coordenada.
    
    Args:
        db: Sesión de base de datos
        lat: Latitud del punto de referencia
        lng: Longitud del punto de referencia
        page: Número de página
        limit: Elementos por página
        
    Returns:
        Tupla con (lista de tuplas (punto, distancia_metros), total)
    """
    offset = (page - 1) * limit
    
    reference_point = ST_SetSRID(ST_MakePoint(lng, lat), 4326)
    distance = ST_DistanceSphere(WifiPoint.location, reference_point).label("distancia_metros")
    
    total = db.query(func.count(WifiPoint.id)).scalar()
    
    results = (
        db.query(WifiPoint, distance)
        .order_by(distance)
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return results, total


def create(db: Session, wifi_point: WifiPoint) -> WifiPoint:
    """Crea un nuevo punto WiFi."""
    db.add(wifi_point)
    db.commit()
    db.refresh(wifi_point)
    return wifi_point


def create_multiple(db: Session, wifi_points: list[WifiPoint]) -> int:
    """Crea múltiples puntos WiFi en una transacción."""
    db.add_all(wifi_points)
    db.commit()
    return len(wifi_points)


def exists(db: Session, wifi_id: str) -> bool:
    """Verifica si existe un punto WiFi con el ID dado."""
    return db.query(
        db.query(WifiPoint).filter(WifiPoint.id == wifi_id).exists()
    ).scalar()


def update(db: Session, wifi_point: WifiPoint) -> WifiPoint:
    """Actualiza un punto WiFi existente."""
    db.commit()
    db.refresh(wifi_point)
    return wifi_point

def update_multiple(db: Session, wifi_points: list[WifiPoint]) -> int:
    """Actualiza múltiples puntos WiFi en una transacción."""
    db.commit()
    return len(wifi_points)