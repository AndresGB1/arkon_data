"""
Punto de entrada de la aplicación FastAPI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.wifi import router as wifi_router


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wifi_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def root():
    """Endpoint de bienvenida."""
    return {
        "message": "WiFi CDMX API",
        "version": settings.api_version,
        "docs": "/docs"
    }
