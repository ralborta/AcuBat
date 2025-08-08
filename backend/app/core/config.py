import os
import sys
import logging
from typing import List, Optional
from pydantic_settings import BaseSettings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Aplicación
    APP_NAME: str = "AcuBat Pricing Platform"
    DEBUG: str = "False"
    VERSION: str = "1.0.0"
    
    # Base de datos
    DATABASE_URL: str = "postgresql://user:password@localhost/acubat_pricing"
    
    # Seguridad
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: str = "30"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # Almacenamiento (S3)
    S3_ENDPOINT: str = "https://s3.amazonaws.com"
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_BUCKET: str = "acubat-pricing"
    S3_SECURE: str = "True"
    
    # API Keys
    API_KEY_HEADER: str = "x-api-key"
    API_KEY_PREFIX: str = "acubat_"
    API_SECRET: str = "your-secret-key-here"
    
    # Límites
    MAX_FILE_SIZE: str = "52428800"  # 50MB en bytes
    MAX_UPLOAD_FILES: str = "10"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Entorno
    ENV: str = "development"
    
    # QA Gates
    QA_GLOBAL_THRESHOLD: str = "0.08"
    QA_SKU_THRESHOLD: str = "0.15"
    AUTO_PUBLISH: str = "False"
    
    # Puerto
    PORT: str = "8000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_debug(self) -> bool:
        """Obtiene el valor de DEBUG como boolean"""
        try:
            return self.DEBUG.lower() in ('true', '1', 'yes', 'on')
        except (AttributeError, ValueError):
            return False
    
    def get_port(self) -> int:
        """Obtiene el puerto de forma segura"""
        try:
            port = int(self.PORT)
            if 1 <= port <= 65535:
                return port
            else:
                logger.warning(f"Puerto {port} fuera de rango válido (1-65535), usando 8000")
                return 8000
        except (ValueError, TypeError):
            logger.warning(f"Puerto '{self.PORT}' no es numérico, usando 8000")
            return 8000
    
    def get_max_file_size(self) -> int:
        """Obtiene el tamaño máximo de archivo como int"""
        try:
            return int(self.MAX_FILE_SIZE)
        except (ValueError, TypeError):
            logger.warning(f"MAX_FILE_SIZE '{self.MAX_FILE_SIZE}' no es numérico, usando 50MB")
            return 50 * 1024 * 1024
    
    def get_max_upload_files(self) -> int:
        """Obtiene el número máximo de archivos como int"""
        try:
            return int(self.MAX_UPLOAD_FILES)
        except (ValueError, TypeError):
            logger.warning(f"MAX_UPLOAD_FILES '{self.MAX_UPLOAD_FILES}' no es numérico, usando 10")
            return 10
    
    def get_access_token_expire_minutes(self) -> int:
        """Obtiene el tiempo de expiración del token como int"""
        try:
            return int(self.ACCESS_TOKEN_EXPIRE_MINUTES)
        except (ValueError, TypeError):
            logger.warning(f"ACCESS_TOKEN_EXPIRE_MINUTES '{self.ACCESS_TOKEN_EXPIRE_MINUTES}' no es numérico, usando 30")
            return 30
    
    def get_qa_global_threshold(self) -> float:
        """Obtiene el umbral global de QA como float"""
        try:
            return float(self.QA_GLOBAL_THRESHOLD)
        except (ValueError, TypeError):
            logger.warning(f"QA_GLOBAL_THRESHOLD '{self.QA_GLOBAL_THRESHOLD}' no es numérico, usando 0.08")
            return 0.08
    
    def get_qa_sku_threshold(self) -> float:
        """Obtiene el umbral de SKU de QA como float"""
        try:
            return float(self.QA_SKU_THRESHOLD)
        except (ValueError, TypeError):
            logger.warning(f"QA_SKU_THRESHOLD '{self.QA_SKU_THRESHOLD}' no es numérico, usando 0.15")
            return 0.15
    
    def get_auto_publish(self) -> bool:
        """Obtiene el valor de AUTO_PUBLISH como boolean"""
        try:
            return self.AUTO_PUBLISH.lower() in ('true', '1', 'yes', 'on')
        except (AttributeError, ValueError):
            return False
    
    def get_s3_secure(self) -> bool:
        """Obtiene el valor de S3_SECURE como boolean"""
        try:
            return self.S3_SECURE.lower() in ('true', '1', 'yes', 'on')
        except (AttributeError, ValueError):
            return True
    
    def validate_required_env_vars(self):
        """Valida que las variables de entorno requeridas estén presentes"""
        required_vars = {
            'DATABASE_URL': self.DATABASE_URL,
            'SECRET_KEY': self.SECRET_KEY,
            'API_SECRET': self.API_SECRET
        }
        
        missing_vars = []
        for var_name, var_value in required_vars.items():
            if not var_value or var_value in ['your-secret-key-here', 'postgresql://user:password@localhost/acubat_pricing']:
                missing_vars.append(var_name)
        
        if missing_vars:
            error_msg = f"Variables de entorno requeridas faltantes o con valores por defecto: {', '.join(missing_vars)}"
            logger.error(error_msg)
            logger.error("Por favor, configura estas variables en tu archivo .env o variables de entorno")
            sys.exit(1)
    
    def log_configuration_summary(self):
        """Loguea un resumen de la configuración (sin información sensible)"""
        logger.info("=== RESUMEN DE CONFIGURACIÓN ===")
        logger.info(f"Entorno: {self.ENV}")
        logger.info(f"Modo Debug: {self.get_debug()}")
        logger.info(f"Puerto: {self.get_port()}")
        logger.info(f"CORS Origins: {self.CORS_ORIGINS}")
        logger.info(f"S3 Bucket: {self.S3_BUCKET}")
        logger.info(f"Log Level: {self.LOG_LEVEL}")
        logger.info(f"Max File Size: {self.get_max_file_size() // (1024*1024)}MB")
        logger.info(f"Max Upload Files: {self.get_max_upload_files()}")
        logger.info("================================")

def create_settings() -> Settings:
    """Crea y valida la configuración"""
    try:
        settings = Settings()
        settings.validate_required_env_vars()
        settings.log_configuration_summary()
        return settings
    except Exception as e:
        logger.error(f"Error al cargar la configuración: {e}")
        sys.exit(1)

# Instancia global de configuración
settings = create_settings()

# Configuración específica por entorno
if os.getenv("ENVIRONMENT") == "production":
    settings.ENV = "production"
elif os.getenv("ENVIRONMENT") == "development":
    settings.ENV = "development"
