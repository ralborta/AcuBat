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
            'lb': Marca.LUBECK  # LB parece ser marca Lubeck
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
        # Mapeo de nombres de columnas comunes
        mapeo_columnas = {
            'codigo': ['código', 'code', 'id', 'producto_id'],
            'nombre': ['descripción', 'descripcion', 'producto', 'name', 'desc'],
            'capacidad': ['ah', 'amperaje', 'capacidad_ah'],
            'marca': ['brand', 'fabricante'],
            'canal': ['tipo', 'tipo_canal', 'categoria'],
            'precio_base': ['precio', 'precio_base', 'costo', 'precio_costo'],
            'precio_final': ['precio_final', 'precio_venta', 'precio_publico']
        }
        
        # Normalizar nombres de columnas
        columnas_normalizadas = {}
        for columna_objetivo, posibles_nombres in mapeo_columnas.items():
            for nombre_posible in posibles_nombres:
                if nombre_posible in df.columns:
                    columnas_normalizadas[nombre_posible] = columna_objetivo
                    break
        
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

    def fila_a_producto(self, row: pd.Series, index: int) -> Optional[Producto]:
        """Convierte una fila del DataFrame a un objeto Producto"""
        try:
            # Extraer código
            codigo = self.extraer_codigo(row)
            
            # Extraer nombre
            nombre = self.extraer_nombre(row)
            
            # Extraer capacidad
            capacidad = self.extraer_capacidad(row)
            
            # Determinar marca
            marca = self.determinar_marca(row, codigo)
            
            # Determinar canal
            canal = self.determinar_canal(row)
            
            # Extraer precios
            precio_base = self.extraer_precio_base(row)
            precio_final = self.extraer_precio_final(row)
            
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
        if 'canal' in row and pd.notna(row['canal']):
            canal_str = str(row['canal']).lower().strip()
            for clave, canal in self.mapeo_canales.items():
                if clave in canal_str:
                    return canal
        
        # Por defecto, minorista
        return Canal.MINORISTA

    def extraer_precio_base(self, row: pd.Series) -> float:
        """Extrae el precio base del producto"""
        if 'precio_base' in row and pd.notna(row['precio_base']):
            return float(row['precio_base'])
        
        # Si no hay precio base, usar precio final como base
        if 'precio_final' in row and pd.notna(row['precio_final']):
            return float(row['precio_final'])
        
        return 0.0

    def extraer_precio_final(self, row: pd.Series) -> float:
        """Extrae el precio final del producto"""
        if 'precio_final' in row and pd.notna(row['precio_final']):
            return float(row['precio_final'])
        
        # Si no hay precio final, usar precio base
        if 'precio_base' in row and pd.notna(row['precio_base']):
            return float(row['precio_base'])
        
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