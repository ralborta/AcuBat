#!/usr/bin/env python3
"""
📊 ANÁLISIS DE RENTABILIDAD ESPECÍFICO DEL SECTOR BATERÍAS
Metodologías reales utilizadas en la industria automotriz argentina
"""
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

class RentabilidadSectorBaterias:
    """Analizador de rentabilidad específico para el sector baterías"""
    
    def __init__(self):
        # Estructura de costos típica del sector baterías
        self.estructura_costos = {
            "costos_producto": {
                "materia_prima": 0.35,      # 35% - Plomo, ácido, plástico
                "mano_obra_directa": 0.08,  # 8% - Operarios producción
                "costos_industriales": 0.12 # 12% - Energía, equipos, etc.
            },
            "costos_comerciales": {
                "comision_vendedores": 0.03,  # 3% sobre venta
                "publicidad_marketing": 0.02, # 2% sobre venta
                "logistica_distribucion": 0.04 # 4% sobre venta
            },
            "costos_estructura": {
                "administracion": 0.08,      # 8% sobre venta
                "gastos_financieros": 0.02,  # 2% sobre venta
                "otros_gastos": 0.01         # 1% sobre venta
            }
        }
        
        # Metodologías de análisis por canal
        self.metodologias_canal = {
            "mayorista": {
                "tipo_analisis": "margen_contribucion",
                "kpis_principales": ["margen_bruto", "rotacion_inventario", "contribucion_fija"],
                "costos_especificos": ["credito_clientes", "logistica_mayor", "descuentos_volumen"]
            },
            "minorista": {
                "tipo_analisis": "rentabilidad_integral", 
                "kpis_principales": ["margen_neto", "ticket_promedio", "frecuencia_compra"],
                "costos_especificos": ["atencion_cliente", "exhibicion", "garantias"]
            },
            "distribuidor": {
                "tipo_analisis": "eficiencia_territorial",
                "kpis_principales": ["margen_zona", "penetracion_mercado", "costo_territorio"],
                "costos_especificos": ["representantes", "territorio", "soporte_tecnico"]
            }
        }
        
    def analizar_rentabilidad_producto(self, producto: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza rentabilidad de un producto según metodologías del sector"""
        
        codigo = producto.get("codigo", "N/A")
        marca = producto.get("marca", "").lower()
        precio_base = producto.get("precio_base", 0)
        pricing_canales = producto.get("pricing_canales", {})
        
        logger.debug(f"Analizando rentabilidad: {codigo}")
        
        # Calcular costos base del producto
        costos_base = self._calcular_costos_base(precio_base, marca)
        
        # Análisis por cada canal
        analisis_canales = {}
        for canal, datos_precio in pricing_canales.items():
            analisis_canales[canal] = self._analizar_rentabilidad_canal(
                canal, datos_precio, costos_base, marca
            )
        
        # Consolidar análisis
        rentabilidad_consolidada = self._consolidar_analisis(analisis_canales, costos_base)
        
        return {
            "codigo": codigo,
            "marca": marca,
            "costos_base": costos_base,
            "analisis_por_canal": analisis_canales,
            "rentabilidad_consolidada": rentabilidad_consolidada,
            "fecha_analisis": datetime.now().isoformat(),
            "metodologia": "sector_baterias_v1.0"
        }
    
    def _calcular_costos_base(self, precio_base: float, marca: str) -> Dict[str, float]:
        """Calcula la estructura de costos base según la marca"""
        
        # Ajustar costos según posicionamiento de marca
        factor_marca = self._obtener_factor_marca(marca)
        
        costos = {}
        
        # Costos de producto (fijos independiente del canal)
        costos_producto = self.estructura_costos["costos_producto"]
        costos["materia_prima"] = precio_base * costos_producto["materia_prima"] * factor_marca
        costos["mano_obra_directa"] = precio_base * costos_producto["mano_obra_directa"]
        costos["costos_industriales"] = precio_base * costos_producto["costos_industriales"]
        
        # Costo total de producción
        costos["costo_produccion"] = sum([
            costos["materia_prima"],
            costos["mano_obra_directa"], 
            costos["costos_industriales"]
        ])
        
        # Costo unitario estándar
        costos["costo_unitario"] = costos["costo_produccion"]
        
        return costos
    
    def _obtener_factor_marca(self, marca: str) -> float:
        """Obtiene factor de ajuste de costos según marca"""
        
        factores_marca = {
            "moura": 1.15,    # Premium - Materiales de mayor calidad
            "varta": 1.20,    # Importada - Costos adicionales
            "acubat": 1.00,   # Base - Marca nacional estándar
            "willard": 0.90   # Económica - Optimización de costos
        }
        
        return factores_marca.get(marca, 1.00)
    
    def _analizar_rentabilidad_canal(self, canal: str, datos_precio: Dict, costos_base: Dict, marca: str) -> Dict[str, Any]:
        """Analiza rentabilidad específica por canal"""
        
        precio_venta = datos_precio.get("precio_final", 0)
        costo_unitario = costos_base.get("costo_unitario", 0)
        
        # Costos específicos del canal
        costos_canal = self._calcular_costos_canal(canal, precio_venta, marca)
        
        # Metodología específica según canal
        metodologia = self.metodologias_canal.get(canal, self.metodologias_canal["minorista"])
        
        if metodologia["tipo_analisis"] == "margen_contribucion":
            # Para mayoristas - Enfoque en contribución
            analisis = self._analisis_margen_contribucion(precio_venta, costo_unitario, costos_canal)
            
        elif metodologia["tipo_analisis"] == "rentabilidad_integral":
            # Para minoristas - Análisis completo
            analisis = self._analisis_rentabilidad_integral(precio_venta, costo_unitario, costos_canal)
            
        elif metodologia["tipo_analisis"] == "eficiencia_territorial":
            # Para distribuidores - Eficiencia territorial
            analisis = self._analisis_eficiencia_territorial(precio_venta, costo_unitario, costos_canal)
            
        else:
            # Análisis estándar
            analisis = self._analisis_rentabilidad_integral(precio_venta, costo_unitario, costos_canal)
        
        # Agregar KPIs específicos del canal
        analisis["kpis_especificos"] = self._calcular_kpis_canal(canal, analisis)
        analisis["evaluacion_rentabilidad"] = self._evaluar_rentabilidad(analisis, canal)
        
        return analisis
    
    def _calcular_costos_canal(self, canal: str, precio_venta: float, marca: str) -> Dict[str, float]:
        """Calcula costos específicos por canal de venta"""
        
        costos_comerciales = self.estructura_costos["costos_comerciales"]
        costos_estructura = self.estructura_costos["costos_estructura"]
        
        costos_canal = {}
        
        # Costos base
        costos_canal["comision_vendedores"] = precio_venta * costos_comerciales["comision_vendedores"]
        costos_canal["publicidad_marketing"] = precio_venta * costos_comerciales["publicidad_marketing"]
        costos_canal["administracion"] = precio_venta * costos_estructura["administracion"]
        costos_canal["gastos_financieros"] = precio_venta * costos_estructura["gastos_financieros"]
        
        # Costos específicos por canal
        if canal == "mayorista":
            costos_canal["credito_clientes"] = precio_venta * 0.03  # 3% - Financiación 30-60 días
            costos_canal["logistica_mayor"] = precio_venta * 0.02   # 2% - Distribución volumen
            costos_canal["descuentos_volumen"] = precio_venta * 0.05 # 5% - Descuentos por cantidad
            
        elif canal == "minorista":
            costos_canal["atencion_cliente"] = precio_venta * 0.04  # 4% - Personal tienda
            costos_canal["exhibicion"] = precio_venta * 0.01       # 1% - Displays, góndolas
            costos_canal["garantias"] = precio_venta * 0.02        # 2% - Servicio post-venta
            
        elif canal == "distribuidor":
            costos_canal["representantes"] = precio_venta * 0.04   # 4% - Comisión distribuidores
            costos_canal["territorio"] = precio_venta * 0.03       # 3% - Cobertura geográfica
            costos_canal["soporte_tecnico"] = precio_venta * 0.02  # 2% - Asistencia técnica
        
        # Costo total del canal
        costos_canal["total_costos_canal"] = sum(costos_canal.values())
        
        return costos_canal
    
    def _analisis_margen_contribucion(self, precio_venta: float, costo_unitario: float, costos_canal: Dict) -> Dict[str, Any]:
        """Análisis de margen de contribución - Metodología Mayorista"""
        
        # Margen de contribución = Precio - Costos Variables
        costos_variables = costo_unitario + costos_canal.get("total_costos_canal", 0)
        margen_contribucion = precio_venta - costos_variables
        margen_contribucion_pct = (margen_contribucion / precio_venta) * 100 if precio_venta > 0 else 0
        
        # Contribución por unidad para gastos fijos
        contribucion_gastos_fijos = margen_contribucion
        
        return {
            "metodologia": "margen_contribucion",
            "precio_venta": precio_venta,
            "costo_unitario": costo_unitario,
            "costos_variables": costos_variables,
            "margen_contribucion": margen_contribucion,
            "margen_contribucion_pct": margen_contribucion_pct,
            "contribucion_gastos_fijos": contribucion_gastos_fijos,
            "punto_equilibrio_unidades": self._calcular_punto_equilibrio(margen_contribucion, 1000)  # Asumiendo gastos fijos de $1000
        }
    
    def _analisis_rentabilidad_integral(self, precio_venta: float, costo_unitario: float, costos_canal: Dict) -> Dict[str, Any]:
        """Análisis integral de rentabilidad - Metodología Minorista"""
        
        costos_totales = costo_unitario + costos_canal.get("total_costos_canal", 0)
        
        # Margen bruto
        margen_bruto = precio_venta - costo_unitario
        margen_bruto_pct = (margen_bruto / precio_venta) * 100 if precio_venta > 0 else 0
        
        # Margen neto
        margen_neto = precio_venta - costos_totales
        margen_neto_pct = (margen_neto / precio_venta) * 100 if precio_venta > 0 else 0
        
        # ROI (Return on Investment)
        roi = (margen_neto / costo_unitario) * 100 if costo_unitario > 0 else 0
        
        return {
            "metodologia": "rentabilidad_integral",
            "precio_venta": precio_venta,
            "costo_unitario": costo_unitario,
            "costos_totales": costos_totales,
            "margen_bruto": margen_bruto,
            "margen_bruto_pct": margen_bruto_pct,
            "margen_neto": margen_neto,
            "margen_neto_pct": margen_neto_pct,
            "roi": roi,
            "rentabilidad_sobre_ventas": margen_neto_pct
        }
    
    def _analisis_eficiencia_territorial(self, precio_venta: float, costo_unitario: float, costos_canal: Dict) -> Dict[str, Any]:
        """Análisis de eficiencia territorial - Metodología Distribuidor"""
        
        costos_totales = costo_unitario + costos_canal.get("total_costos_canal", 0)
        margen_zona = precio_venta - costos_totales
        margen_zona_pct = (margen_zona / precio_venta) * 100 if precio_venta > 0 else 0
        
        # Eficiencia territorial (simulada)
        eficiencia_territorial = margen_zona_pct * 0.8  # Factor de penetración de mercado
        
        return {
            "metodologia": "eficiencia_territorial", 
            "precio_venta": precio_venta,
            "costo_unitario": costo_unitario,
            "costos_totales": costos_totales,
            "margen_zona": margen_zona,
            "margen_zona_pct": margen_zona_pct,
            "eficiencia_territorial": eficiencia_territorial,
            "penetracion_mercado": 80.0,  # Simulado
            "cobertura_territorial": 95.0  # Simulado
        }
    
    def _calcular_kpis_canal(self, canal: str, analisis: Dict) -> Dict[str, float]:
        """Calcula KPIs específicos por canal"""
        
        metodologia = self.metodologias_canal.get(canal, {})
        kpis_principales = metodologia.get("kpis_principales", [])
        
        kpis = {}
        
        for kpi in kpis_principales:
            if kpi in analisis:
                kpis[kpi] = analisis[kpi]
            elif kpi == "rotacion_inventario":
                kpis[kpi] = 8.5  # Rotaciones por año (simulado)
            elif kpi == "ticket_promedio":
                kpis[kpi] = analisis.get("precio_venta", 0) * 1.2  # Simulado
            elif kpi == "frecuencia_compra":
                kpis[kpi] = 2.3  # Compras por año (simulado)
            elif kpi == "penetracion_mercado":
                kpis[kpi] = 75.0  # Porcentaje (simulado)
        
        return kpis
    
    def _evaluar_rentabilidad(self, analisis: Dict, canal: str) -> Dict[str, Any]:
        """Evalúa la rentabilidad según benchmarks del sector"""
        
        # Benchmarks típicos del sector baterías
        benchmarks = {
            "mayorista": {"margen_minimo": 15, "margen_objetivo": 25, "margen_excelente": 35},
            "minorista": {"margen_minimo": 25, "margen_objetivo": 40, "margen_excelente": 55},
            "distribuidor": {"margen_minimo": 20, "margen_objetivo": 30, "margen_excelente": 45}
        }
        
        benchmark = benchmarks.get(canal, benchmarks["minorista"])
        
        # Obtener margen relevante según metodología
        if analisis.get("metodologia") == "margen_contribucion":
            margen_actual = analisis.get("margen_contribucion_pct", 0)
        elif analisis.get("metodologia") == "eficiencia_territorial":
            margen_actual = analisis.get("margen_zona_pct", 0)
        else:
            margen_actual = analisis.get("margen_neto_pct", 0)
        
        # Evaluación
        if margen_actual >= benchmark["margen_excelente"]:
            evaluacion = "EXCELENTE"
            color = "green"
        elif margen_actual >= benchmark["margen_objetivo"]:
            evaluacion = "BUENA"
            color = "blue"
        elif margen_actual >= benchmark["margen_minimo"]:
            evaluacion = "ACEPTABLE"
            color = "yellow"
        else:
            evaluacion = "DEFICIENTE"
            color = "red"
        
        return {
            "evaluacion": evaluacion,
            "color": color,
            "margen_actual": margen_actual,
            "margen_objetivo": benchmark["margen_objetivo"],
            "brecha": margen_actual - benchmark["margen_objetivo"],
            "recomendacion": self._generar_recomendacion(evaluacion, margen_actual, benchmark)
        }
    
    def _generar_recomendacion(self, evaluacion: str, margen_actual: float, benchmark: Dict) -> str:
        """Genera recomendaciones según la evaluación"""
        
        if evaluacion == "EXCELENTE":
            return f"Mantener estrategia actual. Margen del {margen_actual:.1f}% supera expectativas."
        elif evaluacion == "BUENA":
            return f"Buen desempeño. Oportunidad de optimizar hacia {benchmark['margen_excelente']}%."
        elif evaluacion == "ACEPTABLE":
            brecha = benchmark["margen_objetivo"] - margen_actual
            return f"Requiere mejora. Incrementar margen {brecha:.1f}% para alcanzar objetivo."
        else:
            brecha = benchmark["margen_minimo"] - margen_actual
            return f"URGENTE: Revisar pricing. Margen {brecha:.1f}% por debajo del mínimo aceptable."
    
    def _calcular_punto_equilibrio(self, margen_contribucion: float, gastos_fijos: float) -> float:
        """Calcula punto de equilibrio en unidades"""
        
        if margen_contribucion <= 0:
            return float('inf')
        
        return gastos_fijos / margen_contribucion
    
    def _consolidar_analisis(self, analisis_canales: Dict, costos_base: Dict) -> Dict[str, Any]:
        """Consolida el análisis de todos los canales"""
        
        if not analisis_canales:
            return {}
        
        # Métricas consolidadas
        total_revenue_potencial = sum([
            canal["precio_venta"] for canal in analisis_canales.values()
        ])
        
        margen_promedio = sum([
            canal.get("margen_neto_pct", canal.get("margen_contribucion_pct", canal.get("margen_zona_pct", 0)))
            for canal in analisis_canales.values()
        ]) / len(analisis_canales)
        
        # Canal más rentable
        canal_mas_rentable = max(
            analisis_canales.items(),
            key=lambda x: x[1].get("margen_neto_pct", x[1].get("margen_contribucion_pct", x[1].get("margen_zona_pct", 0)))
        )
        
        return {
            "total_revenue_potencial": total_revenue_potencial,
            "margen_promedio_canales": margen_promedio,
            "canal_mas_rentable": {
                "canal": canal_mas_rentable[0],
                "margen": canal_mas_rentable[1].get("margen_neto_pct", 
                        canal_mas_rentable[1].get("margen_contribucion_pct", 
                        canal_mas_rentable[1].get("margen_zona_pct", 0)))
            },
            "evaluacion_general": self._evaluar_producto_general(margen_promedio),
            "recomendacion_estrategica": self._generar_recomendacion_estrategica(analisis_canales)
        }
    
    def _evaluar_producto_general(self, margen_promedio: float) -> str:
        """Evalúa el producto en general"""
        
        if margen_promedio >= 40:
            return "PRODUCTO_ESTRELLA"
        elif margen_promedio >= 25:
            return "PRODUCTO_RENTABLE"
        elif margen_promedio >= 15:
            return "PRODUCTO_MARGINAL"
        else:
            return "PRODUCTO_PROBLEMATICO"
    
    def _generar_recomendacion_estrategica(self, analisis_canales: Dict) -> str:
        """Genera recomendación estratégica global"""
        
        canales_buenos = [
            canal for canal, datos in analisis_canales.items()
            if datos.get("evaluacion_rentabilidad", {}).get("evaluacion") in ["EXCELENTE", "BUENA"]
        ]
        
        if len(canales_buenos) == len(analisis_canales):
            return "Producto con excelente desempeño en todos los canales. Mantener estrategia."
        elif len(canales_buenos) >= len(analisis_canales) / 2:
            return f"Enfocar en canales rentables: {', '.join(canales_buenos)}. Revisar otros canales."
        else:
            return "Producto requiere revisión integral de pricing y costos en todos los canales."

# Función utilitaria para integración
def analizar_productos_con_rentabilidad_sector(productos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analiza lista de productos con metodología del sector baterías"""
    
    analizador = RentabilidadSectorBaterias()
    productos_analizados = []
    
    for producto in productos:
        try:
            analisis = analizador.analizar_rentabilidad_producto(producto)
            producto_completo = producto.copy()
            producto_completo["analisis_rentabilidad"] = analisis
            productos_analizados.append(producto_completo)
        except Exception as e:
            logger.error(f"Error analizando producto {producto.get('codigo', 'N/A')}: {e}")
            productos_analizados.append(producto)
    
    return productos_analizados