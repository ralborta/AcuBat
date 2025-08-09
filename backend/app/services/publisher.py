import csv
import io
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import Publish, PriceRun, PriceItem
from app.services.storage import storage_service

logger = logging.getLogger(__name__)

class Publisher:
    """Servicio para publicar resultados de simulaciones"""
    
    def __init__(self):
        pass
    
    def publish_results(self, db: Session, tenant_id: str, run_id: str, channel: str, changelog: Optional[str] = None) -> Publish:
        """
        Publica los resultados de una simulación
        
        Args:
            db: Sesión de base de datos
            tenant_id: ID del tenant
            run_id: ID del price run
            channel: Canal de publicación
            changelog: Descripción de cambios
            
        Returns:
            Publish con la información de publicación
        """
        try:
            # Verificar que el price run existe y está completado
            price_run = db.query(PriceRun).filter(PriceRun.id == run_id).first()
            if not price_run:
                raise ValueError(f"Price run no encontrado: {run_id}")
            
            if price_run.status != "completed":
                raise ValueError(f"Price run no está completado: {run_id}")
            
            # Obtener price items
            price_items = db.query(PriceItem).filter(PriceItem.run_id == run_id).all()
            if not price_items:
                raise ValueError(f"No se encontraron items para el run: {run_id}")
            
            # Generar CSV
            csv_data = self._generate_csv(price_items, channel)
            
            # Guardar CSV en almacenamiento local (volumen)
            filename = f"pricing_export_{run_id}_{channel}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            export_url = storage_service.upload_file(
                file_data=io.BytesIO(csv_data.encode('utf-8')),
                filename=filename,
                content_type="text/csv"
            )
            
            # Crear registro de publicación
            publish = Publish(
                run_id=run_id,
                canal=channel,
                export_url=export_url,
                changelog=changelog
            )
            
            db.add(publish)
            db.commit()
            db.refresh(publish)
            
            logger.info(f"Publicación creada: {publish.id} - {filename}")
            return publish
            
        except Exception as e:
            logger.error(f"Error en publicación: {e}")
            raise
    
    def _generate_csv(self, price_items: List[PriceItem], channel: str) -> str:
        """
        Genera el contenido CSV para los price items
        
        Args:
            price_items: Lista de price items
            channel: Canal de publicación
            
        Returns:
            Contenido CSV como string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Escribir headers
        headers = [
            'SKU', 'Marca', 'Línea', 'Precio Base', 'Costo',
            'K', 'P', 'Markup (Q)', 'Rentabilidad (R)',
            'Precio Público', 'Precio Público sin IVA',
            'Canal', 'Fecha Exportación'
        ]
        writer.writerow(headers)
        
        # Escribir datos
        for item in price_items:
            inputs = item.inputs
            outputs = item.outputs
            
            row = [
                inputs.get('sku', ''),
                inputs.get('marca', ''),
                inputs.get('linea', ''),
                inputs.get('base_price', 0),
                inputs.get('cost', 0),
                outputs.get('K', 0),
                outputs.get('P', 0),
                outputs.get('markup', 0),
                outputs.get('rentabilidad', 0),
                outputs.get('precio_publico', 0),
                outputs.get('precio_publico_sin_iva', 0),
                channel,
                datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            ]
            writer.writerow(row)
        
        return output.getvalue()
    
    def get_publish(self, db: Session, publish_id: str) -> Optional[Publish]:
        """
        Obtiene una publicación por ID
        
        Args:
            db: Sesión de base de datos
            publish_id: ID de la publicación
            
        Returns:
            Publish o None si no existe
        """
        return db.query(Publish).filter(Publish.id == publish_id).first()
    
    def get_publishes_by_run(self, db: Session, run_id: str) -> List[Publish]:
        """
        Obtiene todas las publicaciones de un run
        
        Args:
            db: Sesión de base de datos
            run_id: ID del price run
            
        Returns:
            Lista de publicaciones
        """
        return db.query(Publish).filter(Publish.run_id == run_id).all()

# Instancia global del publisher
publisher = Publisher()
