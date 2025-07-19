import pandas as pd
import re
from typing import List, Optional
from .models import Producto, Canal, Marca
import logging

logger = logging.getLogger(__name__)

class ExcelParser:
    def __init__(self):
        # Mapeo de nombres de marcas para normalización
        self.mapeo_marcas = {
            'moura': Marca.MOURA,
            'acubat': Marca.ACUBAT,
            'lubeck': Marca.LUBECK,
            'solar': Marca.SOLAR,
            'zx': Marca.SOLAR,  # ZX parece ser marca solar
            'lb': Marca.LUBECK,  # LB parece ser marca Lubeck
            'black series': Marca.ACUBAT,  # BLACK SERIES como marca premium
            'black': Marca.ACUBAT,
            'lüsqtoff': Marca.ACUBAT,  # LÜSQTOFF como marca principal
            'lusqtoff': Marca.ACUBAT,
            'accesorios': Marca.ACUBAT,  # ACCESORIOS como subcategoría
            'accesorios lusqtoff': Marca.ACUBAT
        }
        
        # Mapeo de canales
        self.mapeo_canales = {
            'minorista': Canal.MINORISTA,
            'mayorista': Canal.MAYORISTA,
            'distribuidor': Canal.DISTRIBUIDOR,
            'dist': Canal.DISTRIBUIDOR
        }

    def leer_excel(self, ruta_archivo: str) -> List[Producto]:
        """Lee un archivo Excel y retorna una lista de productos normalizados"""
        try:
            logger.info(f"Iniciando lectura de archivo: {ruta_archivo}")
            
            # Leer el archivo Excel con manejo de errores
            try:
                df = pd.read_excel(ruta_archivo)
            except Exception as e:
                logger.error(f"Error leyendo Excel: {e}")
                # Intentar con engine openpyxl
                try:
                    df = pd.read_excel(ruta_archivo, engine='openpyxl')
                except Exception as e2:
                    logger.error(f"Error con openpyxl: {e2}")
                    # Intentar con xlrd
                    try:
                        df = pd.read_excel(ruta_archivo, engine='xlrd')
                    except Exception as e3:
                        logger.error(f"Error con xlrd: {e3}")
                        raise Exception(f"No se pudo leer el archivo Excel: {e}")
            
            logger.info(f"Archivo Excel leído exitosamente: {ruta_archivo}")
            logger.info(f"Columnas encontradas: {list(df.columns)}")
            logger.info(f"Filas encontradas: {len(df)}")
            
            # Verificar que el DataFrame no esté vacío
            if df.empty:
                logger.warning("DataFrame vacío")
                return []
            
            # Limpiar datos
            df = self.limpiar_dataframe(df)
            
            # Normalizar columnas
            df = self.normalizar_columnas(df)
            
            # Convertir a productos
            productos = self.convertir_a_productos(df)
            
            logger.info(f"Productos procesados: {len(productos)}")
            return productos
            
        except Exception as e:
            logger.error(f"Error al leer archivo Excel: {e}")
            raise

    def limpiar_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia el DataFrame eliminando filas vacías y headers duplicados"""
        try:
            # Eliminar filas completamente vacías
            df = df.dropna(how='all')
            
            # Si la primera fila parece ser un header (contiene palabras como 'marca', 'modelo', etc.)
            primera_fila = df.iloc[0]
            es_header = any(
                str(val).lower().strip() in ['marca', 'modelo', 'descripcion', 'precio', 'pvp', 'lista', 'rubro']
                for val in primera_fila if pd.notna(val) and str(val).strip()
            )
            
            if es_header:
                logger.info("Detectado header en primera fila, usando como nombres de columnas")
                # Usar la primera fila como nombres de columnas
                df.columns = df.iloc[0]
                df = df.iloc[1:].reset_index(drop=True)
                # Eliminar filas vacías nuevamente
                df = df.dropna(how='all')
            
            logger.info(f"DataFrame limpio: {len(df)} filas, {len(df.columns)} columnas")
            return df
            
        except Exception as e:
            logger.error(f"Error limpiando DataFrame: {e}")
            return df

    def normalizar_columnas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza los nombres de las columnas del DataFrame"""
        try:
            # Mapeo de nombres de columnas
            mapeo_columnas = {}
            
            for col in df.columns:
                col_lower = str(col).lower().strip()
                logger.info(f"Procesando columna: '{col}' -> '{col_lower}'")
                
                # Mapeo flexible de columnas
                if any(keyword in col_lower for keyword in ['modelo', 'codigo', 'code']):
                    mapeo_columnas[col] = 'codigo'
                    logger.info(f"  -> Mapeada a 'codigo'")
                elif any(keyword in col_lower for keyword in ['descripcion', 'nombre', 'producto', 'name']):
                    mapeo_columnas[col] = 'nombre'
                    logger.info(f"  -> Mapeada a 'nombre'")
                elif any(keyword in col_lower for keyword in ['precio lista', 'precio_base', 'base']):
                    mapeo_columnas[col] = 'precio_base'
                    logger.info(f"  -> Mapeada a 'precio_base'")
                elif any(keyword in col_lower for keyword in ['pvp', 'precio final', 'final', 'venta']):
                    mapeo_columnas[col] = 'precio_final'
                    logger.info(f"  -> Mapeada a 'precio_final'")
                elif any(keyword in col_lower for keyword in ['marca', 'brand']):
                    mapeo_columnas[col] = 'marca'
                    logger.info(f"  -> Mapeada a 'marca'")
                elif any(keyword in col_lower for keyword in ['rubro', 'categoria', 'category']):
                    mapeo_columnas[col] = 'categoria'
                    logger.info(f"  -> Mapeada a 'categoria'")
                elif any(keyword in col_lower for keyword in ['stock', 'cantidad', 'qty', 'q. pallet']):
                    mapeo_columnas[col] = 'stock'
                    logger.info(f"  -> Mapeada a 'stock'")
                else:
                    logger.info(f"  -> No mapeada (columna opcional)")
            
            # Renombrar columnas
            df = df.rename(columns=mapeo_columnas)
            
            logger.info(f"Columnas después de normalizar: {list(df.columns)}")
            return df
            
        except Exception as e:
            logger.error(f"Error normalizando columnas: {e}")
            return df

    def convertir_a_productos(self, df: pd.DataFrame) -> List[Producto]:
        """Convierte el DataFrame a una lista de productos"""
        productos = []
        
        # Verificar columnas mínimas requeridas
        columnas_requeridas = ['codigo', 'nombre']
        columnas_disponibles = list(df.columns)
        
        # Si no tenemos las columnas requeridas, intentar con las disponibles
        if not all(col in columnas_disponibles for col in columnas_requeridas):
            logger.warning(f"Columnas requeridas no encontradas: {columnas_requeridas}")
            logger.info(f"Columnas disponibles: {columnas_disponibles}")
            
            # Intentar mapear columnas disponibles
            for col in columnas_disponibles:
                col_lower = str(col).lower()
                if 'modelo' in col_lower or 'codigo' in col_lower:
                    df = df.rename(columns={col: 'codigo'})
                elif 'descripcion' in col_lower or 'nombre' in col_lower:
                    df = df.rename(columns={col: 'nombre'})
        
        for index, row in df.iterrows():
            try:
                producto = self.fila_a_producto(row, index)
                if producto:
                    productos.append(producto)
            except Exception as e:
                logger.warning(f"Error procesando fila {index}: {e}")
                continue
        
        logger.info(f"Productos convertidos exitosamente: {len(productos)}")
        return productos

    def fila_a_producto(self, row: pd.Series, index: int) -> Optional[Producto]:
        """Convierte una fila del DataFrame a un objeto Producto"""
        try:
            # Extraer datos básicos con valores por defecto
            codigo = str(row.get('codigo', f'PROD_{index}')).strip()
            if pd.isna(codigo) or codigo == '':
                codigo = f'PROD_{index}'
            
            nombre = str(row.get('nombre', f'Producto {index}')).strip()
            if pd.isna(nombre) or nombre == '':
                nombre = f'Producto {index}'
            
            # Extraer precios con manejo de errores
            precio_base = self.extraer_precio_seguro(row, 'precio_base', 0.0)
            precio_final = self.extraer_precio_seguro(row, 'precio_final', precio_base)
            
            # Si no hay precio final, usar precio base
            if precio_final == 0.0:
                precio_final = precio_base
            
            # Determinar marca y canal
            marca = self.determinar_marca_segura(row, codigo)
            canal = self.determinar_canal_seguro(row)
            
            # Extraer capacidad
            capacidad = self.extraer_capacidad_segura(row)
            
            # Crear producto
            producto = Producto(
                codigo=codigo,
                nombre=nombre,
                marca=marca,
                canal=canal,
                categoria="General",
                precio_base=precio_base,
                precio_final=precio_final,
                stock=0,
                capacidad=capacidad,
                alertas=[],
                sugerencias_openai="",
                margen=0.0
            )
            
            logger.info(f"Producto creado: {codigo} - {nombre}")
            return producto
            
        except Exception as e:
            logger.error(f"Error creando producto de fila {index}: {e}")
            return None

    def extraer_precio_seguro(self, row: pd.Series, columna: str, valor_default: float) -> float:
        """Extrae precio de forma segura con manejo de errores"""
        try:
            valor = row.get(columna, valor_default)
            if pd.isna(valor) or valor == '':
                return valor_default
            
            # Convertir a string y limpiar
            valor_str = str(valor).strip()
            if not valor_str:
                return valor_default
            
            # Remover caracteres no numéricos excepto punto y coma
            valor_limpio = re.sub(r'[^\d.,]', '', valor_str)
            if not valor_limpio:
                return valor_default
            
            # Convertir coma a punto si es necesario
            valor_limpio = valor_limpio.replace(',', '.')
            
            # Convertir a float
            return float(valor_limpio)
            
        except Exception as e:
            logger.warning(f"Error extrayendo precio de {columna}: {e}")
            return valor_default

    def determinar_marca_segura(self, row: pd.Series, codigo: str) -> Marca:
        """Determina marca de forma segura"""
        try:
            marca_str = str(row.get('marca', '')).lower().strip()
            
            # Buscar en mapeo
            for clave, marca_enum in self.mapeo_marcas.items():
                if clave in marca_str:
                    return marca_enum
            
            # Determinar por código
            codigo_lower = codigo.lower()
            for clave, marca_enum in self.mapeo_marcas.items():
                if clave in codigo_lower:
                    return marca_enum
            
            # Por defecto
            return Marca.ACUBAT
            
        except Exception as e:
            logger.warning(f"Error determinando marca: {e}")
            return Marca.ACUBAT

    def determinar_canal_seguro(self, row: pd.Series) -> Canal:
        """Determina canal de forma segura"""
        try:
            categoria_str = str(row.get('categoria', '')).lower().strip()
            
            # Buscar en mapeo
            for clave, canal_enum in self.mapeo_canales.items():
                if clave in categoria_str:
                    return canal_enum
            
            # Por defecto
            return Canal.MINORISTA
            
        except Exception as e:
            logger.warning(f"Error determinando canal: {e}")
            return Canal.MINORISTA

    def extraer_capacidad_segura(self, row: pd.Series) -> Optional[str]:
        """Extrae capacidad de forma segura"""
        try:
            # Buscar en nombre o código
            nombre = str(row.get('nombre', ''))
            codigo = str(row.get('codigo', ''))
            
            # Patrón para encontrar capacidad
            patron = r'(\d+)\s*(ah|amper|amp|v|volt)'
            
            # Buscar en nombre
            match = re.search(patron, nombre, re.IGNORECASE)
            if match:
                return match.group(0)
            
            # Buscar en código
            match = re.search(patron, codigo, re.IGNORECASE)
            if match:
                return match.group(0)
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extrayendo capacidad: {e}")
            return None

    # Métodos legacy para compatibilidad
    def extraer_codigo(self, row: pd.Series) -> str:
        return str(row.get('codigo', 'SIN_CODIGO')).strip()
    
    def extraer_nombre(self, row: pd.Series) -> str:
        return str(row.get('nombre', 'Producto sin nombre')).strip()
    
    def extraer_capacidad(self, row: pd.Series) -> Optional[str]:
        return self.extraer_capacidad_segura(row)
    
    def determinar_marca(self, row: pd.Series, codigo: str) -> Marca:
        return self.determinar_marca_segura(row, codigo)
    
    def determinar_canal(self, row: pd.Series) -> Canal:
        return self.determinar_canal_seguro(row)
    
    def extraer_precio_base(self, row: pd.Series) -> float:
        return self.extraer_precio_seguro(row, 'precio_base', 0.0)
    
    def extraer_precio_final(self, row: pd.Series) -> float:
        return self.extraer_precio_seguro(row, 'precio_final', 0.0)

    def crear_archivo_ejemplo(self, ruta_archivo: str = "data/ejemplo_productos.xlsx"):
        """Crea un archivo Excel de ejemplo para testing"""
        try:
            import os
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
            
            # Datos de ejemplo
            datos = {
                'MODELO': ['BAT001', 'BAT002', 'BAT003'],
                'DESCRIPCION': ['Batería 12V 100Ah', 'Batería 12V 200Ah', 'Batería 24V 100Ah'],
                'MARCA': ['ACUBAT', 'ACUBAT', 'ACUBAT'],
                'RUBRO': ['Baterías', 'Baterías', 'Baterías'],
                'PRECIO LISTA': [150000, 280000, 320000],
                'PVP ON LINE': [180000, 336000, 384000],
                'Q. PALLET': [10, 5, 8]
            }
            
            df = pd.DataFrame(datos)
            df.to_excel(ruta_archivo, index=False)
            
            logger.info(f"Archivo de ejemplo creado: {ruta_archivo}")
            return ruta_archivo
            
        except Exception as e:
            logger.error(f"Error creando archivo de ejemplo: {e}")
            return None 