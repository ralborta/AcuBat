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
            # Leer el archivo Excel
            df = pd.read_excel(ruta_archivo)
            logger.info(f"Archivo Excel leído exitosamente: {ruta_archivo}")
            logger.info(f"Columnas encontradas: {list(df.columns)}")
            logger.info(f"Filas encontradas: {len(df)}")
            
            # Normalizar columnas
            df = self.normalizar_columnas(df)
            
            # Convertir a productos
            productos = self.convertir_a_productos(df)
            
            logger.info(f"Productos procesados: {len(productos)}")
            return productos
            
        except Exception as e:
            logger.error(f"Error al leer archivo Excel: {e}")
            raise

    def normalizar_columnas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza los nombres de las columnas del DataFrame"""
        # Mapeo de nombres de columnas específicas para archivos LÜSQTOFF
        mapeo_columnas = {
            'codigo': ['modelo'],  # MODELO es el código del producto
            'nombre': ['descripcion'],  # DESCRIPCION es el nombre del producto
            'marca': ['marca'],  # MARCA
            'categoria': ['rubro', 'subrubro'],  # RUBRO y SUBRUBRO
            'precio_base': ['precio lista'],  # PRECIO LISTA
            'precio_final': ['pvp on line'],  # PVP On line
            'stock': ['q. pallet', 'inner', 'master']  # Cantidades
        }
        
        # Normalizar nombres de columnas
        columnas_normalizadas = {}
        for columna_objetivo, posibles_nombres in mapeo_columnas.items():
            for nombre_posible in posibles_nombres:
                if nombre_posible in df.columns:
                    columnas_normalizadas[nombre_posible] = columna_objetivo
                    break
        
        # Mapeo exacto para columnas específicas
        for col in df.columns:
            col_lower = str(col).lower().strip()
            logger.info(f"Procesando columna: '{col}' -> '{col_lower}'")
            
            # Mapeo exacto para archivos LÜSQTOFF
            if col_lower == 'modelo':
                columnas_normalizadas[col] = 'codigo'
                logger.info(f"  -> Mapeada a 'codigo'")
            elif col_lower == 'descripcion':
                columnas_normalizadas[col] = 'nombre'
                logger.info(f"  -> Mapeada a 'nombre'")
            elif col_lower == 'precio lista':
                columnas_normalizadas[col] = 'precio_base'
                logger.info(f"  -> Mapeada a 'precio_base'")
            elif col_lower == 'pvp on line':
                columnas_normalizadas[col] = 'precio_final'
                logger.info(f"  -> Mapeada a 'precio_final'")
            elif col_lower == 'marca':
                columnas_normalizadas[col] = 'marca'
                logger.info(f"  -> Mapeada a 'marca'")
            elif col_lower == 'rubro':
                columnas_normalizadas[col] = 'categoria'
                logger.info(f"  -> Mapeada a 'categoria'")
            elif col_lower == 'q. pallet':
                columnas_normalizadas[col] = 'stock'
                logger.info(f"  -> Mapeada a 'stock'")
            else:
                logger.info(f"  -> No mapeada (columna opcional)")
        
        # Renombrar columnas
        df = df.rename(columns=columnas_normalizadas)
        
        return df

    def convertir_a_productos(self, df: pd.DataFrame) -> List[Producto]:
        """Convierte el DataFrame a una lista de productos"""
        productos = []
        
        for index, row in df.iterrows():
            try:
                producto = self.fila_a_producto(row, index)
                if producto:
                    productos.append(producto)
            except Exception as e:
                logger.warning(f"Error procesando fila {index}: {e}")
                continue
        
        return productos

    def convertir_dataframe_a_productos(self, df: pd.DataFrame) -> List[Producto]:
        """Convierte un DataFrame directamente a productos (para Vercel)"""
        try:
            # Verificar que el DataFrame tenga datos
            if df.empty:
                logger.warning("DataFrame vacío recibido")
                return []
            
            # Verificar si la primera fila es un header (no datos)
            primera_fila = df.iloc[0]
            primera_fila_es_header = any(
                str(val).lower() in ['marca', 'rubro', 'modelo', 'descripcion', 'precio', 'pvp', 'lista']
                for val in primera_fila if pd.notna(val)
            )
            
            if primera_fila_es_header:
                logger.info("Detectado header en primera fila, saltando...")
                # Usar la segunda fila como headers y saltar la primera
                df = df.iloc[1:].reset_index(drop=True)
                # Renombrar columnas usando la primera fila de datos
                if len(df) > 0:
                    df.columns = df.iloc[0]
                    df = df.iloc[1:].reset_index(drop=True)
            
            logger.info(f"DataFrame después de limpiar headers: {len(df)} filas, {len(df.columns)} columnas")
            logger.info(f"Columnas finales: {list(df.columns)}")
            
            # Verificar que tengamos las columnas mínimas requeridas
            columnas_disponibles = [str(col).lower().strip() for col in df.columns]
            logger.info(f"Columnas disponibles: {columnas_disponibles}")
            
            # Verificar columnas requeridas
            columnas_requeridas = ['modelo', 'descripcion', 'precio lista', 'pvp on line']
            columnas_faltantes = []
            
            for col_req in columnas_requeridas:
                if col_req not in columnas_disponibles:
                    columnas_faltantes.append(col_req)
            
            if columnas_faltantes:
                logger.error(f"Columnas requeridas faltantes: {columnas_faltantes}")
                logger.error(f"Columnas disponibles: {columnas_disponibles}")
                return []  # Retornar lista vacía si faltan columnas requeridas
            
            # Normalizar columnas
            df_normalizado = self.normalizar_columnas(df)
            logger.info(f"Columnas después de normalizar: {list(df_normalizado.columns)}")
            
            # Verificar qué columnas se mapearon
            columnas_mapeadas = {}
            for col_original in df.columns:
                if col_original in df_normalizado.columns:
                    columnas_mapeadas[col_original] = col_original
                else:
                    # Buscar a qué se mapeó
                    for col_nueva in df_normalizado.columns:
                        if col_original in df_normalizado.columns:
                            columnas_mapeadas[col_original] = col_nueva
                            break
            
            logger.info(f"Columnas mapeadas: {columnas_mapeadas}")
            
            df = df_normalizado
            
            # Convertir a productos
            productos = self.convertir_a_productos(df)
            
            logger.info(f"Convertidos {len(productos)} productos del DataFrame")
            
            # Si no se procesaron productos, dar información detallada
            if len(productos) == 0:
                logger.error(f"No se procesaron productos. Columnas disponibles: {list(df.columns)}")
                
                # Verificar qué columnas se mapearon
                columnas_requeridas = ['codigo', 'nombre', 'precio_base', 'precio_final']
                columnas_faltantes = []
                
                for col_req in columnas_requeridas:
                    if col_req not in df.columns:
                        columnas_faltantes.append(col_req)
                
                if columnas_faltantes:
                    logger.error(f"Columnas faltantes después de normalizar: {columnas_faltantes}")
            
            return productos
            
        except Exception as e:
            logger.error(f"Error convirtiendo DataFrame a productos: {e}")
            return []

    def fila_a_producto(self, row: pd.Series, index: int) -> Optional[Producto]:
        """Convierte una fila del DataFrame a un objeto Producto"""
        try:
            logger.info(f"Procesando fila {index}: {dict(row)}")
            
            # Extraer código
            codigo = self.extraer_codigo(row)
            logger.info(f"  Código extraído: {codigo}")
            
            # Extraer nombre
            nombre = self.extraer_nombre(row)
            logger.info(f"  Nombre extraído: {nombre}")
            
            # Extraer capacidad
            capacidad = self.extraer_capacidad(row)
            logger.info(f"  Capacidad extraída: {capacidad}")
            
            # Determinar marca
            marca = self.determinar_marca(row, codigo)
            logger.info(f"  Marca determinada: {marca}")
            
            # Determinar canal (usar categoría si está disponible)
            canal = self.determinar_canal(row)
            logger.info(f"  Canal determinado: {canal}")
            
            # Extraer precios
            precio_base = self.extraer_precio_base(row)
            precio_final = self.extraer_precio_final(row)
            logger.info(f"  Precios extraídos: base={precio_base}, final={precio_final}")
            
            # Verificar que tengamos al menos código o nombre
            if codigo == "SIN_CODIGO" and nombre == "Producto sin nombre":
                logger.warning(f"Fila {index} sin código ni nombre válido, saltando...")
                return None
            
            # Crear producto
            producto = Producto(
                codigo=codigo,
                nombre=nombre,
                capacidad=capacidad,
                marca=marca,
                canal=canal,
                precio_base=precio_base,
                precio_final=precio_final,
                margen=0.0  # Se calculará después
            )
            
            logger.info(f"  Producto creado exitosamente: {producto.codigo} - {producto.nombre}")
            return producto
            
        except Exception as e:
            logger.warning(f"Error procesando fila {index}: {e}")
            return None

    def extraer_codigo(self, row: pd.Series) -> str:
        """Extrae y normaliza el código del producto"""
        if 'codigo' in row and pd.notna(row['codigo']):
            return str(row['codigo']).strip().upper()
        
        # Intentar extraer código del nombre si no hay columna específica
        if 'nombre' in row and pd.notna(row['nombre']):
            nombre = str(row['nombre'])
            # Buscar patrones de código (ej: MO123, ZX100, etc.)
            match = re.search(r'([A-Z]{2}\d+)', nombre.upper())
            if match:
                return match.group(1)
        
        return "SIN_CODIGO"

    def extraer_nombre(self, row: pd.Series) -> str:
        """Extrae el nombre del producto"""
        if 'nombre' in row and pd.notna(row['nombre']):
            return str(row['nombre']).strip()
        return "Producto sin nombre"

    def extraer_capacidad(self, row: pd.Series) -> Optional[str]:
        """Extrae la capacidad del producto"""
        if 'capacidad' in row and pd.notna(row['capacidad']):
            return str(row['capacidad']).strip()
        
        # Intentar extraer capacidad del nombre
        if 'nombre' in row and pd.notna(row['nombre']):
            nombre = str(row['nombre'])
            # Buscar patrones de capacidad (ej: 60 Ah, 70Ah, etc.)
            match = re.search(r'(\d+)\s*[Aa][Hh]', nombre)
            if match:
                return f"{match.group(1)} Ah"
        
        return None

    def determinar_marca(self, row: pd.Series, codigo: str) -> Marca:
        """Determina la marca del producto"""
        # Primero intentar desde la columna marca
        if 'marca' in row and pd.notna(row['marca']):
            marca_str = str(row['marca']).lower().strip()
            for clave, marca in self.mapeo_marcas.items():
                if clave in marca_str:
                    return marca
        
        # Determinar por código
        codigo_upper = codigo.upper()
        if codigo_upper.startswith('MO'):
            return Marca.MOURA
        elif codigo_upper.startswith('ZX'):
            return Marca.SOLAR
        elif codigo_upper.startswith('LB'):
            return Marca.LUBECK
        elif codigo_upper.startswith('AC'):
            return Marca.ACUBAT
        
        # Determinar por nombre
        if 'nombre' in row and pd.notna(row['nombre']):
            nombre = str(row['nombre']).lower()
            for clave, marca in self.mapeo_marcas.items():
                if clave in nombre:
                    return marca
        
        # Por defecto, Moura
        return Marca.MOURA

    def determinar_canal(self, row: pd.Series) -> Canal:
        """Determina el canal del producto"""
        # Buscar en columna canal
        if 'canal' in row and pd.notna(row['canal']):
            canal_str = str(row['canal']).lower().strip()
            for clave, canal in self.mapeo_canales.items():
                if clave in canal_str:
                    return canal
        
        # Buscar en columna categoria
        if 'categoria' in row and pd.notna(row['categoria']):
            categoria_str = str(row['categoria']).lower().strip()
            for clave, canal in self.mapeo_canales.items():
                if clave in categoria_str:
                    return canal
        
        # Por defecto, minorista
        return Canal.MINORISTA

    def extraer_precio_base(self, row: pd.Series) -> float:
        """Extrae el precio base del producto"""
        if 'precio_base' in row and pd.notna(row['precio_base']):
            precio_str = str(row['precio_base'])
            
            # Manejar casos especiales como "LIBERADO"
            if 'liberado' in precio_str.lower():
                return 0.0
            
            # Limpiar y convertir precio
            precio_limpio = re.sub(r'[^\d.,]', '', precio_str)
            if precio_limpio:
                try:
                    # Manejar diferentes separadores decimales
                    precio_limpio = precio_limpio.replace(',', '.')
                    return float(precio_limpio)
                except ValueError:
                    pass
        
        # Si no hay precio base, usar precio final como base
        if 'precio_final' in row and pd.notna(row['precio_final']):
            return self.extraer_precio_final(row)
        
        return 0.0

    def extraer_precio_final(self, row: pd.Series) -> float:
        """Extrae el precio final del producto"""
        if 'precio_final' in row and pd.notna(row['precio_final']):
            precio_str = str(row['precio_final'])
            
            # Manejar casos especiales como "LIBERADO"
            if 'liberado' in precio_str.lower():
                return 0.0
            
            # Limpiar y convertir precio
            precio_limpio = re.sub(r'[^\d.,]', '', precio_str)
            if precio_limpio:
                try:
                    # Manejar diferentes separadores decimales
                    precio_limpio = precio_limpio.replace(',', '.')
                    return float(precio_limpio)
                except ValueError:
                    pass
        
        # Si no hay precio final, usar precio base
        if 'precio_base' in row and pd.notna(row['precio_base']):
            return self.extraer_precio_base(row)
        
        return 0.0

    def crear_archivo_ejemplo(self, ruta_archivo: str = "data/ejemplo_productos.xlsx"):
        """Crea un archivo Excel de ejemplo para testing"""
        datos_ejemplo = {
            'codigo': ['MO123', 'MO456', 'MO769', 'ZX100', 'LB200', 'LB300'],
            'nombre': ['Bateria 60 Ah', 'Bateria 70 Ah', 'Bateria 80 Ah', 'Bateria solar', 'Bateria Acubat', 'Bateria Lubeck'],
            'capacidad': ['60 Ah', '70 Ah', '80 Ah', '100 Ah', '120 Ah', '150 Ah'],
            'marca': ['moura', 'moura', 'moura', 'solar', 'acubat', 'lubeck'],
            'canal': ['minorista', 'mayorista', 'distribuidor', 'minorista', 'minorista', 'minorista'],
            'precio_base': [74.07, 96.00, 103.70, 111.11, 118.52, 133.33],
            'precio_final': [100.00, 120.00, 140.00, 150.00, 160.00, 180.00]
        }
        
        df = pd.DataFrame(datos_ejemplo)
        df.to_excel(ruta_archivo, index=False)
        logger.info(f"Archivo de ejemplo creado: {ruta_archivo}")
        
        return ruta_archivo 