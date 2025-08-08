from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from sqlalchemy.engine.url import make_url
import logging
import re

logger = logging.getLogger(__name__)

# Sanitizar DATABASE_URL si el puerto no es numérico
raw_url = settings.DATABASE_URL

def _fix_port_with_regex(url: str) -> str:
    # Reemplaza el primer segmento ":<algo no numérico>/" por ":5432/"
    fixed = re.sub(r":[^/@]+(/|$)", r":5432\1", url, count=1)
    if fixed != url:
        logger.warning("DATABASE_URL tenía un puerto inválido; reemplazado por 5432 mediante regex")
    return fixed

try:
    url_obj = make_url(raw_url)
    try:
        _ = url_obj.port  # valida puerto
        database_url = str(url_obj)
    except ValueError:
        logger.warning("DATABASE_URL contiene puerto no numérico; usando 5432 por defecto (parsed)")
        url_obj = url_obj.set(port=5432)
        database_url = str(url_obj)
except Exception:
    # Si no se puede parsear, intentar fix por regex y reintentar parseo
    logger.warning("DATABASE_URL inválida al parsear; intentando corregir puerto por regex")
    fixed = _fix_port_with_regex(raw_url)
    try:
        url_obj = make_url(fixed)
        database_url = str(url_obj)
    except Exception:
        logger.error("DATABASE_URL sigue siendo inválida tras corrección; usando valor corregido directamente")
        database_url = fixed

# Crear engine de SQLAlchemy
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=300,
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
