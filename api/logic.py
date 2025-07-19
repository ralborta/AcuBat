from typing import List, Dict, Optional
from .models import Producto, Canal, Marca, TipoAlerta, ConfiguracionMarkup
import math

class LogicaNegocio:
    def __init__(self):
        # Configuración de markup por canal
        self.configuracion_markup = {
            Canal.MINORISTA: ConfiguracionMarkup(
                canal=Canal.MINORISTA,
                porcentaje=35.0,
                aplicar_redondeo=True
            ),
            Canal.MAYORISTA: ConfiguracionMarkup(
                canal=Canal.MAYORISTA,
                porcentaje=25.0,
                aplicar_redondeo=False
            ),
            Canal.DISTRIBUIDOR: ConfiguracionMarkup(
                canal=Canal.DISTRIBUIDOR,
                porcentaje=15.0,
                aplicar_redondeo=False
            )
        }
        
        # Rangos de márgenes aceptables
        self.margenes_minimos = {
            Canal.MINORISTA: 25.0,
            Canal.MAYORISTA: 15.0,
            Canal.DISTRIBUIDOR: 10.0
        }
        
        # Rangos de precios por marca (para validaciones)
        self.rangos_precios = {
            Marca.MOURA: {"min": 80.0, "max": 200.0},
            Marca.ACUBAT: {"min": 100.0, "max": 250.0},
            Marca.LUBECK: {"min": 120.0, "max": 300.0},
            Marca.SOLAR: {"min": 150.0, "max": 400.0}
        }

    def aplicar_markup(self, producto: Producto) -> Producto:
        """Aplica markup según el canal del producto"""
        config = self.configuracion_markup[producto.canal]
        
        # Calcular precio con markup
        precio_con_markup = producto.precio_base * (1 + config.porcentaje / 100)
        
        # Aplicar redondeo si corresponde
        if config.aplicar_redondeo:
            precio_con_markup = self.redondear_precio(precio_con_markup)
        
        producto.precio_final = precio_con_markup
        producto.margen = self.calcular_margen(producto.precio_base, producto.precio_final)
        
        return producto

    def redondear_precio(self, precio: float) -> float:
        """Redondea el precio al múltiplo de $100 más cercano"""
        return round(precio / 100) * 100

    def calcular_margen(self, precio_base: float, precio_final: float) -> float:
        """Calcula el margen porcentual"""
        if precio_base == 0:
            return 0.0
        return ((precio_final - precio_base) / precio_base) * 100

    def validar_alertas(self, producto: Producto) -> List[TipoAlerta]:
        """Valida y genera alertas para el producto"""
        alertas = []
        
        # Verificar si tiene código
        if not producto.codigo or producto.codigo.strip() == "":
            alertas.append(TipoAlerta.SIN_CODIGO)
        
        # Verificar margen mínimo
        margen_minimo = self.margenes_minimos.get(producto.canal, 10.0)
        if producto.margen < margen_minimo:
            alertas.append(TipoAlerta.MARGEN_BAJO)
        
        # Verificar si el precio está liberado (sin markup aplicado)
        precio_esperado = producto.precio_base * (1 + self.configuracion_markup[producto.canal].porcentaje / 100)
        if abs(producto.precio_final - precio_esperado) > 1.0:
            alertas.append(TipoAlerta.PRECIO_LIBERADO)
        
        # Verificar si el precio está fuera del rango esperado para la marca
        rango = self.rangos_precios.get(producto.marca, {"min": 0, "max": float('inf')})
        if producto.precio_final < rango["min"] or producto.precio_final > rango["max"]:
            alertas.append(TipoAlerta.PRECIO_FUERA_RANGO)
        
        # Verificar si no se aplicó markup
        if producto.margen == 0:
            alertas.append(TipoAlerta.SIN_MARKUP)
        
        producto.alertas = alertas
        return alertas

    def procesar_productos(self, productos: List[Producto], aplicar_markup: bool = True) -> List[Producto]:
        """Procesa una lista de productos aplicando toda la lógica de negocio"""
        productos_procesados = []
        
        for producto in productos:
            if aplicar_markup:
                producto = self.aplicar_markup(producto)
            
            self.validar_alertas(producto)
            productos_procesados.append(producto)
        
        return productos_procesados

    def generar_resumen(self, productos: List[Producto]) -> Dict:
        """Genera un resumen estadístico de los productos"""
        total_productos = len(productos)
        productos_con_alertas = len([p for p in productos if p.alertas])
        
        # Resumen por marca
        resumen_marcas = {}
        for marca in Marca:
            productos_marca = [p for p in productos if p.marca == marca]
            resumen_marcas[marca.value] = {
                "cantidad": len(productos_marca),
                "precio_promedio": sum(p.precio_final for p in productos_marca) / len(productos_marca) if productos_marca else 0,
                "alertas": len([p for p in productos_marca if p.alertas])
            }
        
        # Resumen por canal
        resumen_canales = {}
        for canal in Canal:
            productos_canal = [p for p in productos if p.canal == canal]
            resumen_canales[canal.value] = {
                "cantidad": len(productos_canal),
                "precio_promedio": sum(p.precio_final for p in productos_canal) / len(productos_canal) if productos_canal else 0,
                "margen_promedio": sum(p.margen for p in productos_canal) / len(productos_canal) if productos_canal else 0
            }
        
        return {
            "total_productos": total_productos,
            "productos_con_alertas": productos_con_alertas,
            "resumen_marcas": resumen_marcas,
            "resumen_canales": resumen_canales
        }

    def obtener_productos_filtrados(self, productos: List[Producto], 
                                  canal: Optional[Canal] = None,
                                  marca: Optional[Marca] = None,
                                  con_alertas: Optional[bool] = None) -> List[Producto]:
        """Filtra productos según criterios especificados"""
        productos_filtrados = productos
        
        if canal:
            productos_filtrados = [p for p in productos_filtrados if p.canal == canal]
        
        if marca:
            productos_filtrados = [p for p in productos_filtrados if p.marca == marca]
        
        if con_alertas is not None:
            if con_alertas:
                productos_filtrados = [p for p in productos_filtrados if p.alertas]
            else:
                productos_filtrados = [p for p in productos_filtrados if not p.alertas]
        
        return productos_filtrados 