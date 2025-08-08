import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.models import PriceRun, PriceItem, Tenant
from app.services.simulator import pricing_simulator
from app.schemas.pricing import RunResponse, RunsListResponse, PriceItemResponse
from app.schemas.common import PaginationParams, PaginatedResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run_details(
    run_id: str,
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles completos de un price run con paginación
    
    - **run_id**: ID del price run
    - **page**: Número de página (opcional, default: 1)
    - **size**: Tamaño de página (opcional, default: 50, max: 100)
    """
    try:
        # Obtener price run
        price_run = db.query(PriceRun).filter(PriceRun.id == run_id).first()
        if not price_run:
            raise HTTPException(status_code=404, detail="Price run no encontrado")
        
        # Obtener resumen
        summary = pricing_simulator.get_run_summary(db, run_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Resumen no encontrado")
        
        # Obtener price items con paginación
        skip = (page - 1) * size
        price_items = pricing_simulator.get_price_items(db, run_id, skip, size)
        
        # Convertir a PriceItemResponse
        items_response = []
        for item in price_items:
            items_response.append(PriceItemResponse(
                id=item.id,
                sku=item.sku,
                inputs=item.inputs,
                outputs=item.outputs,
                breakdown=item.breakdown,
                created_at=item.created_at
            ))
        
        return RunResponse(
            id=price_run.id,
            list_id=price_run.list_id,
            ruleset_id=price_run.ruleset_id,
            status=price_run.status,
            created_at=price_run.created_at,
            completed_at=price_run.completed_at,
            summary=summary,
            items=items_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo detalles del run: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/runs", response_model=RunsListResponse)
async def list_runs(
    tenant_id: str = Query(..., description="ID del tenant"),
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    """
    Lista los price runs de un tenant con paginación
    
    - **tenant_id**: ID del tenant
    - **page**: Número de página (opcional, default: 1)
    - **size**: Tamaño de página (opcional, default: 50, max: 100)
    """
    try:
        # Validar tenant
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant no encontrado")
        
        # Obtener runs del tenant (a través de las listas)
        from app.db.models import ListRaw
        
        # Query compleja para obtener runs del tenant
        runs_query = db.query(PriceRun).join(
            ListRaw, PriceRun.list_id == ListRaw.id
        ).filter(ListRaw.tenant_id == tenant_id)
        
        # Contar total
        total = runs_query.count()
        
        # Paginar
        skip = (page - 1) * size
        runs = runs_query.offset(skip).limit(size).all()
        
        # Convertir a SimulateResponse
        items = []
        for run in runs:
            items.append({
                "id": run.id,
                "list_id": run.list_id,
                "ruleset_id": run.ruleset_id,
                "status": run.status,
                "created_at": run.created_at,
                "completed_at": run.completed_at,
                "summary": run.resumen
            })
        
        # Calcular páginas
        pages = (total + size - 1) // size
        
        return RunsListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listando runs: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
