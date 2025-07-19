import pandas as pd
import logging
from typing import Dict, Tuple, Optional
from .models import Marca, Canal

logger = logging.getLogger(__name__)

class RentabilidadValidator:
    def __init__(self):
        self.tabla_rentabilidad = {}
        self.archivo_cargado = False
        
    def cargar_rentabilidades(self, ruta_archivo: str) -> bool:
        """Carga el archivo de rentabilidades y estructura los datos"""
        try:
            logger.info(f"Cargando archivo de rentabilidades: {ruta_archivo}")
            
            # Leer el archivo Excel
            df = pd.read_excel(ruta_archivo)
            logger.info(f"Archivo leído: {len(df)} filas, {len(df.columns)} columnas")
            logger.info(f"Columnas encontradas: {list(df.columns)}")
            
            # Normalizar columnas
            df = self.normalizar_columnas(df)
            
            # Procesar datos
            self.procesar_datos_rentabilidad(df)
            
            self.archivo_cargado = True
            logger.info(f"Rentabilidades cargadas: {len(self.tabla_rentabilidad)} reglas")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando rentabilidades: {e}")
            return False
    
    def normalizar_columnas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza los nombres de las columnas del archivo de rentabilidades"""
        try:
            # Mapeo de columnas esperadas
            mapeo_columnas = {}
            
            for col in df.columns:
                col_lower = str(col).lower().strip()
                logger.info(f"Procesando columna rentabilidad: '{col}' -> '{col_lower}'")
                
                if any(keyword in col_lower for keyword in ['marca', 'brand']):
                    mapeo_columnas[col] = 'marca'
                    logger.info(f"  -> Mapeada a 'marca'")
                elif any(keyword in col_lower for keyword in ['canal', 'channel']):
                    mapeo_columnas[col] = 'canal'
                    logger.info(f"  -> Mapeada a 'canal'")
                elif any(keyword in col_lower for keyword in ['linea', 'line', 'tipo', 'categoria']):
                    mapeo_columnas[col] = 'linea'
                    logger.info(f"  -> Mapeada a 'linea'")
                elif any(keyword in col_lower for keyword in ['margen minimo', 'minimo', 'min', 'minimo margen']):
                    mapeo_columnas[col] = 'margen_minimo'
                    logger.info(f"  -> Mapeada a 'margen_minimo'")
                elif any(keyword in col_lower for keyword in ['margen optimo', 'optimo', 'opt', 'optimo margen']):
                    mapeo_columnas[col] = 'margen_optimo'
                    logger.info(f"  -> Mapeada a 'margen_optimo'")
                else:
                    logger.info(f"  -> No mapeada (columna opcional)")
            
            # Renombrar columnas
            df = df.rename(columns=mapeo_columnas)
            
            logger.info(f"Columnas después de normalizar: {list(df.columns)}")
            return df
            
        except Exception as e:
            logger.error(f"Error normalizando columnas de rentabilidad: {e}")
            return df
    
    def procesar_datos_rentabilidad(self, df: pd.DataFrame):
        """Procesa los datos de rentabilidad y crea la tabla de reglas"""
        try:
            # Verificar columnas requeridas
            columnas_requeridas = ['marca', 'canal', 'linea', 'margen_minimo', 'margen_optimo']
            columnas_disponibles = list(df.columns)
            
            columnas_faltantes = []
            for col_req in columnas_requeridas:
                if col_req not in columnas_disponibles:
                    columnas_faltantes.append(col_req)
            
            if columnas_faltantes:
                logger.warning(f"Columnas faltantes en rentabilidades: {columnas_faltantes}")
                logger.info(f"Columnas disponibles: {columnas_disponibles}")
                
                # Intentar mapear columnas disponibles
                for col in columnas_disponibles:
                    col_lower = str(col).lower()
                    if 'marca' in col_lower and 'marca' not in columnas_disponibles:
                        df = df.rename(columns={col: 'marca'})
                    elif 'canal' in col_lower and 'canal' not in columnas_disponibles:
                        df = df.rename(columns={col: 'canal'})
                    elif any(keyword in col_lower for keyword in ['linea', 'tipo']) and 'linea' not in columnas_disponibles:
                        df = df.rename(columns={col: 'linea'})
                    elif 'minimo' in col_lower and 'margen_minimo' not in columnas_disponibles:
                        df = df.rename(columns={col: 'margen_minimo'})
                    elif 'optimo' in col_lower and 'margen_optimo' not in columnas_disponibles:
                        df = df.rename(columns={col: 'margen_optimo'})
            
            # Procesar cada fila
            for index, row in df.iterrows():
                try:
                    # Extraer datos
                    marca_str = str(row.get('marca', '')).strip()
                    canal_str = str(row.get('canal', '')).strip()
                    linea_str = str(row.get('linea', '')).strip()
                    
                    # Convertir márgenes a float
                    margen_minimo = self.convertir_porcentaje(row.get('margen_minimo', 0))
                    margen_optimo = self.convertir_porcentaje(row.get('margen_optimo', 0))
                    
                    # Normalizar marca y canal
                    marca = self.normalizar_marca(marca_str)
                    canal = self.normalizar_canal(canal_str)
                    
                    if marca and canal and linea_str:
                        # Crear clave única
                        clave = (marca.value, canal.value, linea_str.lower())
                        
                        # Guardar regla
                        self.tabla_rentabilidad[clave] = {
                            'marca': marca,
                            'canal': canal,
                            'linea': linea_str,
                            'margen_minimo': margen_minimo,
                            'margen_optimo': margen_optimo
                        }
                        
                        logger.info(f"Regla agregada: {marca.value} - {canal.value} - {linea_str} (min: {margen_minimo}%, opt: {margen_optimo}%)")
                    
                except Exception as e:
                    logger.warning(f"Error procesando fila {index} de rentabilidades: {e}")
                    continue
            
            logger.info(f"Procesadas {len(self.tabla_rentabilidad)} reglas de rentabilidad")
            
        except Exception as e:
            logger.error(f"Error procesando datos de rentabilidad: {e}")
    
    def convertir_porcentaje(self, valor) -> float:
        """Convierte un valor a porcentaje float"""
        try:
            if pd.isna(valor) or valor == '':
                return 0.0
            
            valor_str = str(valor).strip()
            if not valor_str:
                return 0.0
            
            # Remover símbolo de porcentaje si existe
            valor_str = valor_str.replace('%', '').replace(' ', '')
            
            # Convertir a float
            valor_float = float(valor_str)
            
            # Si el valor es mayor a 1, asumir que ya es porcentaje
            # Si es menor a 1, multiplicar por 100
            if valor_float < 1:
                valor_float *= 100
            
            return valor_float
            
        except Exception as e:
            logger.warning(f"Error convirtiendo porcentaje '{valor}': {e}")
            return 0.0
    
    def normalizar_marca(self, marca_str: str) -> Optional[Marca]:
        """Normaliza el string de marca a enum Marca"""
        try:
            marca_lower = marca_str.lower().strip()
            
            # Mapeo de marcas
            mapeo_marcas = {
                'moura': Marca.MOURA,
                'acubat': Marca.ACUBAT,
                'lubeck': Marca.LUBECK,
                'solar': Marca.SOLAR,
                'zetta': Marca.SOLAR,  # Zetta como marca solar
                'zx': Marca.SOLAR,
                'lb': Marca.LUBECK
            }
            
            for clave, marca_enum in mapeo_marcas.items():
                if clave in marca_lower:
                    return marca_enum
            
            return None
            
        except Exception as e:
            logger.warning(f"Error normalizando marca '{marca_str}': {e}")
            return None
    
    def normalizar_canal(self, canal_str: str) -> Optional[Canal]:
        """Normaliza el string de canal a enum Canal"""
        try:
            from .models import Canal
            
            canal_lower = canal_str.lower().strip()
            
            # Mapeo de canales
            mapeo_canales = {
                'minorista': Canal.MINORISTA,
                'mayorista': Canal.MAYORISTA,
                'distribuidor': Canal.DISTRIBUIDOR,
                'dist': Canal.DISTRIBUIDOR
            }
            
            for clave, canal_enum in mapeo_canales.items():
                if clave in canal_lower:
                    return canal_enum
            
            return None
            
        except Exception as e:
            logger.warning(f"Error normalizando canal '{canal_str}': {e}")
            return None
    
    def evaluar_rentabilidad(self, producto) -> Dict:
        """Evalúa la rentabilidad de un producto según las reglas cargadas"""
        try:
            if not self.archivo_cargado:
                return {
                    'estado': 'Sin referencia',
                    'mensaje': 'Archivo de rentabilidades no cargado',
                    'margen_minimo': 0,
                    'margen_optimo': 0,
                    'diferencia': 0
                }
            
            # Obtener datos del producto
            marca = producto.marca.value
            canal = producto.canal.value
            linea = self.extraer_linea_producto(producto)
            margen_actual = producto.margen
            
            # Buscar regla específica
            clave_especifica = (marca, canal, linea)
            regla = self.tabla_rentabilidad.get(clave_especifica)
            
            # Si no hay regla específica, buscar por marca y canal
            if not regla:
                clave_general = (marca, canal, 'general')
                regla = self.tabla_rentabilidad.get(clave_general)
            
            # Si no hay regla, buscar solo por marca
            if not regla:
                clave_marca = (marca, 'general', 'general')
                regla = self.tabla_rentabilidad.get(clave_marca)
            
            if not regla:
                return {
                    'estado': 'Sin referencia',
                    'mensaje': f'No hay regla para {marca} - {canal} - {linea}',
                    'margen_minimo': 0,
                    'margen_optimo': 0,
                    'diferencia': 0
                }
            
            # Evaluar margen
            margen_minimo = regla['margen_minimo']
            margen_optimo = regla['margen_optimo']
            
            if margen_actual < margen_minimo:
                estado = 'Ajustar'
                mensaje = f'Margen {margen_actual:.1f}% < mínimo {margen_minimo:.1f}%'
            elif margen_actual < margen_optimo:
                estado = 'Revisar'
                mensaje = f'Margen {margen_actual:.1f}% entre mínimo y óptimo'
            else:
                estado = 'OK'
                mensaje = f'Margen {margen_actual:.1f}% ≥ óptimo {margen_optimo:.1f}%'
            
            return {
                'estado': estado,
                'mensaje': mensaje,
                'margen_minimo': margen_minimo,
                'margen_optimo': margen_optimo,
                'diferencia': margen_actual - margen_minimo
            }
            
        except Exception as e:
            logger.error(f"Error evaluando rentabilidad de {producto.codigo}: {e}")
            return {
                'estado': 'Error',
                'mensaje': f'Error en evaluación: {str(e)}',
                'margen_minimo': 0,
                'margen_optimo': 0,
                'diferencia': 0
            }
    
    def extraer_linea_producto(self, producto) -> str:
        """Extrae la línea del producto basándose en su información"""
        try:
            # Buscar en nombre
            nombre_lower = producto.nombre.lower()
            codigo_lower = producto.codigo.lower()
            
            # Detectar líneas por patrones
            if any(keyword in nombre_lower for keyword in ['efb', 'enhanced flooded battery']):
                return 'efb'
            elif any(keyword in nombre_lower for keyword in ['agm', 'absorbed glass mat']):
                return 'agm'
            elif any(keyword in nombre_lower for keyword in ['gel', 'gel battery']):
                return 'gel'
            elif any(keyword in nombre_lower for keyword in ['estandar', 'standard', 'convencional']):
                return 'estandar'
            elif any(keyword in nombre_lower for keyword in ['asiatica', 'asian']):
                return 'asiatica'
            elif any(keyword in nombre_lower for keyword in ['premium', 'alta gama']):
                return 'premium'
            else:
                return 'general'
                
        except Exception as e:
            logger.warning(f"Error extrayendo línea de producto {producto.codigo}: {e}")
            return 'general'
    
    def obtener_resumen_rentabilidad(self) -> Dict:
        """Obtiene un resumen de las reglas de rentabilidad cargadas"""
        try:
            resumen = {
                'total_reglas': len(self.tabla_rentabilidad),
                'por_marca': {},
                'por_canal': {},
                'por_linea': {}
            }
            
            for clave, regla in self.tabla_rentabilidad.items():
                marca = regla['marca'].value
                canal = regla['canal'].value
                linea = regla['linea']
                
                # Contar por marca
                if marca not in resumen['por_marca']:
                    resumen['por_marca'][marca] = 0
                resumen['por_marca'][marca] += 1
                
                # Contar por canal
                if canal not in resumen['por_canal']:
                    resumen['por_canal'][canal] = 0
                resumen['por_canal'][canal] += 1
                
                # Contar por línea
                if linea not in resumen['por_linea']:
                    resumen['por_linea'][linea] = 0
                resumen['por_linea'][linea] += 1
            
            return resumen
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen de rentabilidad: {e}")
            return {'total_reglas': 0, 'por_marca': {}, 'por_canal': {}, 'por_linea': {}} 