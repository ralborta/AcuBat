import logging
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.models import Tenant, PriceRun, ListRaw
from app.services.publisher import publisher
from app.services.storage import storage_service
from app.schemas.pricing import PublishRequest, PublishResponse
from app.schemas.common import ErrorResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/publish", response_model=PublishResponse)
async def publish_results(
    request: PublishRequest,
    db: Session = Depends(get_db)
):
    """
    Publica los resultados de una simulación
    
    - **tenant_id**: ID del tenant
    - **run_id**: ID de la simulación
    - **channel**: Canal de publicación (minorista/mayorista)
    - **changelog**: Descripción de cambios (opcional)
    """
    try:
        # Validar tenant
        tenant = db.query(Tenant).filter(Tenant.id == request.tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant no encontrado")
        
        # Validar que el price run pertenece al tenant
        price_run = db.query(PriceRun).filter(
            PriceRun.id == request.run_id
        ).first()
        if not price_run:
            raise HTTPException(status_code=404, detail="Simulación no encontrada")
        
        # Verificar que la lista pertenece al tenant
        list_raw = db.query(ListRaw).filter(
            ListRaw.id == price_run.list_id,
            ListRaw.tenant_id == request.tenant_id
        ).first()
        if not list_raw:
            raise HTTPException(status_code=403, detail="Acceso denegado a la simulación")
        
        # Publicar resultados
        publish = publisher.publish_results(
            db=db,
            tenant_id=request.tenant_id,
            run_id=request.run_id,
            channel=request.channel,
            changelog=request.changelog
        )
        
        logger.info(f"Publicación creada: {publish.id}")
        
        return PublishResponse(
            id=publish.id,
            run_id=publish.run_id,
            channel=publish.canal,
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
async def get_publish_details(
    publish_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles de una publicación
    """
    publish = publisher.get_publish(db, publish_id)
    if not publish:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    
    return PublishResponse(
        id=publish.id,
        run_id=publish.run_id,
        channel=publish.canal,
        export_url=publish.export_url,
        changelog=publish.changelog,
        created_at=publish.created_at
    )

@router.get("/export.csv")
async def download_csv(
    publish_id: str,
    db: Session = Depends(get_db)
):
    """
    Descarga el CSV de una publicación
    
    - **publish_id**: ID de la publicación
    """
    try:
        # Obtener publicación
        publish = publisher.get_publish(db, publish_id)
        if not publish:
            raise HTTPException(status_code=404, detail="Publicación no encontrada")
        
        # Extraer object_name de la URL
        # Asumiendo que la URL es: http://minio:9000/bucket/object_name
        url_parts = publish.export_url.split('/')
        if len(url_parts) < 4:
            raise HTTPException(status_code=500, detail="URL de exportación inválida")
        
        object_name = '/'.join(url_parts[3:])  # Todo después del bucket
        
        # Descargar archivo de S3
        file_data = storage_service.download_file(object_name)
        if not file_data:
            raise HTTPException(status_code=404, detail="Archivo no encontrado en S3")
        
        # Leer contenido
        content = file_data.read()
        
        # Generar nombre de archivo
        filename = f"pricing_export_{publish_id}_{publish.canal}.csv"
        
        logger.info(f"CSV descargado: {filename}")
        
        return Response(
            content=content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error descargando CSV: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
