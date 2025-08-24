import logging
from typing import List, Dict, Optional
from .models import Producto, Canal, Marca, TipoAlerta
from .rentabilidad import RentabilidadValidator

logger = logging.getLogger(__name__)

class PricingLogic:
    def __init__(self):
        # Validador de rentabilidad
        self.rentabilidad_validator = RentabilidadValidator()
        
        # Estado del proceso
        self.precios_cargados = False
        self.rentabilidades_cargadas = False
        self.relevamiento_realizado = False
        
        # Cache para listas específicas de precios por marca/canal
        self.listas_especificas = {}
        self.precios_minorista_cache = {}
        
        # Configuración simplificada de markups por marca (según tu imagen)
        self.markups_por_marca = {
            'moura': {
                'mayorista': 0.18,  # 18%
                'minorista': 'lista_especial'  # Según lista de Moura
            },
            'acubat': {
                'mayorista': 0.22,  # 22%
                'minorista': 0.57   # 57%
            },
            'varta': {
                'mayorista': 0.30,  # 30%
                'minorista': 0.97   # 97%
            },
            'willard': {
                'mayorista': 0.22,  # 22%
                'minorista': 0.48   # 48%
            }
        }

    def procesar_productos(self, productos: List[Producto]) -> Dict:
        """Procesa productos con el nuevo flujo simplificado"""
        try:
            logger.info("🚀 Iniciando proceso de pricing simplificado")
            
            # Verificar que tenemos los datos necesarios
            if not self.precios_cargados:
                return {
                    'error': '❌ No hay precios cargados. Carga primero la lista de precios.',
                    'pasos_completados': []
                }
            
            if not self.rentabilidades_cargadas:
                return {
                    'error': '❌ No hay rentabilidades cargadas. Carga primero las reglas de rentabilidad.',
                    'pasos_completados': []
                }
            
            pasos_completados = []
            productos_procesados = []
            
            # PASO 1: Validar códigos cruzados
            logger.info("📋 Paso 1: Validando códigos cruzados...")
            codigos_validados = self.validar_codigos_cruzados(productos)
            pasos_completados.append({
                'paso': 1,
                'descripcion': 'Validación de códigos cruzados',
                'estado': '✅ Completado',
                'detalles': f'Validados {codigos_validados} códigos'
            })
            
            # PASO 2: Relevamiento de mercado (simulado)
            logger.info("🔍 Paso 2: Relevamiento de mercado...")
            pasos_completados.append({
                'paso': 2,
                'descripcion': 'Relevamiento de precios de mercado',
                'estado': '⚠️ No disponible',
                'detalles': 'Funcionalidad en desarrollo - usando markups estándar'
            })
            
            # PASO 3: Aplicar markups dinámicos
            logger.info("💰 Paso 3: Aplicando markups...")
            productos_con_markup = self.aplicar_markups_dinamicos(productos)
            pasos_completados.append({
                'paso': 3,
                'descripcion': 'Aplicación de markups por marca y canal',
                'estado': '✅ Completado',
                'detalles': f'Procesados {len(productos_con_markup)} productos'
            })
            
            # PASO 4: Redondeo (solo minorista)
            logger.info("🔢 Paso 4: Aplicando redondeo...")
            productos_redondeados = self.aplicar_redondeo_simplificado(productos_con_markup)
            pasos_completados.append({
                'paso': 4,
                'descripcion': 'Redondeo de precios minoristas',
                'estado': '✅ Completado',
                'detalles': 'Redondeo de $100 en $100 para minorista'
            })
            
            # PASO 5: Calcular márgenes
            logger.info("📊 Paso 5: Calculando márgenes...")
            productos_con_margen = self.calcular_margenes(productos_redondeados)
            pasos_completados.append({
                'paso': 5,
                'descripcion': 'Cálculo de márgenes de rentabilidad',
                'estado': '✅ Completado',
                'detalles': f'Calculados márgenes para {len(productos_con_margen)} productos'
            })
            
            # PASO 6: Validar rentabilidad
            logger.info("✅ Paso 6: Validando rentabilidad...")
            productos_validados = self.validar_rentabilidad_final(productos_con_margen)
            pasos_completados.append({
                'paso': 6,
                'descripcion': 'Validación contra reglas de rentabilidad',
                'estado': '✅ Completado',
                'detalles': 'Validados contra reglas cargadas'
            })
            
            logger.info(f"🎉 Proceso completado exitosamente - {len(productos_validados)} productos procesados")
            
            return {
                'success': True,
                'productos': productos_validados,
                'pasos_completados': pasos_completados,
                'resumen': self.generar_resumen_final(productos_validados)
            }
            
        except Exception as e:
            logger.error(f"Error en proceso de pricing: {e}")
            return {
                'error': f'❌ Error en el proceso: {str(e)}',
                'pasos_completados': pasos_completados if 'pasos_completados' in locals() else []
            }

    def validar_codigos_cruzados(self, productos: List[Producto]) -> int:
        """Valida que los códigos sean consistentes"""
        try:
            codigos_validos = 0
            for producto in productos:
                if producto.codigo and len(producto.codigo.strip()) > 0:
                    codigos_validos += 1
            return codigos_validos
        except Exception as e:
            logger.error(f"Error validando códigos: {e}")
            return 0

    def aplicar_markups_dinamicos(self, productos: List[Producto]) -> List[Producto]:
        """Aplica markups según marca y canal"""
        try:
            for producto in productos:
                marca_lower = producto.marca.value.lower()
                canal_lower = producto.canal.value.lower()
                
                # Obtener markup según marca y canal
                if marca_lower in self.markups_por_marca:
                    markup_config = self.markups_por_marca[marca_lower]
                    
                    if canal_lower == 'mayorista':
                        markup = markup_config.get('mayorista', 0.20)
                    elif canal_lower == 'minorista':
                        markup = markup_config.get('minorista', 0.50)
                        if markup == 'lista_especial':
                            # Para Moura minorista, usar precio específico de lista
                            precio_especifico = self._obtener_precio_lista_especial(
                                producto.codigo, 
                                marca_lower, 
                                'minorista'
                            )
                            if precio_especifico:
                                producto.precio_final = precio_especifico
                                # Calcular el markup real aplicado
                                markup_real = (precio_especifico - producto.precio_base) / producto.precio_base
                                producto.markup_aplicado = markup_real * 100
                                logger.debug(f"Precio lista especial para {producto.codigo}: ${precio_especifico:,.0f} (markup: {markup_real*100:.1f}%)")
                                continue  # Saltar el cálculo normal de markup
                            else:
                                # Fallback si no se encuentra en lista específica
                                markup = 0.85  # Valor por defecto
                    else:
                        markup = 0.25  # Default
                else:
                    markup = 0.25  # Default para marcas no configuradas
                
                # Aplicar markup
                producto.precio_final = producto.precio_base * (1 + markup)
                producto.markup_aplicado = markup * 100
                
                logger.debug(f"Markup aplicado a {producto.codigo}: {markup*100:.1f}%")
            
            return productos
            
        except Exception as e:
            logger.error(f"Error aplicando markups: {e}")
            return productos

    def _obtener_precio_lista_especial(self, codigo: str, marca: str, canal: str) -> Optional[float]:
        """
        Obtiene el precio específico de la lista especial para una marca/canal
        
        Args:
            codigo: Código del producto
            marca: Marca del producto (moura, acubat, etc.)
            canal: Canal de venta (minorista, mayorista)
            
        Returns:
            Precio específico o None si no se encuentra
        """
        try:
            # Generar clave de cache
            cache_key = f"{marca}_{canal}_{codigo}"
            
            # Verificar cache primero
            if cache_key in self.precios_minorista_cache:
                return self.precios_minorista_cache[cache_key]
            
            # Si tenemos datos de rentabilidades cargados, buscar ahí
            if hasattr(self, 'rentabilidades_data') and self.rentabilidades_data:
                precio = self._buscar_en_rentabilidades(codigo, marca, canal)
                if precio:
                    self.precios_minorista_cache[cache_key] = precio
                    return precio
            
            # Si no se encuentra, intentar cargar desde archivos conocidos
            precio = self._cargar_precio_desde_archivo(codigo, marca, canal)
            if precio:
                self.precios_minorista_cache[cache_key] = precio
                return precio
            
            logger.warning(f"No se encontró precio específico para {codigo} ({marca} {canal})")
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo precio lista especial para {codigo}: {e}")
            return None

    def _buscar_en_rentabilidades(self, codigo: str, marca: str, canal: str) -> Optional[float]:
        """Busca el precio en los datos de rentabilidades cargados"""
        try:
            if not hasattr(self, 'rentabilidades_data'):
                return None
                
            # Buscar en reglas de minorista si es canal minorista
            if canal == 'minorista' and 'reglas_minorista' in self.rentabilidades_data:
                for regla in self.rentabilidades_data['reglas_minorista']:
                    if regla.get('codigo') == codigo:
                        # Calcular precio final usando markup de la regla
                        precio_base = regla.get('precio_base', 0)
                        markup = regla.get('markup', 0) / 100  # Convertir porcentaje a decimal
                        precio_final = precio_base * (1 + markup)
                        logger.debug(f"Precio encontrado en rentabilidades: {codigo} = ${precio_final:,.0f}")
                        return precio_final
            
            return None
            
        except Exception as e:
            logger.error(f"Error buscando en rentabilidades: {e}")
            return None

    def _cargar_precio_desde_archivo(self, codigo: str, marca: str, canal: str) -> Optional[float]:
        """Intenta cargar el precio desde archivos específicos de la marca"""
        try:
            # Para Moura, intentar cargar desde lista específica
            if marca == 'moura' and canal == 'minorista':
                return self._cargar_precio_moura_minorista(codigo)
            
            # Agregar más marcas aquí según sea necesario
            # elif marca == 'acubat' and canal == 'minorista':
            #     return self._cargar_precio_acubat_minorista(codigo)
            
            return None
            
        except Exception as e:
            logger.error(f"Error cargando precio desde archivo: {e}")
            return None

    def _cargar_precio_moura_minorista(self, codigo: str) -> Optional[float]:
        """Carga precio específico de Moura minorista desde archivo"""
        try:
            # Intentar importar las funciones de Moura
            from .moura_rentabilidad import analizar_rentabilidades_moura
            
            # Si ya tenemos los datos cargados, usarlos
            if hasattr(self, 'moura_data_cache'):
                for regla in self.moura_data_cache.get('reglas_minorista', []):
                    if regla.get('codigo') == codigo:
                        precio_base = regla.get('precio_base', 0)
                        markup = regla.get('markup', 0) / 100
                        return precio_base * (1 + markup)
            
            logger.debug(f"No se encontró precio Moura minorista para código {codigo}")
            return None
            
        except Exception as e:
            logger.error(f"Error cargando precio Moura minorista: {e}")
            return None

    def cargar_listas_especificas(self, archivo_rentabilidades: str = None):
        """
        Carga las listas específicas de precios desde archivos
        
        Args:
            archivo_rentabilidades: Ruta al archivo de rentabilidades
        """
        try:
            if archivo_rentabilidades:
                # Cargar datos de Moura
                from .moura_rentabilidad import analizar_rentabilidades_moura
                self.moura_data_cache = analizar_rentabilidades_moura(archivo_rentabilidades)
                logger.info(f"✅ Listas específicas cargadas desde {archivo_rentabilidades}")
                
                # Marcar que tenemos rentabilidades cargadas
                self.rentabilidades_cargadas = True
                self.rentabilidades_data = self.moura_data_cache
            
        except Exception as e:
            logger.error(f"Error cargando listas específicas: {e}")

    def aplicar_redondeo_simplificado(self, productos: List[Producto]) -> List[Producto]:
        """Aplica redondeo solo para minorista, de $100 en $100"""
        try:
            for producto in productos:
                if producto.canal.value.lower() == 'minorista':
                    # Redondear a múltiplos de 100
                    precio_redondeado = round(producto.precio_final / 100) * 100
                    producto.precio_final = precio_redondeado
                    logger.debug(f"Redondeado {producto.codigo}: ${producto.precio_final:,.0f}")
            
            return productos
            
        except Exception as e:
            logger.error(f"Error aplicando redondeo: {e}")
            return productos

    def calcular_margenes(self, productos: List[Producto]) -> List[Producto]:
        """Calcula márgenes de rentabilidad"""
        try:
            for producto in productos:
                if producto.precio_base > 0:
                    margen = ((producto.precio_final - producto.precio_base) / producto.precio_base) * 100
                    producto.margen = round(margen, 2)
                else:
                    producto.margen = 0.0
            
            return productos
            
        except Exception as e:
            logger.error(f"Error calculando márgenes: {e}")
            return productos

    def validar_rentabilidad_final(self, productos: List[Producto]) -> List[Producto]:
        """Valida rentabilidad contra reglas cargadas"""
        try:
            for producto in productos:
                # Extraer línea del producto
                linea = self.extraer_linea_producto(producto)
                
                # Evaluar rentabilidad
                estado, margen_min, margen_opt = self.rentabilidad_validator.evaluar_rentabilidad(
                    producto.marca.value, 
                    producto.canal.value, 
                    linea, 
                    producto.margen
                )
                
                producto.estado_rentabilidad = estado
                producto.margen_minimo_esperado = margen_min
                producto.margen_optimo_esperado = margen_opt
                
                # Agregar alertas si es necesario
                if estado == 'Ajustar':
                    producto.alertas.append(TipoAlerta.MARGEN_BAJO)
                elif estado == 'Revisar':
                    producto.alertas.append(TipoAlerta.MARGEN_BAJO)
            
            return productos
            
        except Exception as e:
            logger.error(f"Error validando rentabilidad: {e}")
            return productos

    def extraer_linea_producto(self, producto: Producto) -> str:
        """Extrae la línea del producto"""
        try:
            nombre_lower = producto.nombre.lower()
            
            if any(keyword in nombre_lower for keyword in ['efb', 'enhanced flooded battery']):
                return 'efb'
            elif any(keyword in nombre_lower for keyword in ['agm', 'absorbed glass mat']):
                return 'agm'
            elif any(keyword in nombre_lower for keyword in ['gel', 'gel battery']):
                return 'gel'
            elif any(keyword in nombre_lower for keyword in ['estandar', 'standard']):
                return 'estandar'
            else:
                return 'general'
                
        except Exception as e:
            logger.warning(f"Error extrayendo línea de {producto.codigo}: {e}")
            return 'general'

    def generar_resumen_final(self, productos: List[Producto]) -> Dict:
        """Genera resumen final del proceso"""
        try:
            total_productos = len(productos)
            con_alertas = sum(1 for p in productos if p.alertas)
            rentabilidad_ok = sum(1 for p in productos if p.estado_rentabilidad == 'OK')
            rentabilidad_revisar = sum(1 for p in productos if p.estado_rentabilidad == 'Revisar')
            rentabilidad_ajustar = sum(1 for p in productos if p.estado_rentabilidad == 'Ajustar')
            
            margen_promedio = sum(p.margen for p in productos) / total_productos if total_productos > 0 else 0
            
            return {
                'total_productos': total_productos,
                'con_alertas': con_alertas,
                'rentabilidad_ok': rentabilidad_ok,
                'rentabilidad_revisar': rentabilidad_revisar,
                'rentabilidad_ajustar': rentabilidad_ajustar,
                'margen_promedio': round(margen_promedio, 2)
            }
            
        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
            return {}

    def cargar_precios(self, productos: List[Producto]) -> bool:
        """Marca que los precios están cargados"""
        try:
            self.precios_cargados = True
            logger.info(f"✅ Precios cargados: {len(productos)} productos")
            return True
        except Exception as e:
            logger.error(f"Error cargando precios: {e}")
            return False

    def cargar_rentabilidades(self, ruta_archivo: str) -> bool:
        """Carga rentabilidades y marca como completado"""
        try:
            resultado = self.rentabilidad_validator.cargar_rentabilidades(ruta_archivo)
            if resultado:
                self.rentabilidades_cargadas = True
                logger.info("✅ Rentabilidades cargadas exitosamente")
            return resultado
        except Exception as e:
            logger.error(f"Error cargando rentabilidades: {e}")
            return False

    def obtener_estado_proceso(self) -> Dict:
        """Obtiene el estado actual del proceso"""
        return {
            'precios_cargados': self.precios_cargados,
            'rentabilidades_cargadas': self.rentabilidades_cargadas,
            'relevamiento_realizado': self.relevamiento_realizado,
            'listo_para_procesar': self.precios_cargados and self.rentabilidades_cargadas
        } 