from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Aplicación
    APP_NAME: str = "AcuBat Pricing Platform"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Base de datos
    DATABASE_URL: str = "postgresql://user:password@localhost/acubat_pricing"
    
    # Seguridad
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
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
    S3_SECURE: bool = True
    
    # API Keys
    API_KEY_HEADER: str = "x-api-key"
    API_KEY_PREFIX: str = "acubat_"
    API_SECRET: str = "your-secret-key-here"
    
    # Límites
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    MAX_UPLOAD_FILES: int = 10
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Entorno
    ENV: str = "development"
    
    # QA Gates
    QA_GLOBAL_THRESHOLD: float = 0.08
    QA_SKU_THRESHOLD: float = 0.15
    AUTO_PUBLISH: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()

# Configuración específica por entorno
if os.getenv("ENVIRONMENT") == "production":
    settings.DEBUG = False
    settings.ALLOWED_ORIGINS = [
        "https://acubat-pricing.vercel.app",
        "https://acubat-pricing.railway.app"
    ]
elif os.getenv("ENVIRONMENT") == "development":
    settings.DEBUG = True
