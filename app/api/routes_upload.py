import os
import tempfile
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.models import ListRaw, Tenant
from app.services.storage import storage_service
from app.services.parser import excel_parser
from app.schemas.pricing import UploadResponse
from app.schemas.common import ErrorResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_excel(
    file: UploadFile = File(..., description="Archivo Excel a subir"),
    tenant_id: str = Form(..., description="ID del tenant"),
    db: Session = Depends(get_db)
):
    """
    Sube un archivo Excel y normaliza los datos
    
    - **file**: Archivo Excel (.xlsx, .xls)
    - **tenant_id**: ID del tenant propietario
    """
    try:
        # Validar tenant
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant no encontrado")
        
        # Validar tipo de archivo
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400, 
                detail="Solo se permiten archivos Excel (.xlsx, .xls)"
            )
        
        # Validar tamaño de archivo
        file_size = 0
        file_content = b""
        for chunk in file.file:
            file_size += len(chunk)
            file_content += chunk
            if file_size > 50 * 1024 * 1024:  # 50MB
                raise HTTPException(
                    status_code=413, 
                    detail="Archivo demasiado grande (máximo 50MB)"
                )
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Guardar archivo (storage local)
            file.file.seek(0)  # Resetear posición del archivo
            storage_url = storage_service.upload_file(
                file_data=file.file,
                filename=file.filename,
                content_type=file.content_type or "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Crear registro en DB
            list_raw = ListRaw(
                tenant_id=tenant_id,
                filename=file.filename,
                storage_url=storage_url,
                list_metadata={
                    "file_size": file_size,
                    "content_type": file.content_type,
                    "original_filename": file.filename
                }
            )
            db.add(list_raw)
            db.commit()
            db.refresh(list_raw)
            
            # Parsear Excel y normalizar datos
            normalized_items = excel_parser.parse_excel_file(
                temp_file_path, 
                tenant_id, 
                list_raw.id
            )
            
            # Guardar items normalizados
            excel_parser.save_items_to_db(normalized_items)
            
            # Actualizar metadata con conteo de items
            list_raw.list_metadata["normalized_items_count"] = len(normalized_items)
            db.commit()
            
            logger.info(f"Archivo subido exitosamente: {file.filename} - {len(normalized_items)} items")
            
            return UploadResponse(
                id=list_raw.id,
                filename=list_raw.filename,
                storage_url=list_raw.storage_url,
                tenant_id=list_raw.tenant_id,
                created_at=list_raw.created_at,
                normalized_items_count=len(normalized_items)
            )
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en upload: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/upload/{list_id}", response_model=UploadResponse)
async def get_upload_details(
    list_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles de un archivo subido
    """
    list_raw = db.query(ListRaw).filter(ListRaw.id == list_id).first()
    if not list_raw:
        raise HTTPException(status_code=404, detail="Lista no encontrada")
    
    normalized_count = (list_raw.list_metadata or {}).get("normalized_items_count", 0)
    
    return UploadResponse(
        id=list_raw.id,
        filename=list_raw.filename,
        storage_url=list_raw.storage_url,
        tenant_id=list_raw.tenant_id,
        created_at=list_raw.created_at,
        normalized_items_count=normalized_count
    )
