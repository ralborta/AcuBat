#!/usr/bin/env python3
"""
Parser específico para archivos MOURA con estructura compleja
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class MouraParser:
    """Parser especializado para archivos MOURA con cálculos complejos"""
    
    def __init__(self):
        self.marca = "Moura"
        self.canal = "Minorista"  # Por defecto, se puede ajustar
        
    def parse_moura_file(self, file_path: str) -> List[Dict]:
        """
        Parsea archivo MOURA con estructura compleja
        
        Estructura esperada:
        - Columna A: Códigos de producto (M0FD, M18FD, etc.)
        - Columna B: Precios iniciales
        - Columna V: Precios sugeridos
        - Columna W: Precios redondeados
        - Columna AA: Precios finales de venta
        - Columna Z: Rentabilidad calculada
        """
        try:
            # Leer todas las hojas del archivo
            excel_file = pd.ExcelFile(file_path)
            logger.info(f"Archivo MOURA detectado con {len(excel_file.sheet_names)} hojas")
            
            productos = []
            
            for sheet_name in excel_file.sheet_names:
                logger.info(f"Procesando hoja: {sheet_name}")
                
                # Leer la hoja
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                
                # Buscar la fila donde empiezan los productos (códigos M...)
                productos_hoja = self._extract_products_from_sheet(df, sheet_name)
                productos.extend(productos_hoja)
            
            logger.info(f"Total de productos MOURA extraídos: {len(productos)}")
            return productos
            
        except Exception as e:
            logger.error(f"Error al parsear archivo MOURA: {str(e)}")
            raise
    
    def _extract_products_from_sheet(self, df: pd.DataFrame, sheet_name: str) -> List[Dict]:
        """Extrae productos de una hoja específica"""
        productos = []
        
        # Buscar filas que contengan códigos de producto MOURA (M...)
        for idx, row in df.iterrows():
            # Verificar si la primera columna contiene un código de producto
            if pd.notna(row.iloc[0]) and isinstance(row.iloc[0], str):
                codigo = str(row.iloc[0]).strip()
                
                # Verificar si es un código MOURA (empieza con M)
                if re.match(r'^M[A-Z0-9]+$', codigo):
                    producto = self._extract_product_data(row, df, idx, sheet_name)
                    if producto:
                        productos.append(producto)
        
        return productos
    
    def _extract_product_data(self, row: pd.Series, df: pd.DataFrame, row_idx: int, sheet_name: str) -> Optional[Dict]:
        """Extrae datos de un producto específico"""
        try:
            codigo = str(row.iloc[0]).strip()
            
            # Extraer precios de diferentes columnas
            precio_base = self._extract_price(row.iloc[1])  # Columna B
            precio_sugerido = self._extract_price(row.iloc[21])  # Columna V
            precio_redondeado = self._extract_price(row.iloc[22])  # Columna W
            precio_final = self._extract_price(row.iloc[26])  # Columna AA
            rentabilidad = self._extract_percentage(row.iloc[25])  # Columna Z
            
            # Si no hay precio base, intentar con precio sugerido
            if not precio_base and precio_sugerido:
                precio_base = precio_sugerido * 0.7  # Estimación
            
            # Si no hay precio final, usar precio redondeado
            if not precio_final and precio_redondeado:
                precio_final = precio_redondeado
            
            # Calcular margen si no está disponible
            margen = rentabilidad if rentabilidad else self._calculate_margin(precio_base, precio_final)
            
            # Determinar estado basado en rentabilidad
            estado = self._determine_status(margen)
            
            producto = {
                'codigo': codigo,
                'descripcion': f"Producto {codigo} - {sheet_name}",
                'marca': self.marca,
                'canal': self.canal,
                'precio_base': precio_base,
                'precio_final': precio_final,
                'margen': margen,
                'estado': estado,
                'estado_rentabilidad': 'Sin ref.',  # Se validará después
                'margen_minimo_esperado': None,
                'margen_optimo_esperado': None,
                'sugerencias_openai': None,
                'hoja_origen': sheet_name
            }
            
            logger.info(f"Producto MOURA extraído: {codigo} - Precio: ${precio_final:,.0f} - Margen: {margen:.1f}%")
            return producto
            
        except Exception as e:
            logger.error(f"Error al extraer producto {codigo}: {str(e)}")
            return None
    
    def _extract_price(self, value) -> Optional[float]:
        """Extrae precio de una celda"""
        if pd.isna(value):
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Limpiar símbolos de moneda y espacios
            cleaned = re.sub(r'[^\d.,]', '', value)
            if cleaned:
                # Convertir coma decimal a punto
                cleaned = cleaned.replace(',', '.')
                try:
                    return float(cleaned)
                except:
                    return None
        
        return None
    
    def _extract_percentage(self, value) -> Optional[float]:
        """Extrae porcentaje de una celda"""
        if pd.isna(value):
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Limpiar símbolo de porcentaje
            cleaned = re.sub(r'[^\d.,]', '', value)
            if cleaned:
                cleaned = cleaned.replace(',', '.')
                try:
                    return float(cleaned)
                except:
                    return None
        
        return None
    
    def _calculate_margin(self, precio_base: float, precio_final: float) -> Optional[float]:
        """Calcula margen si no está disponible"""
        if not precio_base or not precio_final or precio_base <= 0:
            return None
        
        margen = ((precio_final - precio_base) / precio_base) * 100
        return round(margen, 2)
    
    def _determine_status(self, margen: float) -> str:
        """Determina estado basado en margen"""
        if not margen:
            return "Alerta"
        
        if margen >= 30:
            return "OK"
        elif margen >= 20:
            return "Revisar"
        else:
            return "Ajustar"

def parse_moura_file(file_path: str) -> List[Dict]:
    """Función principal para parsear archivos MOURA"""
    parser = MouraParser()
    return parser.parse_moura_file(file_path) 