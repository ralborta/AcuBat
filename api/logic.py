import logging
from typing import List, Dict, Optional
from .models import Producto, Canal, Marca, TipoAlerta
from .rentabilidad import RentabilidadValidator

logger = logging.getLogger(__name__)

class PricingLogic:
    def __init__(self):
        # Configuración de markups por canal y marca
        self.markups = {
            (Canal.MINORISTA, Marca.MOURA): 0.35,      # 35% markup para Moura minorista
            (Canal.MINORISTA, Marca.ACUBAT): 0.40,     # 40% markup para Acubat minorista
            (Canal.MINORISTA, Marca.LUBECK): 0.30,     # 30% markup para Lubeck minorista
            (Canal.MINORISTA, Marca.SOLAR): 0.25,      # 25% markup para Solar minorista
            
            (Canal.MAYORISTA, Marca.MOURA): 0.25,      # 25% markup para Moura mayorista
            (Canal.MAYORISTA, Marca.ACUBAT): 0.30,     # 30% markup para Acubat mayorista
            (Canal.MAYORISTA, Marca.LUBECK): 0.20,     # 20% markup para Lubeck mayorista
            (Canal.MAYORISTA, Marca.SOLAR): 0.15,      # 15% markup para Solar mayorista
            
            (Canal.DISTRIBUIDOR, Marca.MOURA): 0.15,   # 15% markup para Moura distribuidor
            (Canal.DISTRIBUIDOR, Marca.ACUBAT): 0.20,  # 20% markup para Acubat distribuidor
            (Canal.DISTRIBUIDOR, Marca.LUBECK): 0.10,  # 10% markup para Lubeck distribuidor
            (Canal.DISTRIBUIDOR, Marca.SOLAR): 0.08,   # 8% markup para Solar distribuidor
        }
        
        # Validador de rentabilidad
        self.rentabilidad_validator = RentabilidadValidator()
        
        # Configuración de redondeo
        self.redondeo_config = {
            'hasta_100': 50,      # Redondear a múltiplos de 50 hasta 100
            'hasta_500': 100,     # Redondear a múltiplos de 100 hasta 500
            'hasta_1000': 250,    # Redondear a múltiplos de 250 hasta 1000
            'mas_1000': 500       # Redondear a múltiplos de 500 para más de 1000
        }

    def procesar_productos(self, productos: List[Producto]) -> List[Producto]:
        """Procesa una lista de productos aplicando pricing y validaciones"""
        try:
            productos_procesados = []
            
            for producto in productos:
                try:
                    # Aplicar markup
                    producto = self.aplicar_markup(producto)
                    
                    # Calcular margen
                    producto = self.calcular_margen(producto)
                    
                    # Evaluar alertas
                    producto = self.evaluar_alertas(producto)
                    
                    # Validar rentabilidad si hay archivo cargado
                    if self.rentabilidad_validator.archivo_cargado:
                        producto = self.validar_rentabilidad(producto)
                    
                    productos_procesados.append(producto)
                    
                except Exception as e:
                    logger.error(f"Error procesando producto {producto.codigo}: {e}")
                    productos_procesados.append(producto)
            
            logger.info(f"Procesados {len(productos_procesados)} productos")
            return productos_procesados
            
        except Exception as e:
            logger.error(f"Error en procesamiento de productos: {e}")
            return productos

    def aplicar_markup(self, producto: Producto) -> Producto:
        """Aplica markup según canal y marca"""
        try:
            # Obtener markup para la combinación canal-marca
            markup = self.markups.get((producto.canal, producto.marca), 0.20)  # Default 20%
            
            # Calcular precio con markup
            precio_con_markup = producto.precio_base * (1 + markup)
            
            # Aplicar redondeo
            precio_redondeado = self.aplicar_redondeo(precio_con_markup)
            
            # Actualizar producto
            producto.precio_final = precio_redondeado
            producto.markup_aplicado = markup * 100  # Convertir a porcentaje
            
            logger.info(f"Markup aplicado a {producto.codigo}: {markup*100:.1f}% -> ${precio_redondeado:,.2f}")
            
            return producto
            
        except Exception as e:
            logger.error(f"Error aplicando markup a {producto.codigo}: {e}")
            return producto

    def aplicar_redondeo(self, precio: float) -> float:
        """Aplica reglas de redondeo según el precio"""
        try:
            if precio <= 100:
                return round(precio / self.redondeo_config['hasta_100']) * self.redondeo_config['hasta_100']
            elif precio <= 500:
                return round(precio / self.redondeo_config['hasta_500']) * self.redondeo_config['hasta_500']
            elif precio <= 1000:
                return round(precio / self.redondeo_config['hasta_1000']) * self.redondeo_config['hasta_1000']
            else:
                return round(precio / self.redondeo_config['mas_1000']) * self.redondeo_config['mas_1000']
                
        except Exception as e:
            logger.error(f"Error aplicando redondeo a {precio}: {e}")
            return precio

    def calcular_margen(self, producto: Producto) -> Producto:
        """Calcula el margen del producto"""
        try:
            if producto.precio_base > 0:
                margen = ((producto.precio_final - producto.precio_base) / producto.precio_base) * 100
                producto.margen = round(margen, 2)
            else:
                producto.margen = 0.0
                
            return producto
            
        except Exception as e:
            logger.error(f"Error calculando margen para {producto.codigo}: {e}")
            producto.margen = 0.0
            return producto

    def evaluar_alertas(self, producto: Producto) -> Producto:
        """Evalúa y agrega alertas al producto"""
        try:
            alertas = []
            
            # Alerta por margen bajo
            if producto.margen < 10:
                alertas.append(TipoAlerta.MARGEN_BAJO)
            
            # Alerta por precio liberado (precio base = 0)
            if producto.precio_base == 0:
                alertas.append(TipoAlerta.PRECIO_LIBERADO)
            
            # Alerta por markup no aplicado
            if producto.markup_aplicado is None or producto.markup_aplicado == 0:
                alertas.append(TipoAlerta.SIN_MARKUP)
            
            # Alerta por precio fuera de rango
            if producto.precio_final > 1000000:  # Más de 1 millón
                alertas.append(TipoAlerta.PRECIO_FUERA_RANGO)
            
            producto.alertas = alertas
            return producto
            
        except Exception as e:
            logger.error(f"Error evaluando alertas para {producto.codigo}: {e}")
            return producto

    def validar_rentabilidad(self, producto: Producto) -> Producto:
        """Valida la rentabilidad del producto según las reglas cargadas"""
        try:
            # Evaluar rentabilidad
            resultado = self.rentabilidad_validator.evaluar_rentabilidad(producto)
            
            # Actualizar producto con resultados
            producto.estado_rentabilidad = resultado['estado']
            producto.margen_minimo_esperado = resultado['margen_minimo']
            producto.margen_optimo_esperado = resultado['margen_optimo']
            
            # Agregar alerta si es necesario
            if resultado['estado'] == 'Ajustar':
                producto.alertas.append(TipoAlerta.MARGEN_BAJO)
            
            logger.info(f"Rentabilidad evaluada para {producto.codigo}: {resultado['estado']} - {resultado['mensaje']}")
            
            return producto
            
        except Exception as e:
            logger.error(f"Error validando rentabilidad para {producto.codigo}: {e}")
            return producto

    def cargar_rentabilidades(self, ruta_archivo: str) -> bool:
        """Carga el archivo de rentabilidades"""
        try:
            return self.rentabilidad_validator.cargar_rentabilidades(ruta_archivo)
        except Exception as e:
            logger.error(f"Error cargando rentabilidades: {e}")
            return False

    def obtener_resumen_marcas(self, productos: List[Producto]) -> Dict:
        """Obtiene resumen de productos por marca"""
        try:
            resumen = {}
            
            for producto in productos:
                marca = producto.marca.value
                if marca not in resumen:
                    resumen[marca] = {
                        'total': 0,
                        'con_alertas': 0,
                        'margen_promedio': 0,
                        'rentabilidad_ok': 0,
                        'rentabilidad_revisar': 0,
                        'rentabilidad_ajustar': 0
                    }
                
                resumen[marca]['total'] += 1
                if producto.alertas:
                    resumen[marca]['con_alertas'] += 1
                resumen[marca]['margen_promedio'] += producto.margen
                
                # Contar estados de rentabilidad
                if producto.estado_rentabilidad == 'OK':
                    resumen[marca]['rentabilidad_ok'] += 1
                elif producto.estado_rentabilidad == 'Revisar':
                    resumen[marca]['rentabilidad_revisar'] += 1
                elif producto.estado_rentabilidad == 'Ajustar':
                    resumen[marca]['rentabilidad_ajustar'] += 1
            
            # Calcular promedios
            for marca in resumen:
                total = resumen[marca]['total']
                if total > 0:
                    resumen[marca]['margen_promedio'] = round(resumen[marca]['margen_promedio'] / total, 1)
            
            return resumen
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen de marcas: {e}")
            return {}

    def obtener_resumen_canales(self, productos: List[Producto]) -> Dict:
        """Obtiene resumen de productos por canal"""
        try:
            resumen = {}
            
            for producto in productos:
                canal = producto.canal.value
                if canal not in resumen:
                    resumen[canal] = {
                        'total': 0,
                        'con_alertas': 0,
                        'margen_promedio': 0,
                        'rentabilidad_ok': 0,
                        'rentabilidad_revisar': 0,
                        'rentabilidad_ajustar': 0
                    }
                
                resumen[canal]['total'] += 1
                if producto.alertas:
                    resumen[canal]['con_alertas'] += 1
                resumen[canal]['margen_promedio'] += producto.margen
                
                # Contar estados de rentabilidad
                if producto.estado_rentabilidad == 'OK':
                    resumen[canal]['rentabilidad_ok'] += 1
                elif producto.estado_rentabilidad == 'Revisar':
                    resumen[canal]['rentabilidad_revisar'] += 1
                elif producto.estado_rentabilidad == 'Ajustar':
                    resumen[canal]['rentabilidad_ajustar'] += 1
            
            # Calcular promedios
            for canal in resumen:
                total = resumen[canal]['total']
                if total > 0:
                    resumen[canal]['margen_promedio'] = round(resumen[canal]['margen_promedio'] / total, 1)
            
            return resumen
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen de canales: {e}")
            return {}

    def exportar_a_csv(self, productos: List[Producto]) -> str:
        """Exporta productos a formato CSV"""
        try:
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Headers
            headers = [
                'Código', 'Nombre', 'Marca', 'Canal', 'Categoría',
                'Precio Base', 'Precio Final', 'Margen (%)', 'Markup (%)',
                'Estado Rentabilidad', 'Margen Mínimo', 'Margen Óptimo',
                'Alertas', 'Sugerencias IA'
            ]
            writer.writerow(headers)
            
            # Datos
            for producto in productos:
                row = [
                    producto.codigo,
                    producto.nombre,
                    producto.marca.value,
                    producto.canal.value,
                    producto.categoria,
                    f"${producto.precio_base:,.2f}",
                    f"${producto.precio_final:,.2f}",
                    f"{producto.margen:.1f}%",
                    f"{producto.markup_aplicado:.1f}%" if producto.markup_aplicado else "0%",
                    producto.estado_rentabilidad,
                    f"{producto.margen_minimo_esperado:.1f}%",
                    f"{producto.margen_optimo_esperado:.1f}%",
                    ", ".join([alerta.value for alerta in producto.alertas]) if producto.alertas else "",
                    producto.sugerencias_openai or ""
                ]
                writer.writerow(row)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error exportando a CSV: {e}")
            return ""

    def generar_reporte_pricing(self, productos: List[Producto]) -> Dict:
        """Genera un reporte completo de pricing"""
        try:
            total_productos = len(productos)
            productos_con_alertas = len([p for p in productos if p.alertas])
            margen_promedio = sum(p.margen for p in productos) / total_productos if productos else 0
            
            # Estadísticas de rentabilidad
            rentabilidad_ok = len([p for p in productos if p.estado_rentabilidad == 'OK'])
            rentabilidad_revisar = len([p for p in productos if p.estado_rentabilidad == 'Revisar'])
            rentabilidad_ajustar = len([p for p in productos if p.estado_rentabilidad == 'Ajustar'])
            sin_referencia = len([p for p in productos if p.estado_rentabilidad == 'Sin referencia'])
            
            # Resúmenes
            resumen_marcas = self.obtener_resumen_marcas(productos)
            resumen_canales = self.obtener_resumen_canales(productos)
            resumen_rentabilidad = self.rentabilidad_validator.obtener_resumen_rentabilidad()
            
            return {
                'total_productos': total_productos,
                'productos_con_alertas': productos_con_alertas,
                'margen_promedio': round(margen_promedio, 1),
                'rentabilidad': {
                    'ok': rentabilidad_ok,
                    'revisar': rentabilidad_revisar,
                    'ajustar': rentabilidad_ajustar,
                    'sin_referencia': sin_referencia
                },
                'resumen_marcas': resumen_marcas,
                'resumen_canales': resumen_canales,
                'resumen_rentabilidad': resumen_rentabilidad
            }
            
        except Exception as e:
            logger.error(f"Error generando reporte de pricing: {e}")
            return {}

    def generar_sugerencias_precio(self, producto: Producto) -> Dict:
        """Genera sugerencias de precio para un producto específico"""
        try:
            sugerencias = {
                'precio_actual': producto.precio_final,
                'margen_actual': producto.margen,
                'sugerencias': []
            }
            
            # Sugerencia basada en margen mínimo
            if producto.margen_minimo_esperado > 0:
                precio_minimo = producto.precio_base * (1 + producto.margen_minimo_esperado / 100)
                precio_minimo_redondeado = self.aplicar_redondeo(precio_minimo)
                
                if producto.precio_final < precio_minimo_redondeado:
                    sugerencias['sugerencias'].append({
                        'tipo': 'Margen mínimo',
                        'precio_sugerido': precio_minimo_redondeado,
                        'margen_resultante': ((precio_minimo_redondeado - producto.precio_base) / producto.precio_base) * 100,
                        'diferencia': precio_minimo_redondeado - producto.precio_final
                    })
            
            # Sugerencia basada en margen óptimo
            if producto.margen_optimo_esperado > 0:
                precio_optimo = producto.precio_base * (1 + producto.margen_optimo_esperado / 100)
                precio_optimo_redondeado = self.aplicar_redondeo(precio_optimo)
                
                sugerencias['sugerencias'].append({
                    'tipo': 'Margen óptimo',
                    'precio_sugerido': precio_optimo_redondeado,
                    'margen_resultante': ((precio_optimo_redondeado - producto.precio_base) / producto.precio_base) * 100,
                    'diferencia': precio_optimo_redondeado - producto.precio_final
                })
            
            return sugerencias
            
        except Exception as e:
            logger.error(f"Error generando sugerencias para {producto.codigo}: {e}")
            return {'precio_actual': 0, 'margen_actual': 0, 'sugerencias': []} 