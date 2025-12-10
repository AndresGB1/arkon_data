import pandas as pd
from sqlalchemy.orm import Session

from app.models.wifi_point import WifiPoint
from app.repositories import wifi_repository as repo
from app.schemas.wifi_point import ImportResponse, ImportError
from app.utils.file_reader import read_file, parse_decimal

REQUIRED_COLUMNS = {"id", "programa", "latitud", "longitud", "alcaldia"}

def validate_row(row: pd.Series) -> str | None:
    """Valida una fila. Retorna None si ok, mensaje si error."""
    if pd.isna(row.get("id")) or str(row.get("id")).strip() == "":
        return "ID es requerido"
    if pd.isna(row.get("programa")):
        return "Programa es requerido"
    if pd.isna(row.get("alcaldia")):
        return "Alcaldía es requerida"
    
    lat = parse_decimal(row.get("latitud"))
    lng = parse_decimal(row.get("longitud"))
    
    if lat is None:
        return "Latitud inválida"
    if lng is None:
        return "Longitud inválida"
    if not -90 <= lat <= 90:
        return f"Latitud fuera de rango: {lat}"
    if not -180 <= lng <= 180:
        return f"Longitud fuera de rango: {lng}"
    
    return None


def row_to_wifi_point(row: pd.Series) -> WifiPoint:
    """Convierte fila a WifiPoint."""
    lat = parse_decimal(row["latitud"])
    lng = parse_decimal(row["longitud"])
    
    return WifiPoint(
        id=str(row["id"]).strip(),
        programa=str(row["programa"]).strip(),
        latitud=lat,
        longitud=lng,
        alcaldia=str(row["alcaldia"]).strip(),
        location=f"SRID=4326;POINT({lng} {lat})"
    )


def update_wifi_point(existing: WifiPoint, row: pd.Series) -> None:
    """Actualiza un WifiPoint existente."""
    lat = parse_decimal(row["latitud"])
    lng = parse_decimal(row["longitud"])
    
    existing.programa = str(row["programa"]).strip()
    existing.latitud = lat
    existing.longitud = lng
    existing.alcaldia = str(row["alcaldia"]).strip()
    existing.location = f"SRID=4326;POINT({lng} {lat})"


def handle_error(
    reason: str,
    row_num: int,
    row_id: str | None,
    strategy: str,
    errors: list[ImportError]
) -> ImportResponse | None:
    """
    Maneja un error según la estrategia.
    
    - fail: retorna ImportResponse (para todo)
    - skip/report: acumula error, retorna None (continúa)
    """
    if strategy == "fail":
        return ImportResponse(
            status="failed",
            imported=0,
            skipped=0,
            errors=[ImportError(row=row_num, id=row_id, reason=reason)]
        )
    
    errors.append(ImportError(row=row_num, id=row_id, reason=reason))
    return None


def import_file(
    db: Session,
    content: bytes,
    filename: str,
    on_error: str = "fail",      # fail | skip 
    on_duplicate: str = "skip"     # fail | skip | update
) -> ImportResponse:
    """Importa puntos WiFi desde CSV/Excel."""
    errors: list[ImportError] = []
    to_insert: list[WifiPoint] = []
    to_update: list[WifiPoint] = []
    skipped = 0
    
    # Leer archivo
    try:
        df = read_file(content, filename)
    except Exception as e:
        return ImportResponse(
            status="failed", imported=0, skipped=0,
            errors=[ImportError(row=0, id=None, reason=f"Error leyendo archivo: {e}")]
        )
    
    # Validar columnas
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        return ImportResponse(
            status="failed", imported=0, skipped=0,
            errors=[ImportError(row=0, id=None, reason=f"Columnas faltantes: {missing}")]
        )
    
    # Procesar filas
    for idx, row in df.iterrows():
        row_num = idx + 2
        row_id = str(row.get("id", "")).strip() if pd.notna(row.get("id")) else None
        
        # Validar estructura
        error_msg = validate_row(row)
        if error_msg:
            response = handle_error(error_msg, row_num, row_id, on_error, errors)
            if response:
                return response
            skipped += 1
            continue
        
        # Verificar duplicado
        if repo.exists(db, row_id):
            if on_duplicate == "update":
                existing = repo.get_by_id(db, row_id)
                update_wifi_point(existing, row)
                to_update.append(existing)
                continue
            
            # fail o skip: misma lógica que errores
            response = handle_error("ID duplicado", row_num, row_id, on_duplicate, errors)
            if response:
                return response
            skipped += 1
            continue
        
        to_insert.append(row_to_wifi_point(row))
    
    # Aplicar cambios
    try:
        if to_insert:
            repo.create_multiple(db, to_insert)
        if to_update:
            repo.update_multiple(db, to_update)
    except Exception as e:
        db.rollback()
        return ImportResponse(
            status="failed", imported=0, skipped=0,
            errors=[ImportError(row=0, id=None, reason=f"Error en BD: {e}")]
        )
    
    imported = len(to_insert) + len(to_update)
    status = "failed" if imported == 0 and skipped > 0 else "partial" if skipped > 0 else "success"
    
    return ImportResponse(
        status=status,
        imported=imported,
        skipped=skipped,
        errors=errors
    )