import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import PriceRun, PriceItem, NormalizedItem, Ruleset
from app.services.rules_engine import RulesEngine

logger = logging.getLogger(__name__)

class PricingSimulator:
    """Servicio para ejecutar simulaciones de pricing"""
    
    def __init__(self):
        self.rules_engine = RulesEngine()
    
    def run_simulation(self, db: Session, tenant_id: str, list_id: str, ruleset_id: str) -> PriceRun:
        """
        Ejecuta una simulación de pricing
        
        Args:
            db: Sesión de base de datos
            tenant_id: ID del tenant
            list_id: ID de la lista de precios
            ruleset_id: ID del ruleset
            
        Returns:
            PriceRun con los resultados
        """
        try:
            # Crear el price run
            price_run = PriceRun(
                list_id=list_id,
                ruleset_id=ruleset_id,
                status="running"
            )
            db.add(price_run)
            db.commit()
            db.refresh(price_run)
            
            # Obtener el ruleset
            ruleset = db.query(Ruleset).filter(Ruleset.id == ruleset_id).first()
            if not ruleset:
                raise ValueError(f"Ruleset no encontrado: {ruleset_id}")
            
            # Cargar el ruleset en el motor
            if not self.rules_engine.load_ruleset(ruleset.config):
                raise ValueError("Error cargando ruleset")
            
            # Obtener items normalizados
            items = db.query(NormalizedItem).filter(NormalizedItem.list_id == list_id).all()
            if not items:
                raise ValueError(f"No se encontraron items para la lista: {list_id}")
            
            # Procesar cada item
            price_items = []
            for item in items:
                price_item = self._process_item(item, price_run.id)
                price_items.append(price_item)
            
            # Guardar price items
            db.add_all(price_items)
            
            # Calcular resumen
            summary = self._calculate_summary(price_items)
            price_run.resumen = summary
            price_run.status = "completed"
            price_run.completed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(price_run)
            
            logger.info(f"Simulación completada: {price_run.id} - {len(price_items)} items")
            return price_run
            
        except Exception as e:
            logger.error(f"Error en simulación: {e}")
            if 'price_run' in locals():
                price_run.status = "failed"
                db.commit()
            raise
    
    def _process_item(self, item: NormalizedItem, run_id: str) -> PriceItem:
        """
        Procesa un item individual con el motor de reglas
        
        Args:
            item: Item normalizado
            run_id: ID del price run
            
        Returns:
            PriceItem con los resultados
        """
        # Preparar datos de entrada
        item_data = {
            'sku': item.sku,
            'marca': item.marca,
            'linea': item.linea,
            'base_price': item.base_price,
            'cost': item.cost,
            **item.attrs
        }
        
        # Ejecutar motor de reglas
        result = self.rules_engine.calculate_pricing(item_data)
        
        # Extraer outputs y breakdown
        outputs = result.get('outputs', {})
        breakdown = result.get('breakdown', {})
        
        # Crear price item
        price_item = PriceItem(
            run_id=run_id,
            sku=item.sku,
            inputs=item_data,
            outputs=outputs,
            breakdown=breakdown
        )
        
        return price_item
    
    def _calculate_summary(self, price_items: List[PriceItem]) -> Dict[str, Any]:
        """
        Calcula el resumen de la simulación
        
        Args:
            price_items: Lista de price items
            
        Returns:
            Diccionario con el resumen
        """
        if not price_items:
            return {}
        
        # Calcular métricas básicas
        total_items = len(price_items)
        margenes = []
        rentabilidades = []
        
        for item in price_items:
            outputs = item.outputs
            if outputs:
                if 'markup' in outputs:
                    margenes.append(outputs['markup'])
                if 'rentabilidad' in outputs:
                    rentabilidades.append(outputs['rentabilidad'])
        
        # Calcular promedios
        margen_promedio = sum(margenes) / len(margenes) if margenes else 0
        rentabilidad_promedio = sum(rentabilidades) / len(rentabilidades) if rentabilidades else 0
        
        # QA Gates (simplificado por ahora)
        skus_bloqueados = 0
        skus_afectados = total_items  # Por defecto, todos están afectados
        
        # Calcular cambio promedio (simplificado)
        cambio_promedio = 0.0  # Esto se calcularía comparando con versión anterior
        
        summary = {
            'total_items': total_items,
            'cambio_promedio': cambio_promedio,
            'skus_afectados': skus_afectados,
            'skus_bloqueados_por_gate': skus_bloqueados,
            'margen_promedio': margen_promedio,
            'rentabilidad_promedio': rentabilidad_promedio
        }
        
        return summary
    
    def get_run_summary(self, db: Session, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el resumen de un price run
        
        Args:
            db: Sesión de base de datos
            run_id: ID del price run
            
        Returns:
            RunSummary o None si no existe
        """
        price_run = db.query(PriceRun).filter(PriceRun.id == run_id).first()
        if not price_run or not price_run.resumen:
            return None
        
        return price_run.resumen
    
    def get_price_items(self, db: Session, run_id: str, skip: int = 0, limit: int = 50) -> List[PriceItem]:
        """
        Obtiene los price items de un run con paginación
        
        Args:
            db: Sesión de base de datos
            run_id: ID del price run
            skip: Número de items a saltar
            limit: Número máximo de items
            
        Returns:
            Lista de price items
        """
        return db.query(PriceItem).filter(
            PriceItem.run_id == run_id
        ).offset(skip).limit(limit).all()

# Instancia global del simulador
pricing_simulator = PricingSimulator()
