import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.models import ListRaw, Ruleset, Tenant
from app.services.simulator import pricing_simulator
from app.schemas.pricing import SimulateRequest, SimulateResponse
from app.schemas.common import ErrorResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/simulate", response_model=SimulateResponse)
async def simulate_pricing(
    request: SimulateRequest,
    db: Session = Depends(get_db)
):
    """
    Ejecuta una simulación de pricing
    
    - **tenant_id**: ID del tenant
    - **list_id**: ID de la lista de precios
    - **ruleset_id**: ID del ruleset a aplicar
    """
    try:
        # Validar tenant
        tenant = db.query(Tenant).filter(Tenant.id == request.tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant no encontrado")
        
        # Validar lista
        list_raw = db.query(ListRaw).filter(
            ListRaw.id == request.list_id,
            ListRaw.tenant_id == request.tenant_id
        ).first()
        if not list_raw:
            raise HTTPException(status_code=404, detail="Lista no encontrada")
        
        # Validar ruleset
        ruleset = db.query(Ruleset).filter(
            Ruleset.id == request.ruleset_id,
            Ruleset.tenant_id == request.tenant_id,
            Ruleset.is_active == True
        ).first()
        if not ruleset:
            raise HTTPException(status_code=404, detail="Ruleset no encontrado o inactivo")
        
        # Ejecutar simulación
        price_run = pricing_simulator.run_simulation(
            db=db,
            tenant_id=request.tenant_id,
            list_id=request.list_id,
            ruleset_id=request.ruleset_id
        )
        
        logger.info(f"Simulación iniciada: {price_run.id}")
        
        return SimulateResponse(
            id=price_run.id,
            list_id=price_run.list_id,
            ruleset_id=price_run.ruleset_id,
            status=price_run.status,
            created_at=price_run.created_at,
            completed_at=price_run.completed_at,
            summary=price_run.resumen
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en simulación: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/simulate/{run_id}", response_model=SimulateResponse)
async def get_simulation_status(
    run_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado de una simulación
    """
    from app.db.models import PriceRun
    
    price_run = db.query(PriceRun).filter(PriceRun.id == run_id).first()
    if not price_run:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")
    
    return SimulateResponse(
        id=price_run.id,
        list_id=price_run.list_id,
        ruleset_id=price_run.ruleset_id,
        status=price_run.status,
        created_at=price_run.created_at,
        completed_at=price_run.completed_at,
        summary=price_run.resumen
    )
