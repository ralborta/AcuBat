import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from app.db.models import NormalizedItem
from app.db.base import SessionLocal

logger = logging.getLogger(__name__)

class ExcelParser:
    """Servicio para parsear archivos Excel y normalizar datos"""
    
    def __init__(self):
        self.required_columns = ['sku', 'marca', 'linea', 'base_price', 'cost']
        self.column_mappings = {
            'codigo': 'sku',
            'producto': 'sku',
            'brand': 'marca',
            'marca_producto': 'marca',
            'linea_producto': 'linea',
            'line': 'linea',
            'precio_base': 'base_price',
            'precio_lista': 'base_price',
            'costo': 'cost',
            'precio_costo': 'cost',
            'cost': 'cost'
        }
    
    def parse_excel_file(self, file_path: str, tenant_id: str, list_id: str) -> List[NormalizedItem]:
        """
        Parsea un archivo Excel y normaliza los datos
        
        Args:
            file_path: Ruta del archivo Excel
            tenant_id: ID del tenant
            list_id: ID de la lista
            
        Returns:
            Lista de items normalizados
        """
        try:
            # Leer archivo Excel
            df = pd.read_excel(file_path, engine='openpyxl')
            logger.info(f"Archivo Excel leído: {len(df)} filas")
            
            # Normalizar columnas
            df = self._normalize_columns(df)
            
            # Validar columnas requeridas
            self._validate_required_columns(df)
            
            # Limpiar datos
            df = self._clean_data(df)
            
            # Convertir a objetos NormalizedItem
            items = self._convert_to_items(df, tenant_id, list_id)
            
            logger.info(f"Items normalizados: {len(items)}")
            return items
            
        except Exception as e:
            logger.error(f"Error parseando Excel: {e}")
            raise
    
    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza los nombres de las columnas"""
        # Convertir a minúsculas y reemplazar espacios
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Aplicar mapeos conocidos
        df = df.rename(columns=self.column_mappings)
        
        return df
    
    def _validate_required_columns(self, df: pd.DataFrame):
        """Valida que existan las columnas requeridas"""
        missing_columns = []
        for col in self.required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            raise ValueError(f"Columnas requeridas faltantes: {missing_columns}")
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y valida los datos"""
        # Eliminar filas vacías
        df = df.dropna(subset=['sku', 'base_price', 'cost'])
        
        # Convertir tipos de datos
        df['base_price'] = pd.to_numeric(df['base_price'], errors='coerce')
        df['cost'] = pd.to_numeric(df['cost'], errors='coerce')
        
        # Eliminar filas con valores inválidos
        df = df.dropna(subset=['base_price', 'cost'])
        
        # Validar que los precios sean positivos
        df = df[(df['base_price'] > 0) & (df['cost'] > 0)]
        
        # Limpiar strings
        df['sku'] = df['sku'].astype(str).str.strip()
        df['marca'] = df['marca'].astype(str).str.strip()
        df['linea'] = df['linea'].astype(str).str.strip()
        
        return df
    
    def _convert_to_items(self, df: pd.DataFrame, tenant_id: str, list_id: str) -> List[NormalizedItem]:
        """Convierte el DataFrame a objetos NormalizedItem"""
        items = []
        
        for _, row in df.iterrows():
            # Extraer atributos adicionales
            attrs = {}
            for col in df.columns:
                if col not in self.required_columns:
                    attrs[col] = row[col]
            
            item = NormalizedItem(
                list_id=list_id,
                sku=str(row['sku']),
                marca=str(row['marca']),
                linea=str(row['linea']),
                base_price=float(row['base_price']),
                cost=float(row['cost']),
                attrs=attrs
            )
            
            items.append(item)
        
        return items
    
    def save_items_to_db(self, items: List[NormalizedItem]):
        """Guarda los items en la base de datos"""
        db = SessionLocal()
        try:
            db.add_all(items)
            db.commit()
            logger.info(f"Items guardados en DB: {len(items)}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error guardando items: {e}")
            raise
        finally:
            db.close()

# Instancia global del parser
excel_parser = ExcelParser()
