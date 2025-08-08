# AcuBat Pricing Platform - Backend

Backend de la plataforma de pricing parametrizable construido con FastAPI, SQLAlchemy y PostgreSQL.

## 🚀 Características

- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para base de datos
- **PostgreSQL**: Base de datos principal
- **S3/MinIO**: Almacenamiento de archivos
- **Motor de reglas**: Sistema configurable de pricing
- **Multi-tenant**: Soporte para múltiples clientes
- **API RESTful**: Endpoints bien documentados

## 📁 Estructura

```
backend/
├── app/
│   ├── main.py              # Aplicación principal FastAPI
│   ├── api/                 # Endpoints de la API
│   │   ├── routes_upload.py
│   │   ├── routes_simulate.py
│   │   ├── routes_publish.py
│   │   └── routes_runs.py
│   ├── core/                # Configuración y utilidades
│   │   ├── config.py
│   │   └── security.py
│   ├── db/                  # Base de datos
│   │   ├── base.py
│   │   └── models.py
│   ├── services/            # Lógica de negocio
│   │   ├── storage.py
│   │   ├── parser.py
│   │   ├── rules_engine.py
│   │   ├── simulator.py
│   │   └── publisher.py
│   ├── schemas/             # Esquemas Pydantic
│   │   ├── common.py
│   │   ├── ruleset.py
│   │   └── pricing.py
│   └── utils/               # Utilidades
│       └── rounding.py
├── tests/                   # Tests
├── requirements.txt         # Dependencias Python
├── Dockerfile              # Imagen Docker
├── init_db.py              # Script de inicialización
└── README.md               # Este archivo
```

## 🛠️ Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp env.example .env
# Editar .env con tus valores
```

### 3. Base de datos

#### Desarrollo local (Docker Compose)

```bash
# Levantar PostgreSQL y MinIO
docker compose -f ../docker-compose.dev.yml up -d

# Inicializar base de datos
python init_db.py
```

#### Producción (Railway)

```bash
# Ejecutar migraciones
alembic upgrade head

# Inicializar datos
python init_db.py
```

### 4. Ejecutar servidor

```bash
# Desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🗄️ Migraciones

### Crear nueva migración

```bash
alembic revision --autogenerate -m "Descripción del cambio"
```

### Aplicar migraciones

```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Aplicar hasta una versión específica
alembic upgrade <revision_id>

# Revertir última migración
alembic downgrade -1
```

### Ver estado de migraciones

```bash
# Ver historial
alembic history

# Ver estado actual
alembic current

# Ver migraciones pendientes
alembic show <revision_id>
```

## 🧪 Testing

### Ejecutar tests

```bash
# Todos los tests
pytest

# Tests con coverage
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_rules_engine.py -v
```

### Tests disponibles

- `test_rules_engine.py`: Tests del motor de reglas
- `test_api.py`: Tests de endpoints API
- `test_parser.py`: Tests del parser de Excel

## 🚀 Deploy

### Railway

1. Conectar repositorio GitHub
2. Configurar variables de entorno
3. Deploy automático

### Variables de entorno requeridas

```bash
DATABASE_URL=postgresql://...
S3_ENDPOINT=https://s3.amazonaws.com
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_BUCKET=acubat-pricing
API_SECRET=your-secret
CORS_ORIGINS=https://your-frontend.vercel.app
ENV=production
```

## 📚 API Documentation

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`

## 🔧 Desarrollo

### Estructura de datos

#### Tenant
```python
{
    "id": "uuid",
    "nombre": "AcuBat",
    "metadata": {
        "qa_gates": {
            "global_threshold": 0.08,
            "sku_threshold": 0.15,
            "auto_publish": False
        }
    }
}
```

#### Ruleset
```python
{
    "name": "moura_base",
    "version": "v1",
    "globals": {
        "IVA": 0.21,
        "L": 0.05,
        "M": 0.00,
        "N": 0.00,
        "roundingPublic": "ceil50"
    },
    "steps": [...],
    "overrides": [...]
}
```

### Endpoints principales

- `POST /api/v1/upload`: Subir archivo Excel
- `POST /api/v1/simulate`: Ejecutar simulación
- `GET /api/v1/runs/{id}`: Obtener resultados
- `POST /api/v1/publish`: Publicar resultados
- `GET /api/v1/export.csv`: Descargar CSV

## 🚨 Troubleshooting

### Error de conexión a base de datos

```bash
# Verificar DATABASE_URL
echo $DATABASE_URL

# Probar conexión
python -c "from app.db.base import engine; print(engine.execute('SELECT 1').scalar())"
```

### Error de S3

```bash
# Verificar credenciales
python -c "from app.services.storage import storage_service; print(storage_service.client.list_buckets())"
```

### Logs detallados

```bash
# Activar debug
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/TU_USUARIO/acubat-pricing-platform/issues)
- **Documentación**: [README.md](../README.md)
