from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from .common import StatusEnum, ChannelEnum, PaginationParams

class UploadRequest(BaseModel):
    tenant_id: str = Field(..., description="ID del tenant")

class UploadResponse(BaseModel):
    id: str
    filename: str
    storage_url: str
    normalized_items_count: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True

class SimulateRequest(BaseModel):
    tenant_id: str = Field(..., description="ID del tenant")
    list_id: str = Field(..., description="ID de la lista de precios")
    ruleset_id: str = Field(..., description="ID del ruleset a aplicar")

class SimulateResponse(BaseModel):
    id: str
    list_id: str
    ruleset_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    summary: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True

class PublishRequest(BaseModel):
    run_id: str = Field(..., description="ID de la ejecución")
    canal: str = Field(..., description="Canal de publicación")

class PublishResponse(BaseModel):
    id: str
    run_id: str
    canal: str
    export_url: str
    changelog: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class PriceItemInput(BaseModel):
    sku: str
    marca: str
    linea: str
    base_price: float
    cost: float
    attrs: Dict[str, Any] = Field(default_factory=dict)

class PriceItemOutput(BaseModel):
    final_price: float = Field(..., description="Precio final")
    markup_applied: float = Field(..., description="Markup aplicado")
    profit_margin: float = Field(..., description="Margen de ganancia")

class PriceItemBreakdown(BaseModel):
    cost: float = Field(..., description="Costo")
    markup: float = Field(..., description="Markup")
    markup_amount: float = Field(..., description="Monto del markup")
    final_price: float = Field(..., description="Precio final")

class PriceItemResponse(BaseModel):
    id: str
    sku: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    breakdown: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class RunResponse(BaseModel):
    id: str
    list_id: str
    ruleset_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    summary: Dict[str, Any]
    items: List[PriceItemResponse]

    class Config:
        from_attributes = True

class RunItemResponse(BaseModel):
    id: str
    sku: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    breakdown: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
