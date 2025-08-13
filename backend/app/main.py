from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
# from app.core.security import get_current_user
from app.api import routes_upload, routes_simulate, routes_publish, routes_runs
from app.db.base import engine, wait_for_db_connectivity, create_demo_data
from app.db.models import Base, Tenant
from sqlalchemy.orm import Session
from app.db.base import get_db
import uuid

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Esperar a que la DB esté lista y luego crear tablas
wait_for_db_connectivity()
Base.metadata.create_all(bind=engine)

# Crear datos de ejemplo si estamos en modo demo
if "sqlite" in str(engine.url):
    create_demo_data()

# Crear aplicación FastAPI
app = FastAPI(
    title="AcuBat Pricing Platform API",
    description="API para la plataforma de pricing parametrizable y multi-producto",
    version="1.0.0",
    docs_url="/docs" if settings.get_debug() else None,
    redoc_url="/redoc" if settings.get_debug() else None,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(routes_upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(routes_simulate.router, prefix="/api/v1", tags=["simulate"])
app.include_router(routes_publish.router, prefix="/api/v1", tags=["publish"])
app.include_router(routes_runs.router, prefix="/api/v1", tags=["runs"])

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "AcuBat Pricing Platform API",
        "version": "1.0.0",
        "status": "running",
        "demo_mode": "sqlite" in str(engine.url)
    }

@app.get("/health")
async def health_check():
    """Health check para monitoreo"""
    from datetime import datetime
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "database": "sqlite" if "sqlite" in str(engine.url) else "postgresql"
    }

@app.get("/demo/data")
async def get_demo_data():
    """Endpoint para obtener información de datos de demo"""
    return {
        "tenant_id": "demo-tenant-001",
        "list_id": "demo-list-001", 
        "ruleset_id": "demo-ruleset-001",
        "products": [
            {"sku": "BAT-001", "marca": "Moura", "linea": "Automotriz", "precio_base": 150.00, "costo": 100.00},
            {"sku": "BAT-002", "marca": "Moura", "linea": "Automotriz", "precio_base": 180.00, "costo": 120.00},
            {"sku": "BAT-003", "marca": "Varta", "linea": "Industrial", "precio_base": 250.00, "costo": 180.00}
        ],
        "ruleset": {
            "nombre": "Reglas Demo 2024",
            "markup_base": 0.25,
            "markup_automotriz": 0.30,
            "markup_industrial": 0.35
        }
    }

@app.post("/create-tenant")
async def create_tenant_endpoint(
    tenant_data: dict,
    db: Session = Depends(get_db)
):
    """Endpoint temporal para crear tenants en Railway"""
    try:
        tenant_id = tenant_data.get("id", f"tenant-{uuid.uuid4()}")
        tenant_name = tenant_data.get("nombre", "Tenant Default")
        
        # Verificar si ya existe
        existing = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if existing:
            return {"message": "Tenant ya existe", "tenant_id": existing.id}
        
        # Crear nuevo tenant
        tenant = Tenant(
            id=tenant_id,
            nombre=tenant_name,
            tenant_metadata=tenant_data.get("metadata", {})
        )
        
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        
        logger.info(f"Tenant creado: {tenant.id}")
        
        return {
            "message": "Tenant creado exitosamente",
            "tenant_id": tenant.id,
            "nombre": tenant.nombre
        }
        
    except Exception as e:
        logger.error(f"Error creando tenant: {e}")
        raise HTTPException(status_code=500, detail=f"Error creando tenant: {str(e)}")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones"""
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.get_port(),
        reload=settings.get_debug()
    )
