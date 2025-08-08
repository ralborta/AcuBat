import json
import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
import math
from app.utils.rounding import rounding

logger = logging.getLogger(__name__)

class RulesEngine:
    """Motor de reglas genérico para pricing"""
    
    def __init__(self):
        self.variables = {}
        self.globals = {}
        self.overrides = []
    
    def load_ruleset(self, ruleset_config: Dict[str, Any]) -> bool:
        """Carga un ruleset desde configuración JSON"""
        try:
            self.name = ruleset_config.get("name", "default")
            self.version = ruleset_config.get("version", "v1")
            self.applies_to = ruleset_config.get("appliesTo", {})
            self.globals = ruleset_config.get("globals", {})
            self.steps = ruleset_config.get("steps", [])
            self.overrides = ruleset_config.get("overrides", [])
            
            logger.info(f"Ruleset cargado: {self.name} v{self.version}")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando ruleset: {e}")
            return False
    
    def apply_overrides(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica overrides basados en condiciones del item"""
        overrides = {}
        
        for override in self.overrides:
            when_conditions = override.get("when", {})
            set_values = override.get("set", {})
            
            # Verificar si se cumplen las condiciones
            conditions_met = True
            for key, value in when_conditions.items():
                if item_data.get(key) != value:
                    conditions_met = False
                    break
            
            if conditions_met:
                overrides.update(set_values)
                logger.debug(f"Override aplicado para {item_data.get('sku', 'unknown')}: {set_values}")
        
        return overrides
    
    def evaluate_expression(self, expr: str, context: Dict[str, Any]) -> float:
        """Evalúa una expresión matemática con variables del contexto"""
        try:
            # Crear un contexto seguro para eval
            safe_context = {
                'math': math,
                'round': round,
                'abs': abs,
                'min': min,
                'max': max,
                'sum': sum,
                **context
            }
            
            # Usar la función de redondeo importada
            safe_context['rounding'] = rounding
            
            # Evaluar expresión
            result = eval(expr, {"__builtins__": {}}, safe_context)
            return float(result)
            
        except Exception as e:
            logger.error(f"Error evaluando expresión '{expr}': {e}")
            return 0.0
    
    def calculate_pricing(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula el pricing para un item usando el ruleset cargado"""
        try:
            # Inicializar variables con datos del item
            self.variables = {
                'sku': item_data.get('sku', ''),
                'marca': item_data.get('marca', ''),
                'linea': item_data.get('linea', ''),
                'base_price': float(item_data.get('base_price', 0)),
                'cost': float(item_data.get('cost', 0)),
                **item_data.get('attrs', {})
            }
            
            # Aplicar overrides
            overrides = self.apply_overrides(item_data)
            self.variables.update(overrides)
            
            # Aplicar variables globales
            self.variables.update(self.globals)
            
            # Ejecutar pasos del ruleset
            for step in self.steps:
                step_type = step.get('type', 'var')
                
                if step_type == 'var':
                    var_name = step['var']
                    
                    if 'from' in step:
                        # Variable desde otra variable
                        source_var = step['from']
                        self.variables[var_name] = self.variables.get(source_var, 0)
                    
                    elif 'value' in step:
                        # Valor fijo
                        self.variables[var_name] = step['value']
                    
                    elif 'expr' in step:
                        # Expresión matemática
                        expr = step['expr']
                        self.variables[var_name] = self.evaluate_expression(expr, self.variables)
                
                elif step_type == 'condition':
                    # Lógica condicional (para futuras expansiones)
                    pass
            
            # Preparar resultado
            result = {
                'inputs': {
                    'sku': self.variables.get('sku'),
                    'marca': self.variables.get('marca'),
                    'linea': self.variables.get('linea'),
                    'base_price': self.variables.get('base_price'),
                    'cost': self.variables.get('cost'),
                },
                'outputs': {
                    'precio_publico': self.variables.get('precio_publico', 0),
                    'markup': self.variables.get('markup', 0),
                    'rentabilidad': self.variables.get('rentabilidad', 0),
                },
                'breakdown': self.variables.copy(),
                'ruleset': {
                    'name': self.name,
                    'version': self.version
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculando pricing para {item_data.get('sku', 'unknown')}: {e}")
            return {
                'inputs': item_data,
                'outputs': {},
                'breakdown': {},
                'error': str(e)
            }
    
    def validate_ruleset(self, ruleset_config: Dict[str, Any]) -> List[str]:
        """Valida la estructura de un ruleset"""
        errors = []
        
        required_fields = ['name', 'version', 'steps']
        for field in required_fields:
            if field not in ruleset_config:
                errors.append(f"Campo requerido faltante: {field}")
        
        if 'steps' in ruleset_config:
            for i, step in enumerate(ruleset_config['steps']):
                if 'var' not in step:
                    errors.append(f"Paso {i}: campo 'var' requerido")
                
                if 'from' not in step and 'value' not in step and 'expr' not in step:
                    errors.append(f"Paso {i}: debe tener 'from', 'value' o 'expr'")
        
        return errors

# Ejemplo de ruleset para Moura (AcuBat)
MOURA_RULESET = {
    "name": "moura_base",
    "version": "v1",
    "appliesTo": { "brand": "Moura" },
    "globals": {
        "IVA": 0.21,
        "L": 0.05,
        "M": 0.00,
        "N": 0.00,
        "roundingPublic": "ceil50"
    },
    "steps": [
        { "var": "precio_lista", "from": "base_price" },
        { "var": "desc1", "value": 0.50 },
        { "var": "neto1", "expr": "precio_lista * (1 - desc1)" },
        { "var": "desc_contado", "value": 0.06 },
        { "var": "K", "expr": "neto1 * (1 - desc_contado)" },
        { "var": "P", "expr": "K - (K*L) - (K*M) - (K*N)" },
        { "var": "precio_publico_bruto", "expr": "K * (1 + IVA)" },
        { "var": "precio_publico", "expr": "rounding(precio_publico_bruto, roundingPublic)" },
        { "var": "precio_publico_sin_iva", "expr": "precio_publico / (1 + IVA)" },
        { "var": "markup", "expr": "(K - cost) / cost" },
        { "var": "rentabilidad", "expr": "(P - cost) / P" }
    ],
    "overrides": [
        { "when": { "linea": "Pesada" }, "set": { "IVA": 0.105 } }
    ]
}
