from fastapi import APIRouter, Depends, HTTPException, Query,UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import wifi_service, import_service
from app.schemas.wifi_point import (
    WifiPointResponse,
    WifiPointWithDistance,
    PaginatedResponse,
    ImportResponse
)
from app.config import settings


router = APIRouter(prefix="/wifi-points", tags=["WiFi Points"])


@router.get(
    "",
    response_model=PaginatedResponse[WifiPointResponse],
    summary="Listar puntos WiFi"
)
def get_wifi_points(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(
        settings.default_page_size, 
        ge=1, 
        le=settings.max_page_size,
        description="Elementos por página"
    ),
    db: Session = Depends(get_db)
) -> PaginatedResponse[WifiPointResponse]:
    return wifi_service.get_all(db, page, limit)


@router.get(
    "/nearby/",
    response_model=PaginatedResponse[WifiPointWithDistance],
    summary="Listar puntos WiFi por proximidad"
)
def get_nearby_wifi_points(
    lat: float = Query(..., ge=-90, le=90, description="Latitud"),
    lng: float = Query(..., ge=-180, le=180, description="Longitud"),
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(
        settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description="Elementos por página"
    ),
    db: Session = Depends(get_db)
) -> PaginatedResponse[WifiPointWithDistance]:
    return wifi_service.get_nearby(db, lat, lng, page, limit)


@router.get(
    "/alcaldia/{alcaldia}",
    response_model=PaginatedResponse[WifiPointResponse],
    summary="Listar puntos WiFi por alcaldía"
)
def get_wifi_points_by_alcaldia(
    alcaldia: str,
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(
        settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description="Elementos por página"
    ),
    db: Session = Depends(get_db)
) -> PaginatedResponse[WifiPointResponse]:
    return wifi_service.get_by_alcaldia(db, alcaldia, page, limit)


@router.get(
    "/{wifi_id}",
    response_model=WifiPointResponse,
    summary="Obtener punto WiFi por ID"
)
def get_wifi_point(
    wifi_id: str,
    db: Session = Depends(get_db)
) -> WifiPointResponse:
    point = wifi_service.get_by_id(db, wifi_id)
    
    if not point:
        raise HTTPException(status_code=404, detail="Punto WiFi no encontrado")
    
    return point


@router.post(
    "/import",
    response_model=ImportResponse,
    summary="Importar desde CSV/Excel"
)
async def import_wifi_points(
    file: UploadFile = File(...),
    on_error: str = Form(default="report"),
    on_duplicate: str = Form(default="ignore"),
    db: Session = Depends(get_db)
) -> ImportResponse:
    content = await file.read()
    return import_service.import_file(db, content, file.filename, on_error, on_duplicate)