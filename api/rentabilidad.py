import pandas as pd
import logging
from typing import Dict, Tuple, Optional, List
from .models import Marca, Canal
import re

logger = logging.getLogger(__name__)

class RentabilidadValidator:
    def __init__(self):
        self.tabla_rentabilidad = {}
        self.archivo_cargado = False
        
    def cargar_rentabilidades(self, file_path: str) -> bool:
        """
        Carga archivo de rentabilidades con soporte para múltiples hojas
        """
        try:
            logger.info(f"Cargando archivo de rentabilidades: {file_path}")
            
            # Usar el nuevo método que maneja múltiples hojas
            return self.leer_archivo_rentabilidad(file_path)
            
        except Exception as e:
            logger.error(f"Error al cargar rentabilidades: {str(e)}")
            return False
    
    def normalizar_columnas(self, columnas) -> list:
        """
        Normaliza nombres de columnas para rentabilidad
        """
        try:
            columnas_normalizadas = []
            
            for col in columnas:
                col_str = str(col).strip().lower()
                
                # Mapeo de nombres de columnas
                if any(keyword in col_str for keyword in ['canal', 'channel']):
                    columnas_normalizadas.append('canal')
                elif any(keyword in col_str for keyword in ['línea', 'linea', 'line', 'producto', 'product']):
                    columnas_normalizadas.append('linea')
                elif any(keyword in col_str for keyword in ['margen mínimo', 'margen_minimo', 'minimo', 'min', 'margen min']):
                    columnas_normalizadas.append('margen_minimo')
                elif any(keyword in col_str for keyword in ['margen óptimo', 'margen_optimo', 'optimo', 'opt', 'margen opt']):
                    columnas_normalizadas.append('margen_optimo')
                else:
                    columnas_normalizadas.append(col_str)
            
            return columnas_normalizadas
            
        except Exception as e:
            logger.error(f"Error normalizando columnas de rentabilidad: {e}")
            return list(columnas)
    
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
    
    def normalizar_canal(self, canal: str) -> str:
        """Normaliza el nombre del canal"""
        if not canal:
            return "Minorista"
        
        canal_lower = canal.lower().strip()
        
        if any(keyword in canal_lower for keyword in ['minorista', 'retail', 'tienda']):
            return "Minorista"
        elif any(keyword in canal_lower for keyword in ['mayorista', 'wholesale', 'distribuidor']):
            return "Mayorista"
        elif any(keyword in canal_lower for keyword in ['distribuidor', 'dealer']):
            return "Distribuidor"
        else:
            return canal.title()
    
    def normalizar_linea(self, linea: str) -> str:
        """Normaliza el nombre de la línea"""
        if not linea:
            return "Estándar"
        
        linea_lower = linea.lower().strip()
        
        if any(keyword in linea_lower for keyword in ['estándar', 'estandar', 'standard']):
            return "Estándar"
        elif any(keyword in linea_lower for keyword in ['efb', 'enhanced']):
            return "EFB"
        elif any(keyword in linea_lower for keyword in ['agm', 'gel']):
            return "AGM"
        elif any(keyword in linea_lower for keyword in ['premium', 'alta']):
            return "Premium"
        elif any(keyword in linea_lower for keyword in ['asiática', 'asiatica', 'asian']):
            return "Asiática"
        else:
            return linea.title()
    
    def extraer_porcentaje(self, valor) -> Optional[float]:
        """Extrae porcentaje de un valor"""
        if pd.isna(valor):
            return None
        
        if isinstance(valor, (int, float)):
            return float(valor)
        
        if isinstance(valor, str):
            # Limpiar símbolos de porcentaje y espacios
            cleaned = re.sub(r'[^\d.,]', '', valor)
            if cleaned:
                # Convertir coma decimal a punto
                cleaned = cleaned.replace(',', '.')
                try:
                    return float(cleaned)
                except:
                    return None
        
        return None
    
    def evaluar_rentabilidad(self, marca: str, canal: str, linea: str, margen_actual: float) -> Tuple[str, Optional[float], Optional[float]]:
        """
        Evalúa la rentabilidad de un producto contra las reglas cargadas
        
        Returns:
            Tuple[estado, margen_minimo_esperado, margen_optimo_esperado]
        """
        try:
            # Normalizar parámetros
            marca_norm = marca.title() if marca else "General"
            canal_norm = self.normalizar_canal(canal)
            linea_norm = self.normalizar_linea(linea)
            
            # Buscar regla correspondiente
            clave = (marca_norm, canal_norm, linea_norm)
            
            if clave not in self.tabla_rentabilidad:
                logger.warning(f"No se encontró regla para: {marca_norm} - {canal_norm} - {linea_norm}")
                return "Sin ref.", None, None
            
            regla = self.tabla_rentabilidad[clave]
            margen_minimo = regla.get('margen_minimo', 20)
            margen_optimo = regla.get('margen_optimo', 30)
            
            # Evaluar estado
            if margen_actual >= margen_optimo:
                estado = "OK"
            elif margen_actual >= margen_minimo:
                estado = "Revisar"
            else:
                estado = "Ajustar"
            
            logger.debug(f"Evaluación rentabilidad: {marca_norm} - {canal_norm} - {linea_norm} = {estado} (actual: {margen_actual}%, min: {margen_minimo}%, opt: {margen_optimo}%)")
            
            return estado, margen_minimo, margen_optimo
            
        except Exception as e:
            logger.error(f"Error evaluando rentabilidad: {str(e)}")
            return "Error", None, None
    
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
        """Obtiene un resumen de las rentabilidades cargadas"""
        try:
            if not self.archivo_cargado:
                return {
                    'total_reglas': 0,
                    'por_marca': {},
                    'por_canal': {},
                    'por_linea': {},
                    'archivo': None
                }
            
            # Contar reglas por categoría
            por_marca = {}
            por_canal = {}
            por_linea = {}
            
            for (marca, canal, linea), regla in self.tabla_rentabilidad.items():
                # Contar por marca
                por_marca[marca] = por_marca.get(marca, 0) + 1
                
                # Contar por canal
                por_canal[canal] = por_canal.get(canal, 0) + 1
                
                # Contar por línea
                por_linea[linea] = por_linea.get(linea, 0) + 1
            
            return {
                'total_reglas': len(self.tabla_rentabilidad),
                'por_marca': por_marca,
                'por_canal': por_canal,
                'por_linea': por_linea,
                'archivo': self.archivo_origen
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen de rentabilidad: {e}")
            return {
                'total_reglas': 0,
                'por_marca': {},
                'por_canal': {},
                'por_linea': {},
                'archivo': None
            }
    
    def leer_archivo_rentabilidad(self, file_path: str) -> bool:
        """
        Lee archivo de rentabilidades con hojas específicas por marca
        """
        try:
            # Leer todas las hojas del archivo
            excel_file = pd.ExcelFile(file_path)
            logger.info(f"Archivo de rentabilidades con {len(excel_file.sheet_names)} hojas: {excel_file.sheet_names}")
            
            reglas_cargadas = 0
            
            for sheet_name in excel_file.sheet_names:
                logger.info(f"Procesando hoja de rentabilidad: {sheet_name}")
                
                # Leer la hoja
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Normalizar nombres de columnas
                df.columns = self.normalizar_columnas(df.columns)
                
                # Determinar marca basada en el nombre de la hoja
                marca_hoja = self.determinar_marca_desde_hoja(sheet_name)
                
                # Procesar reglas de esta hoja
                reglas_hoja = self.procesar_hoja_rentabilidad(df, marca_hoja)
                reglas_cargadas += len(reglas_hoja)
                
                # Agregar reglas al diccionario principal
                for regla in reglas_hoja:
                    clave = (regla['marca'], regla['canal'], regla['linea'])
                    self.tabla_rentabilidad[clave] = regla
            
            logger.info(f"Total de reglas de rentabilidad cargadas: {reglas_cargadas}")
            self.archivo_cargado = reglas_cargadas > 0
            self.archivo_origen = file_path
            
            return self.archivo_cargado
            
        except Exception as e:
            logger.error(f"Error al leer archivo de rentabilidad: {str(e)}")
            return False
    
    def determinar_marca_desde_hoja(self, sheet_name: str) -> str:
        """
        Determina la marca basada en el nombre de la hoja
        """
        sheet_lower = sheet_name.lower().strip()
        
        # Mapeo de nombres de hoja a marcas
        mapeo_marcas = {
            'moura': 'Moura',
            'acubat': 'Acubat', 
            'lubeck': 'Lubeck',
            'solar': 'Solar',
            'zetta': 'Zetta',
            'rentabilidades': 'General',  # Hoja general
            'general': 'General'
        }
        
        # Buscar coincidencias
        for key, marca in mapeo_marcas.items():
            if key in sheet_lower:
                logger.info(f"Hoja '{sheet_name}' mapeada a marca: {marca}")
                return marca
        
        # Si no encuentra coincidencia, usar el nombre de la hoja
        logger.info(f"Hoja '{sheet_name}' sin mapeo específico, usando como marca")
        return sheet_name.title()
    
    def procesar_hoja_rentabilidad(self, df: pd.DataFrame, marca_hoja: str) -> List[Dict]:
        """
        Procesa una hoja específica de rentabilidad
        """
        reglas = []
        
        # Buscar columnas requeridas
        columnas_requeridas = ['canal', 'linea', 'margen_minimo', 'margen_optimo']
        columnas_disponibles = [col for col in columnas_requeridas if col in df.columns]
        
        if len(columnas_disponibles) < 3:  # Al menos canal, línea y un margen
            logger.warning(f"Hoja {marca_hoja}: Columnas insuficientes. Disponibles: {list(df.columns)}")
            return reglas
        
        # Procesar cada fila
        for idx, row in df.iterrows():
            try:
                # Extraer datos básicos
                canal = self.normalizar_canal(str(row.get('canal', '')).strip())
                linea = self.normalizar_linea(str(row.get('linea', '')).strip())
                margen_minimo = self.extraer_porcentaje(row.get('margen_minimo'))
                margen_optimo = self.extraer_porcentaje(row.get('margen_optimo'))
                
                # Validar datos mínimos
                if not canal or not linea:
                    continue
                
                if margen_minimo is None and margen_optimo is None:
                    continue
                
                # Usar valores por defecto si no están disponibles
                if margen_minimo is None:
                    margen_minimo = margen_optimo * 0.7 if margen_optimo else 20
                if margen_optimo is None:
                    margen_optimo = margen_minimo * 1.4 if margen_minimo else 30
                
                regla = {
                    'marca': marca_hoja,
                    'canal': canal,
                    'linea': linea,
                    'margen_minimo': margen_minimo,
                    'margen_optimo': margen_optimo,
                    'hoja_origen': marca_hoja
                }
                
                reglas.append(regla)
                logger.debug(f"Regla cargada: {marca_hoja} - {canal} - {linea} - Min: {margen_minimo}% - Opt: {margen_optimo}%")
                
            except Exception as e:
                logger.warning(f"Error procesando fila {idx} en hoja {marca_hoja}: {str(e)}")
                continue
        
        logger.info(f"Hoja {marca_hoja}: {len(reglas)} reglas procesadas")
        return reglas 