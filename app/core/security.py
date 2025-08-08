"""
Módulo de seguridad para autenticación y autorización
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Esquema de autenticación
security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Valida el API key del usuario actual
    """
    if not credentials:
        # Para desarrollo, permitir acceso sin API key
        if settings.DEBUG:
            return "dev-user"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key requerida",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = credentials.credentials
    
    # Validación básica del API key
    if not api_key or not api_key.startswith(settings.API_KEY_PREFIX):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # TODO: Implementar validación completa contra base de datos
    # Por ahora, solo validamos el formato
    logger.info(f"Usuario autenticado con API key: {api_key[:10]}...")
    return api_key

def verify_api_key(api_key: str) -> bool:
    """
    Verifica si un API key es válido
    """
    if not api_key:
        return False
    
    if not api_key.startswith(settings.API_KEY_PREFIX):
        return False
    
    # TODO: Implementar validación contra base de datos
    return True
