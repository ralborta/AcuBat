from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from sqlalchemy.engine.url import make_url
import logging

logger = logging.getLogger(__name__)

# Sanitizar DATABASE_URL si el puerto no es numérico
raw_url = settings.DATABASE_URL
try:
    url_obj = make_url(raw_url)
    # url_obj.port puede disparar ValueError si no es numérico
    try:
        _ = url_obj.port  # fuerza parseo del puerto
    except ValueError:
        logger.warning("DATABASE_URL contiene puerto no numérico; usando 5432 por defecto")
        # reconstruir con puerto 5432
        url_obj = url_obj.set(port=5432)
    database_url = str(url_obj)
except Exception:
    logger.error("DATABASE_URL inválida; usando valor original y dejando que SQLAlchemy maneje el error")
    database_url = raw_url

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
