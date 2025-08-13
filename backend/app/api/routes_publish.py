import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.models import PriceRun, Publish, ListRaw, Tenant
from app.schemas.pricing import PublishRequest, PublishResponse
from app.schemas.common import ErrorResponse
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/publish", response_model=PublishResponse)
async def publish_pricing(
    request: PublishRequest,
    db: Session = Depends(get_db)
):
    """
    Publica los resultados de una ejecución de pricing
    
    - **run_id**: ID de la ejecución
    - **canal**: Canal de publicación (ej: "web", "api", "export")
    """
    try:
        # Validar price run
        price_run = db.query(PriceRun).filter(PriceRun.id == request.run_id).first()
        if not price_run:
            raise HTTPException(status_code=404, detail="Ejecución no encontrada")
        
        # Verificar que el run esté completado
        if price_run.status != "completed":
            raise HTTPException(
                status_code=400, 
                detail="Solo se pueden publicar ejecuciones completadas"
            )
        
        # Crear publicación
        publish = Publish(
            id=str(uuid.uuid4()),
            run_id=request.run_id,
            canal=request.canal,
            export_url=f"demo://export/{request.run_id}/{request.canal}",
            changelog=f"Publicación automática en canal {request.canal}",
            created_at=datetime.utcnow()
        )
        
        db.add(publish)
        db.commit()
        db.refresh(publish)
        
        logger.info(f"Publicación creada: {publish.id} para run {request.run_id}")
        
        return PublishResponse(
            id=publish.id,
            run_id=publish.run_id,
            canal=publish.canal,
            export_url=publish.export_url,
            changelog=publish.changelog,
            created_at=publish.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en publicación: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/publish/{publish_id}", response_model=PublishResponse)
async def get_publish_status(
    publish_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado de una publicación
    """
    publish = db.query(Publish).filter(Publish.id == publish_id).first()
    if not publish:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    
    return PublishResponse(
        id=publish.id,
        run_id=publish.run_id,
        canal=publish.canal,
        export_url=publish.export_url,
        changelog=publish.changelog,
        created_at=publish.created_at
    )

@router.get("/publish/run/{run_id}", response_model=list[PublishResponse])
async def get_run_publications(
    run_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las publicaciones de una ejecución
    """
    # Validar price run
    price_run = db.query(PriceRun).filter(PriceRun.id == run_id).first()
    if not price_run:
        raise HTTPException(status_code=404, detail="Ejecución no encontrada")
    
    publications = db.query(Publish).filter(Publish.run_id == run_id).all()
    
    return [
        PublishResponse(
            id=pub.id,
            run_id=pub.run_id,
            canal=pub.canal,
            export_url=pub.export_url,
            changelog=pub.changelog,
            created_at=pub.created_at
        )
        for pub in publications
    ]

@router.get("/publish/tenant/{tenant_id}", response_model=list[PublishResponse])
async def get_tenant_publications(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las publicaciones de un tenant
    """
    # Validar tenant
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    
    # Obtener publicaciones del tenant
    publications = db.query(Publish).join(PriceRun).join(ListRaw).filter(ListRaw.tenant_id == tenant_id).all()
    
    return [
        PublishResponse(
            id=pub.id,
            run_id=pub.run_id,
            canal=pub.canal,
            export_url=pub.export_url,
            changelog=pub.changelog,
            created_at=pub.created_at
        )
        for pub in publications
    ]

@router.delete("/publish/{publish_id}")
async def delete_publication(
    publish_id: str,
    db: Session = Depends(get_db)
):
    """
    Elimina una publicación
    """
    publish = db.query(Publish).filter(Publish.id == publish_id).first()
    if not publish:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    
    db.delete(publish)
    db.commit()
    
    return {"message": "Publicación eliminada exitosamente"}
