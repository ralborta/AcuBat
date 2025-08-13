import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.models import PriceRun, PriceItem, ListRaw, Ruleset, Tenant
from app.schemas.pricing import RunResponse, RunItemResponse
from app.schemas.common import ErrorResponse
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run_details(
    run_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles de una ejecución de pricing
    """
    price_run = db.query(PriceRun).filter(PriceRun.id == run_id).first()
    if not price_run:
        raise HTTPException(status_code=404, detail="Ejecución no encontrada")
    
    # Obtener items del run
    items = db.query(PriceItem).filter(PriceItem.run_id == run_id).all()
    
    return RunResponse(
        id=price_run.id,
        list_id=price_run.list_id,
        ruleset_id=price_run.ruleset_id,
        status=price_run.status,
        created_at=price_run.created_at,
        completed_at=price_run.completed_at,
        summary=price_run.resumen,
        items=[
            RunItemResponse(
                id=item.id,
                sku=item.sku,
                inputs=item.inputs,
                outputs=item.outputs,
                breakdown=item.breakdown,
                created_at=item.created_at
            )
            for item in items
        ]
    )

@router.get("/runs/tenant/{tenant_id}", response_model=List[RunResponse])
async def get_tenant_runs(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las ejecuciones de un tenant
    """
    # Validar tenant
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    
    # Obtener runs del tenant
    runs = db.query(PriceRun).join(ListRaw).filter(ListRaw.tenant_id == tenant_id).all()
    
    result = []
    for run in runs:
        # Obtener items del run
        items = db.query(PriceItem).filter(PriceItem.run_id == run.id).all()
        
        result.append(RunResponse(
            id=run.id,
            list_id=run.list_id,
            ruleset_id=run.ruleset_id,
            status=run.status,
            created_at=run.created_at,
            completed_at=run.completed_at,
            summary=run.resumen,
            items=[
                RunItemResponse(
                    id=item.id,
                    sku=item.sku,
                    inputs=item.inputs,
                    outputs=item.outputs,
                    breakdown=item.breakdown,
                    created_at=item.created_at
                )
                for item in items
            ]
        ))
    
    return result

@router.get("/runs/list/{list_id}", response_model=List[RunResponse])
async def get_list_runs(
    list_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las ejecuciones de una lista específica
    """
    # Validar lista
    list_raw = db.query(ListRaw).filter(ListRaw.id == list_id).first()
    if not list_raw:
        raise HTTPException(status_code=404, detail="Lista no encontrada")
    
    # Obtener runs de la lista
    runs = db.query(PriceRun).filter(PriceRun.list_id == list_id).all()
    
    result = []
    for run in runs:
        # Obtener items del run
        items = db.query(PriceItem).filter(PriceItem.run_id == run.id).all()
        
        result.append(RunResponse(
            id=run.id,
            list_id=run.list_id,
            ruleset_id=run.ruleset_id,
            status=run.status,
            created_at=run.created_at,
            completed_at=run.completed_at,
            summary=run.resumen,
            items=[
                RunItemResponse(
                    id=item.id,
                    sku=item.sku,
                    inputs=item.inputs,
                    outputs=item.outputs,
                    breakdown=item.breakdown,
                    created_at=item.created_at
                )
                for item in items
            ]
        ))
    
    return result

@router.delete("/runs/{run_id}")
async def delete_run(
    run_id: str,
    db: Session = Depends(get_db)
):
    """
    Elimina una ejecución de pricing
    """
    price_run = db.query(PriceRun).filter(PriceRun.id == run_id).first()
    if not price_run:
        raise HTTPException(status_code=404, detail="Ejecución no encontrada")
    
    # Eliminar items del run
    db.query(PriceItem).filter(PriceItem.run_id == run_id).delete()
    
    # Eliminar el run
    db.delete(price_run)
    db.commit()
    
    return {"message": "Ejecución eliminada exitosamente"}
