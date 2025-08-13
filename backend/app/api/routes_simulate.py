import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.models import ListRaw, Ruleset, Tenant, PriceRun, PriceItem
from app.services.simulator import pricing_simulator
from app.schemas.pricing import SimulateRequest, SimulateResponse
from app.schemas.common import ErrorResponse
from datetime import datetime
import uuid

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
        
        # Crear price run
        price_run = PriceRun(
            id=str(uuid.uuid4()),
            list_id=request.list_id,
            ruleset_id=request.ruleset_id,
            status="running",
            resumen={},
            created_at=datetime.utcnow()
        )
        db.add(price_run)
        db.commit()
        db.refresh(price_run)
        
        # Simular cálculo de precios (demo)
        try:
            # Obtener items normalizados
            from app.db.models import NormalizedItem
            items = db.query(NormalizedItem).filter(NormalizedItem.list_id == request.list_id).all()
            
            # Aplicar reglas de pricing
            for item in items:
                # Calcular markup según línea
                markup = ruleset.config.get("markup_base", 0.25)
                if item.linea == "Automotriz":
                    markup = ruleset.config.get("markup_automotriz", 0.30)
                elif item.linea == "Industrial":
                    markup = ruleset.config.get("markup_industrial", 0.35)
                
                # Calcular precio final
                precio_final = item.cost * (1 + markup)
                
                # Crear price item
                price_item = PriceItem(
                    id=str(uuid.uuid4()),
                    run_id=price_run.id,
                    sku=item.sku,
                    inputs={
                        "base_price": item.base_price,
                        "cost": item.cost,
                        "linea": item.linea,
                        "marca": item.marca
                    },
                    outputs={
                        "final_price": round(precio_final, 2),
                        "markup_applied": markup,
                        "profit_margin": round((precio_final - item.cost) / precio_final, 4)
                    },
                    breakdown={
                        "cost": item.cost,
                        "markup": markup,
                        "markup_amount": round(item.cost * markup, 2),
                        "final_price": round(precio_final, 2)
                    }
                )
                db.add(price_item)
            
            # Actualizar resumen
            price_run.resumen = {
                "total_items": len(items),
                "total_cost": sum(item.cost for item in items),
                "total_revenue": sum(item.cost * (1 + ruleset.config.get("markup_base", 0.25)) for item in items),
                "average_markup": ruleset.config.get("markup_base", 0.25),
                "status": "completed"
            }
            price_run.status = "completed"
            price_run.completed_at = datetime.utcnow()
            
        except Exception as e:
            price_run.status = "failed"
            price_run.resumen = {"error": str(e)}
            logger.error(f"Error en simulación: {e}")
        
        db.commit()
        logger.info(f"Simulación completada: {price_run.id} - Status: {price_run.status}")
        
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

@router.get("/simulate/tenant/{tenant_id}", response_model=list[SimulateResponse])
async def get_tenant_simulations(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las simulaciones de un tenant
    """
    # Validar tenant
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    
    # Obtener simulaciones del tenant
    simulations = db.query(PriceRun).join(ListRaw).filter(ListRaw.tenant_id == tenant_id).all()
    
    return [
        SimulateResponse(
            id=sim.id,
            list_id=sim.list_id,
            ruleset_id=sim.ruleset_id,
            status=sim.status,
            created_at=sim.created_at,
            completed_at=sim.completed_at,
            summary=sim.resumen
        )
        for sim in simulations
    ]
