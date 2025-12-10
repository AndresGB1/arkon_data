import pandas as pd
from io import BytesIO


def read_file(content: bytes, filename: str) -> pd.DataFrame:
    """
    Lee un archivo CSV o Excel y retorna un DataFrame.
    """
    buffer = BytesIO(content)
    
    if filename.endswith(".csv"):
        try:
            return pd.read_csv(buffer, encoding="utf-8")
        except:
            buffer.seek(0) 
            try:
                return pd.read_csv(buffer, encoding="latin-1")
            except:
                buffer.seek(0)
                return pd.read_csv(buffer, encoding="utf-8", sep=";")
    
    elif filename.endswith((".xlsx", ".xls")):
        return pd.read_excel(buffer)
    
    else: 
        raise ValueError(f"Formato no soportado: {filename}")


def parse_decimal(value) -> float | None:
    """Convierte string a float, manejando comas como decimales."""
    if pd.isna(value):
        return None
    try:
        return float(str(value).replace(",", "."))
    except (ValueError, TypeError):
        return None