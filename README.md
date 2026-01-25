# WiFi CDMX API

API para consultar los puntos de acceso WiFi gratuitos en la Ciudad de México. Básicamente es un backend que te permite buscar puntos cercanos, filtrar por alcaldía y cargar datos desde archivos CSV o Excel.

Lo hice con FastAPI porque es rápido de desarrollar y tiene buena documentación automática. Para las consultas geográficas uso PostGIS que es muy útil para calcular distancias.

## ¿Qué hace?

- Guarda info de puntos WiFi (id, programa, latitud, longitud, alcaldía)
- Busca puntos cercanos a una ubicación dada
- Filtra por alcaldía
- Importa datos masivos desde CSV/Excel
- Todo paginado para no saturar las respuestas

## Tech stack

- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **PostGIS** - Extensión de PostgreSQL para datos geográficos
- **Pydantic** - Validación de datos
- **Pandas** - Para leer los archivos CSV/Excel

## Cómo correrlo

### Opción 1: Docker

Requisitos: Docker y docker compose.

1. Construye y levanta todo (API + PostGIS):

```bash
docker compose up -d --build
```

1. Espera unos segundos a que la BD pase el healthcheck y abre la doc: [http://localhost:8000/docs](http://localhost:8000/docs)

Logs en vivo de la API:

```bash
docker compose logs -f api
```

Para parar todo:

```bash
docker compose down
```

### Opción 2: Local

Requisitos: Python 3.10+ y Docker solo para la BD.

1. Levanta solo la base:

```bash
docker compose up -d db
```

1. Instala dependencias (mejor en un virtualenv):

```bash
pip install -r requirements.txt
```

1. Arranca la API:

```bash
uvicorn app.main:app --reload
```

1. Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Endpoints principales

| Método | Ruta | Qué hace |
|--------|------|----------|
| GET | `/api/v1/wifi-points` | Lista todos los puntos (paginado) |
| GET | `/api/v1/wifi-points/{id}` | Obtiene un punto específico |
| GET | `/api/v1/wifi-points/alcaldia/{alcaldia}` | Filtra por alcaldía |
| GET | `/api/v1/wifi-points/nearby/?lat=...&lng=...` | Puntos cercanos ordenados por distancia |
| POST | `/api/v1/wifi-points/import` | Importa desde CSV/Excel |

### Sobre la importación

El endpoint de importación acepta archivos CSV o Excel. Las columnas requeridas son:

- `id` - Identificador único
- `programa` - Nombre del programa
- `latitud` - Pues eso, la latitud
- `longitud` - Y la longitud
- `alcaldia` - La alcaldía donde está

Parámetros opcionales:

- `on_error`: qué hacer si hay errores (`fail`, `skip`, `report`)
- `on_duplicate`: qué hacer con duplicados (`fail`, `skip`, `update`)

## Estructura del proyecto

```text
app/
├── api/          # Rutas de FastAPI
├── models/       # Modelos de SQLAlchemy
├── repositories/ # Acceso a datos
├── schemas/      # Esquemas Pydantic
├── services/     # Lógica de negocio
└── utils/        # Utilidades varias
scripts/          # Scripts para cargar datos
tests/            # Tests (hay algunos básicos)
```

## Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/wifi_cdmx` | URL de conexión a la BD |

## Tests

Hay algunos tests básicos que puedes correr con:

```bash
pytest
```

Todavía faltan más tests pero bueno, es lo que hay por ahora.

## Cosas pendientes / mejoras futuras

- [ ] Agregar más tests
- [ ] Configurar CI/CD
- [ ] Agregar autenticación si se necesita
- [ ] Cachear consultas frecuentes redis

## Notas técnicas

- Las coordenadas se guardan como geometría POINT con SRID 4326
- La distancia se calcula con `ST_DistanceSphere` que da metros

---

Cualquier duda o sugerencia, estoy pendiente 👍
