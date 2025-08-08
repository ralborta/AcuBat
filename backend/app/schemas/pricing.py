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
    tenant_id: str
    created_at: datetime
    normalized_items_count: int

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
    status: StatusEnum
    created_at: datetime
    completed_at: Optional[datetime] = None
    summary: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True

class PublishRequest(BaseModel):
    tenant_id: str = Field(..., description="ID del tenant")
    run_id: str = Field(..., description="ID de la simulación")
    channel: ChannelEnum = Field(..., description="Canal de publicación")
    changelog: Optional[str] = Field(None, description="Descripción de cambios")

class PublishResponse(BaseModel):
    id: str
    run_id: str
    channel: ChannelEnum
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
    K: float = Field(..., description="Precio neto")
    P: float = Field(..., description="Precio después de comisiones")
    markup: float = Field(..., description="Markup (Q)")
    rentabilidad: float = Field(..., description="Rentabilidad (R)")
    precio_publico: float = Field(..., description="Precio público final")
    precio_publico_sin_iva: float = Field(..., description="Precio público sin IVA")

class PriceItemBreakdown(BaseModel):
    desc1: float = Field(..., description="Descuento 1")
    desc_contado: float = Field(..., description="Descuento contado")
    L: float = Field(..., description="Comisión L")
    M: float = Field(..., description="Comisión M")
    N: float = Field(..., description="Comisión N")
    IVA: float = Field(..., description="IVA aplicado")
    precio_lista: float = Field(..., description="Precio lista")
    neto1: float = Field(..., description="Neto 1")
    precio_publico_bruto: float = Field(..., description="Precio público bruto")

class PriceItemResponse(BaseModel):
    id: str
    sku: str
    inputs: PriceItemInput
    outputs: PriceItemOutput
    breakdown: PriceItemBreakdown
    created_at: datetime

    class Config:
        from_attributes = True

class RunSummary(BaseModel):
    total_items: int
    cambio_promedio: float = Field(..., description="Cambio promedio en %")
    skus_afectados: int = Field(..., description="SKUs con cambios")
    skus_bloqueados_por_gate: int = Field(..., description="SKUs bloqueados por QA gate")
    margen_promedio: float = Field(..., description="Margen promedio")
    rentabilidad_promedio: float = Field(..., description="Rentabilidad promedio")

class RunResponse(BaseModel):
    id: str
    list_id: str
    ruleset_id: str
    status: StatusEnum
    created_at: datetime
    completed_at: Optional[datetime]
    summary: RunSummary
    items: List[PriceItemResponse]

    class Config:
        from_attributes = True

class RunsListResponse(BaseModel):
    items: List[SimulateResponse]
    total: int
    page: int
    size: int
    pages: int
