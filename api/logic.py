import logging
from typing import List, Dict, Optional
from .models import Producto, Canal, Marca, TipoAlerta
import math

logger = logging.getLogger(__name__)

class PricingLogic:
    def __init__(self):
        # Configuración de markup por canal y marca
        self.markup_config = {
            (Canal.MINORISTA, Marca.MOURA): 0.35,      # 35%
            (Canal.MINORISTA, Marca.ACUBAT): 0.45,     # 45%
            (Canal.MINORISTA, Marca.LUBECK): 0.40,     # 40%
            (Canal.MINORISTA, Marca.SOLAR): 0.38,      # 38%
            
            (Canal.MAYORISTA, Marca.MOURA): 0.20,      # 20%
            (Canal.MAYORISTA, Marca.ACUBAT): 0.25,     # 25%
            (Canal.MAYORISTA, Marca.LUBECK): 0.22,     # 22%
            (Canal.MAYORISTA, Marca.SOLAR): 0.20,      # 20%
            
            (Canal.DISTRIBUIDOR, Marca.MOURA): 0.15,   # 15%
            (Canal.DISTRIBUIDOR, Marca.ACUBAT): 0.18,  # 18%
            (Canal.DISTRIBUIDOR, Marca.LUBECK): 0.16,  # 16%
            (Canal.DISTRIBUIDOR, Marca.SOLAR): 0.15,   # 15%
        }
        
        # Configuración de márgenes
        self.margen_minimo = 0.10  # 10%
        self.margen_maximo = 0.80  # 80%
        self.margen_optimo = 0.25  # 25% - margen objetivo
        
        # Configuración de redondeo
        self.redondeo_minorista = 100  # Múltiplos de $100 para minorista
        
        # Configuración de análisis de precios
        self.precio_minimo = 1000  # Precio mínimo para alertas
        self.precio_maximo = 50000  # Precio máximo para alertas
        
        # Configuración de sugerencias
        self.sugerencias_habilitadas = True

    def aplicar_markup(self, producto: Producto) -> Producto:
        """Aplica markup según canal y marca del producto"""
        try:
            # Obtener markup configurado
            markup_key = (producto.canal, producto.marca)
            markup_porcentaje = self.markup_config.get(markup_key, 0.30)  # Default 30%
            
            # Calcular precio con markup
            precio_con_markup = producto.precio_base * (1 + markup_porcentaje)
            
            # Aplicar redondeo si es necesario
            precio_final = self.redondear_precio(precio_con_markup, producto.canal)
            
            # Actualizar producto
            producto.precio_final = precio_final
            producto.markup_aplicado = markup_porcentaje * 100  # Guardar como porcentaje
            producto.margen = self.calcular_margen(producto.precio_base, precio_final)
            
            # Generar sugerencias si está habilitado
            if self.sugerencias_habilitadas:
                producto.sugerencias_precio = self.generar_sugerencias_precio(producto)
            
            # Evaluar alertas
            producto.alertas = self.evaluar_alertas(producto)
            
            logger.info(f"Markup aplicado a {producto.codigo}: {markup_porcentaje:.1%} -> ${precio_final:,.2f}")
            
            return producto
            
        except Exception as e:
            logger.error(f"Error aplicando markup a {producto.codigo}: {e}")
            # Agregar alerta de error
            producto.alertas.append(TipoAlerta.SIN_MARKUP)
            return producto

    def redondear_precio(self, precio: float, canal: Canal) -> float:
        """Redondea el precio según el canal"""
        if canal == Canal.MINORISTA:
            # Redondear a múltiplos de $100 para minorista
            return round(precio / self.redondeo_minorista) * self.redondeo_minorista
        elif canal == Canal.MAYORISTA:
            # Redondear a múltiplos de $50 para mayorista
            return round(precio / 50) * 50
        else:
            # Para distribuidores, redondear a 2 decimales
            return round(precio, 2)

    def calcular_margen(self, precio_base: float, precio_final: float) -> float:
        """Calcula el margen como porcentaje"""
        if precio_base <= 0:
            return 0.0
        
        margen = (precio_final - precio_base) / precio_base
        return round(margen * 100, 2)  # Retornar como porcentaje

    def generar_sugerencias_precio(self, producto: Producto) -> Dict[str, float]:
        """Genera sugerencias de precio basadas en análisis"""
        sugerencias = {}
        
        # Sugerencia 1: Precio con margen óptimo
        precio_optimo = producto.precio_base * (1 + self.margen_optimo)
        sugerencias['margen_optimo'] = self.redondear_precio(precio_optimo, producto.canal)
        
        # Sugerencia 2: Precio competitivo (margen mínimo + 5%)
        margen_competitivo = self.margen_minimo + 0.05
        precio_competitivo = producto.precio_base * (1 + margen_competitivo)
        sugerencias['precio_competitivo'] = self.redondear_precio(precio_competitivo, producto.canal)
        
        # Sugerencia 3: Precio premium (margen alto pero razonable)
        margen_premium = self.margen_optimo + 0.15
        precio_premium = producto.precio_base * (1 + margen_premium)
        sugerencias['precio_premium'] = self.redondear_precio(precio_premium, producto.canal)
        
        return sugerencias

    def evaluar_alertas(self, producto: Producto) -> List[TipoAlerta]:
        """Evalúa y retorna las alertas para un producto"""
        alertas = []
        
        # Verificar margen bajo
        if producto.margen < (self.margen_minimo * 100):
            alertas.append(TipoAlerta.MARGEN_BAJO)
        
        # Verificar margen alto (posible sobreprecio)
        if producto.margen > (self.margen_maximo * 100):
            alertas.append(TipoAlerta.PRECIO_FUERA_RANGO)
        
        # Verificar si no tiene código
        if not producto.codigo or producto.codigo == "SIN_CODIGO":
            alertas.append(TipoAlerta.SIN_CODIGO)
        
        # Verificar si el precio final es igual al base (sin markup)
        if abs(producto.precio_final - producto.precio_base) < 0.01:
            alertas.append(TipoAlerta.PRECIO_LIBERADO)
        
        # Verificar precio muy bajo
        if producto.precio_final < self.precio_minimo:
            alertas.append(TipoAlerta.PRECIO_FUERA_RANGO)
        
        # Verificar precio muy alto
        if producto.precio_final > self.precio_maximo:
            alertas.append(TipoAlerta.PRECIO_FUERA_RANGO)
        
        return alertas

    def analizar_competencia(self, productos: List[Producto]) -> Dict[str, Dict]:
        """Analiza precios de competencia por marca y canal"""
        analisis = {}
        
        for producto in productos:
            clave = f"{producto.marca.value}_{producto.canal.value}"
            
            if clave not in analisis:
                analisis[clave] = {
                    'precio_min': float('inf'),
                    'precio_max': 0,
                    'precio_promedio': 0,
                    'total_productos': 0,
                    'margen_promedio': 0
                }
            
            analisis[clave]['precio_min'] = min(analisis[clave]['precio_min'], producto.precio_final)
            analisis[clave]['precio_max'] = max(analisis[clave]['precio_max'], producto.precio_final)
            analisis[clave]['precio_promedio'] += producto.precio_final
            analisis[clave]['margen_promedio'] += producto.margen
            analisis[clave]['total_productos'] += 1
        
        # Calcular promedios
        for clave in analisis:
            total = analisis[clave]['total_productos']
            if total > 0:
                analisis[clave]['precio_promedio'] = round(analisis[clave]['precio_promedio'] / total, 2)
                analisis[clave]['margen_promedio'] = round(analisis[clave]['margen_promedio'] / total, 2)
        
        return analisis

    def generar_reporte_pricing(self, productos: List[Producto]) -> Dict:
        """Genera un reporte completo de pricing"""
        if not productos:
            return {}
        
        # Análisis básico
        total_productos = len(productos)
        productos_con_alertas = len([p for p in productos if p.alertas])
        margen_promedio = sum(p.margen for p in productos) / total_productos
        
        # Análisis por canal
        resumen_canales = self.obtener_resumen_canales(productos)
        
        # Análisis por marca
        resumen_marcas = self.obtener_resumen_marcas(productos)
        
        # Análisis de competencia
        analisis_competencia = self.analizar_competencia(productos)
        
        # Productos con mejor margen
        mejores_margenes = sorted(productos, key=lambda x: x.margen, reverse=True)[:5]
        
        # Productos con alertas críticas
        alertas_criticas = [p for p in productos if TipoAlerta.MARGEN_BAJO in p.alertas]
        
        return {
            'resumen_general': {
                'total_productos': total_productos,
                'productos_con_alertas': productos_con_alertas,
                'porcentaje_alertas': round((productos_con_alertas / total_productos) * 100, 2),
                'margen_promedio': round(margen_promedio, 2)
            },
            'resumen_canales': resumen_canales,
            'resumen_marcas': resumen_marcas,
            'analisis_competencia': analisis_competencia,
            'mejores_margenes': [
                {
                    'codigo': p.codigo,
                    'nombre': p.nombre,
                    'margen': p.margen,
                    'precio_final': p.precio_final
                } for p in mejores_margenes
            ],
            'alertas_criticas': len(alertas_criticas)
        }

    def procesar_productos(self, productos: List[Producto]) -> List[Producto]:
        """Procesa una lista de productos aplicando pricing"""
        productos_procesados = []
        
        for producto in productos:
            try:
                producto_procesado = self.aplicar_markup(producto)
                productos_procesados.append(producto_procesado)
            except Exception as e:
                logger.error(f"Error procesando producto {producto.codigo}: {e}")
                # Agregar alerta de error y continuar
                producto.alertas.append(TipoAlerta.SIN_MARKUP)
                productos_procesados.append(producto)
        
        logger.info(f"Procesados {len(productos_procesados)} productos")
        return productos_procesados

    def obtener_resumen_marcas(self, productos: List[Producto]) -> Dict[str, Dict]:
        """Genera resumen de productos por marca"""
        resumen = {}
        
        for producto in productos:
            marca = producto.marca.value
            if marca not in resumen:
                resumen[marca] = {
                    'total': 0,
                    'con_alertas': 0,
                    'margen_promedio': 0,
                    'precio_promedio': 0,
                    'mejor_margen': 0,
                    'peor_margen': float('inf')
                }
            
            resumen[marca]['total'] += 1
            if producto.alertas:
                resumen[marca]['con_alertas'] += 1
            resumen[marca]['margen_promedio'] += producto.margen
            resumen[marca]['precio_promedio'] += producto.precio_final
            resumen[marca]['mejor_margen'] = max(resumen[marca]['mejor_margen'], producto.margen)
            resumen[marca]['peor_margen'] = min(resumen[marca]['peor_margen'], producto.margen)
        
        # Calcular promedios
        for marca in resumen:
            total = resumen[marca]['total']
            if total > 0:
                resumen[marca]['margen_promedio'] = round(resumen[marca]['margen_promedio'] / total, 2)
                resumen[marca]['precio_promedio'] = round(resumen[marca]['precio_promedio'] / total, 2)
                if resumen[marca]['peor_margen'] == float('inf'):
                    resumen[marca]['peor_margen'] = 0
        
        return resumen

    def obtener_resumen_canales(self, productos: List[Producto]) -> Dict[str, Dict]:
        """Genera resumen de productos por canal"""
        resumen = {}
        
        for producto in productos:
            canal = producto.canal.value
            if canal not in resumen:
                resumen[canal] = {
                    'total': 0,
                    'con_alertas': 0,
                    'margen_promedio': 0,
                    'precio_promedio': 0,
                    'mejor_margen': 0,
                    'peor_margen': float('inf')
                }
            
            resumen[canal]['total'] += 1
            if producto.alertas:
                resumen[canal]['con_alertas'] += 1
            resumen[canal]['margen_promedio'] += producto.margen
            resumen[canal]['precio_promedio'] += producto.precio_final
            resumen[canal]['mejor_margen'] = max(resumen[canal]['mejor_margen'], producto.margen)
            resumen[canal]['peor_margen'] = min(resumen[canal]['peor_margen'], producto.margen)
        
        # Calcular promedios
        for canal in resumen:
            total = resumen[canal]['total']
            if total > 0:
                resumen[canal]['margen_promedio'] = round(resumen[canal]['margen_promedio'] / total, 2)
                resumen[canal]['precio_promedio'] = round(resumen[canal]['precio_promedio'] / total, 2)
                if resumen[canal]['peor_margen'] == float('inf'):
                    resumen[canal]['peor_margen'] = 0
        
        return resumen

    def exportar_a_csv(self, productos: List[Producto]) -> str:
        """Exporta productos a formato CSV con información mejorada"""
        csv_lines = [
            "Código,Descripción,Canal,Marca,Precio Base,Precio Final,Markup %,Margen %,Estado,Alertas,Sugerencias"
        ]
        
        for producto in productos:
            # Calcular markup aplicado
            markup_aplicado = ((producto.precio_final - producto.precio_base) / producto.precio_base * 100) if producto.precio_base > 0 else 0
            
            # Determinar estado
            estado = "OK" if not producto.alertas else "ALERTA"
            
            # Alertas como texto
            alertas_texto = "; ".join([str(alerta.value) for alerta in producto.alertas]) if producto.alertas else ""
            
            # Sugerencias como texto
            sugerencias_texto = ""
            if hasattr(producto, 'sugerencias_precio') and producto.sugerencias_precio:
                sugerencias = []
                for tipo, precio in producto.sugerencias_precio.items():
                    sugerencias.append(f"{tipo}: ${precio:,.2f}")
                sugerencias_texto = "; ".join(sugerencias)
            
            csv_line = f'"{producto.codigo}","{producto.nombre}","{producto.canal.value}","{producto.marca.value}",{producto.precio_base},{producto.precio_final},{markup_aplicado:.1f},{producto.margen:.1f},"{estado}","{alertas_texto}","{sugerencias_texto}"'
            csv_lines.append(csv_line)
        
        return "\n".join(csv_lines) 