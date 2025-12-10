from sqlalchemy import Column, String, Numeric, DateTime, func
from geoalchemy2 import Geometry

from app.database import Base


class WifiPoint(Base):
    """Representa un punto de acceso WiFi en la CDMX."""
    
    __tablename__ = "wifi_points"
    
    id = Column(String(100), primary_key=True)
    programa = Column(String(255), nullable=False)
    latitud = Column(Numeric(10, 6), nullable=False)
    longitud = Column(Numeric(10, 6), nullable=False)
    alcaldia = Column(String(100), nullable=False)
    location = Column(Geometry("POINT", srid=4326))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<WifiPoint(id={self.id}, alcaldia={self.alcaldia})>"