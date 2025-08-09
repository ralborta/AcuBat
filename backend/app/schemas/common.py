from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class StatusEnum(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ChannelEnum(str, Enum):
    MINORISTA = "minorista"
    MAYORISTA = "mayorista"

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Número de página")
    size: int = Field(default=50, ge=1, le=100, description="Tamaño de página")

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

class SuccessResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None

class TenantBase(BaseModel):
    nombre: str = Field(..., description="Nombre del tenant")
    tenant_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos del tenant")

class TenantCreate(TenantBase):
    pass

class TenantResponse(TenantBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str = Field(..., description="Email del usuario")
    rol: str = Field(default="viewer", description="Rol del usuario")

class UserCreate(UserBase):
    tenant_id: str

class UserResponse(UserBase):
    id: str
    tenant_id: str
    api_key: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
