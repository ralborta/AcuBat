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
