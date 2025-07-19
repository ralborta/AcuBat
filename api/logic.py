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
        
        # Configuración de redondeo
        self.redondeo_minorista = 100  # Múltiplos de $100 para minorista

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
        else:
            # Para otros canales, redondear a 2 decimales
            return round(precio, 2)

    def calcular_margen(self, precio_base: float, precio_final: float) -> float:
        """Calcula el margen como porcentaje"""
        if precio_base <= 0:
            return 0.0
        
        margen = (precio_final - precio_base) / precio_base
        return round(margen * 100, 2)  # Retornar como porcentaje

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
        
        return alertas

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
                    'precio_promedio': 0
                }
            
            resumen[marca]['total'] += 1
            if producto.alertas:
                resumen[marca]['con_alertas'] += 1
            resumen[marca]['margen_promedio'] += producto.margen
            resumen[marca]['precio_promedio'] += producto.precio_final
        
        # Calcular promedios
        for marca in resumen:
            total = resumen[marca]['total']
            if total > 0:
                resumen[marca]['margen_promedio'] = round(resumen[marca]['margen_promedio'] / total, 2)
                resumen[marca]['precio_promedio'] = round(resumen[marca]['precio_promedio'] / total, 2)
        
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
                    'precio_promedio': 0
                }
            
            resumen[canal]['total'] += 1
            if producto.alertas:
                resumen[canal]['con_alertas'] += 1
            resumen[canal]['margen_promedio'] += producto.margen
            resumen[canal]['precio_promedio'] += producto.precio_final
        
        # Calcular promedios
        for canal in resumen:
            total = resumen[canal]['total']
            if total > 0:
                resumen[canal]['margen_promedio'] = round(resumen[canal]['margen_promedio'] / total, 2)
                resumen[canal]['precio_promedio'] = round(resumen[canal]['precio_promedio'] / total, 2)
        
        return resumen

    def exportar_a_csv(self, productos: List[Producto]) -> str:
        """Exporta productos a formato CSV"""
        csv_lines = [
            "Código,Descripción,Canal,Marca,Precio Base,Precio Final,Markup %,Margen %,Estado,Alertas"
        ]
        
        for producto in productos:
            # Calcular markup aplicado
            markup_aplicado = ((producto.precio_final - producto.precio_base) / producto.precio_base * 100) if producto.precio_base > 0 else 0
            
            # Determinar estado
            estado = "OK" if not producto.alertas else "ALERTA"
            
            # Alertas como texto
            alertas_texto = "; ".join(producto.alertas) if producto.alertas else ""
            
            csv_line = f'"{producto.codigo}","{producto.nombre}","{producto.canal.value}","{producto.marca.value}",{producto.precio_base},{producto.precio_final},{markup_aplicado:.1f},{producto.margen:.1f},"{estado}","{alertas_texto}"'
            csv_lines.append(csv_line)
        
        return "\n".join(csv_lines) 