from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging
import time
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

# Usar la URL original tal como viene de las variables de entorno.
# Evitamos reparsear/reformatear para no romper el percent-encoding de la contraseña.
database_url = settings.DATABASE_URL

# Crear engine de SQLAlchemy
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    # Para SQLite en memoria
    connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Función para obtener sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_db_connectivity(max_attempts: int = 30, delay_seconds: float = 2.0) -> None:
    """Bloquea el arranque hasta que la DB acepte conexiones o agote reintentos.

    Esto evita fallos al inicio cuando el contenedor del backend arranca antes
    de que PostgreSQL esté listo.
    """
    # Para SQLite en memoria, no necesitamos esperar
    if "sqlite" in database_url:
        logger.info("SQLite en memoria detectado - saltando verificación de conectividad")
        return
        
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Conexión a la base de datos verificada correctamente")
            return
        except Exception as exc:  # pragma: no cover - robustez en producción
            last_error = exc
            logger.warning(
                f"DB no lista aún (intento {attempt}/{max_attempts}): {exc}"
            )
            time.sleep(delay_seconds)

    logger.error(
        f"No se pudo establecer conexión con la DB tras {max_attempts} intentos: {last_error}"
    )
    # Re-lanzamos el último error para que el proceso falle explícitamente si la DB no está disponible
    if last_error:
        raise last_error


def create_demo_data():
    """Crea datos de ejemplo para la demo"""
    from app.db.models import Tenant, Product, Ruleset, ListRaw, NormalizedItem
    from datetime import datetime
    import uuid
    
    logger.info("Creando datos de ejemplo para la demo...")
    
    db = SessionLocal()
    try:
        # Crear tenant de demo
        demo_tenant = Tenant(
            id="demo-tenant-001",
            nombre="Demo Company",
            tenant_metadata={"industry": "Electronics", "region": "Latam"}
        )
        db.add(demo_tenant)
        
        # Crear productos de ejemplo
        demo_products = [
            Product(
                id=str(uuid.uuid4()),
                tenant_id=demo_tenant.id,
                sku="BAT-001",
                marca="Moura",
                linea="Automotriz",
                atributos={"capacidad": "60Ah", "tecnologia": "AGM"}
            ),
            Product(
                id=str(uuid.uuid4()),
                tenant_id=demo_tenant.id,
                sku="BAT-002", 
                marca="Moura",
                linea="Automotriz",
                atributos={"capacidad": "70Ah", "tecnologia": "AGM"}
            ),
            Product(
                id=str(uuid.uuid4()),
                tenant_id=demo_tenant.id,
                sku="BAT-003",
                marca="Varta",
                linea="Industrial",
                atributos={"capacidad": "100Ah", "tecnologia": "Gel"}
            )
        ]
        
        for product in demo_products:
            db.add(product)
        
        # Crear ruleset de ejemplo
        demo_ruleset = Ruleset(
            id="demo-ruleset-001",
            tenant_id=demo_tenant.id,
            nombre="Reglas Demo 2024",
            version="1.0",
            config={
                "markup_base": 0.25,
                "markup_automotriz": 0.30,
                "markup_industrial": 0.35,
                "descuentos": {
                    "volumen": 0.05,
                    "cliente_premium": 0.10
                }
            },
            is_active=True
        )
        db.add(demo_ruleset)
        
        # Crear lista de precios de ejemplo
        demo_list = ListRaw(
            id="demo-list-001",
            tenant_id=demo_tenant.id,
            filename="lista_precios_demo.xlsx",
            storage_url="demo://local/demo_list.xlsx",
            list_metadata={
                "file_size": 1024000,
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "original_filename": "lista_precios_demo.xlsx"
            }
        )
        db.add(demo_list)
        
        # Crear items normalizados de ejemplo
        demo_items = [
            NormalizedItem(
                id=str(uuid.uuid4()),
                list_id=demo_list.id,
                sku="BAT-001",
                marca="Moura",
                linea="Automotriz",
                base_price=150.00,
                cost=100.00,
                attrs={"capacidad": "60Ah", "tecnologia": "AGM"}
            ),
            NormalizedItem(
                id=str(uuid.uuid4()),
                list_id=demo_list.id,
                sku="BAT-002",
                marca="Moura", 
                linea="Automotriz",
                base_price=180.00,
                cost=120.00,
                attrs={"capacidad": "70Ah", "tecnologia": "AGM"}
            ),
            NormalizedItem(
                id=str(uuid.uuid4()),
                list_id=demo_list.id,
                sku="BAT-003",
                marca="Varta",
                linea="Industrial",
                base_price=250.00,
                cost=180.00,
                attrs={"capacidad": "100Ah", "tecnologia": "Gel"}
            )
        ]
        
        for item in demo_items:
            db.add(item)
        
        db.commit()
        logger.info("Datos de ejemplo creados exitosamente")
        
    except Exception as e:
        logger.error(f"Error creando datos de ejemplo: {e}")
        db.rollback()
    finally:
        db.close()
