#!/usr/bin/env python3
"""
Parser específico para la hoja Moura del archivo de rentabilidades
Basado en el diagnóstico que muestra columnas MARK-UP y RENT en las posiciones 16, 17, 25, 26
"""

import pandas as pd
import logging
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)

def analizar_rentabilidades_moura(file_path: str) -> Dict:
    """
    Analiza reglas de rentabilidad SOLO de la hoja Moura
    """
    try:
        logger.info(f"🔍 Analizando rentabilidades SOLO de Moura: {file_path}")

        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            logger.error(f"❌ Archivo no encontrado: {file_path}")
            return {
                'reglas_minorista': [],
                'reglas_mayorista': [],
                'resumen': {
                    'archivo': file_path,
                    'hojas_procesadas': [],
                    'total_reglas': 0,
                    'error': 'Archivo no encontrado'
                }
            }

        # Leer el archivo Excel
        xl = pd.ExcelFile(file_path)
        hojas_disponibles = xl.sheet_names
        logger.info(f"📊 Hojas disponibles: {hojas_disponibles}")

        reglas_minorista = []
        reglas_mayorista = []

        # Procesar SOLO hoja Moura
        if "Moura" in hojas_disponibles:
            logger.info("🔍 Procesando SOLO hoja Moura...")
            df_moura = xl.parse("Moura")
            reglas_moura = _procesar_hoja_moura(df_moura)
            reglas_minorista.extend(reglas_moura['minorista'])
            reglas_mayorista.extend(reglas_moura['mayorista'])
            logger.info(f"✅ Hoja Moura: {len(reglas_moura['minorista'])} reglas minorista, {len(reglas_moura['mayorista'])} reglas mayorista")
        else:
            logger.error("❌ Hoja 'Moura' no encontrada")
            return {
                'reglas_minorista': [],
                'reglas_mayorista': [],
                'resumen': {
                    'archivo': file_path,
                    'hojas_procesadas': [],
                    'total_reglas': 0,
                    'error': 'Hoja Moura no encontrada'
                }
            }

        # Generar resumen
        total_reglas = len(reglas_minorista) + len(reglas_mayorista)
        logger.info(f"✅ Total de reglas extraídas: {total_reglas}")

        return {
            'reglas_minorista': reglas_minorista,
            'reglas_mayorista': reglas_mayorista,
            'resumen': {
                'archivo': file_path,
                'hojas_procesadas': ['Moura'],
                'total_reglas': total_reglas,
                'reglas_minorista': len(reglas_minorista),
                'reglas_mayorista': len(reglas_mayorista)
            }
        }

    except Exception as e:
        logger.error(f"❌ Error analizando rentabilidades: {e}")
        return {
            'reglas_minorista': [],
            'reglas_mayorista': [],
            'resumen': {
                'archivo': file_path,
                'hojas_procesadas': [],
                'total_reglas': 0,
                'error': str(e)
            }
        }

def _procesar_hoja_varta(df_varta) -> Dict:
    """Procesa específicamente la hoja Varta"""
    reglas_minorista = []
    reglas_mayorista = []
    
    # Buscar columnas específicas de Varta (corregidas según imagen)
    col_markup_mayorista = 15  # Columna P - Mak-up Mayorista
    col_rent_mayorista = 16    # Columna Q - rentabili Mayorista
    col_markup_minorista = 23  # Columna X - Mark-UP Minorista
    col_rent_minorista = 24    # Columna Y - Rentabilidad Minorista
    
    # Procesar productos desde la línea 4 en adelante
    for i in range(3, len(df_varta)):
        try:
            codigo = str(df_varta.iloc[i, 0]).strip()
            if not codigo or codigo == 'nan':
                continue
            
            precio_base = _convertir_precio(df_varta.iloc[i, 1])
            if not precio_base:
                continue
            
            # Extraer datos Mayorista (Columna P)
            if col_markup_mayorista < len(df_varta.columns):
                markup_mayorista = _convertir_porcentaje(df_varta.iloc[i, col_markup_mayorista])
                rent_mayorista = _convertir_porcentaje(df_varta.iloc[i, col_rent_mayorista]) if col_rent_mayorista < len(df_varta.columns) else 0
                if markup_mayorista > 0:
                    regla_mayorista = {
                        'codigo': codigo,
                        'canal': 'Mayorista',
                        'precio_base': precio_base,
                        'markup': markup_mayorista,
                        'rentabilidad': rent_mayorista,
                        'fila': i,
                        'hoja': 'Varta'
                    }
                    reglas_mayorista.append(regla_mayorista)
            
            # Extraer datos Minorista (Columna X)
            if col_markup_minorista < len(df_varta.columns):
                markup_minorista = _convertir_porcentaje(df_varta.iloc[i, col_markup_minorista])
                rent_minorista = _convertir_porcentaje(df_varta.iloc[i, col_rent_minorista]) if col_rent_minorista < len(df_varta.columns) else 0
                if markup_minorista > 0:
                    regla_minorista = {
                        'codigo': codigo,
                        'canal': 'Minorista',
                        'precio_base': precio_base,
                        'markup': markup_minorista,
                        'rentabilidad': rent_minorista,
                        'fila': i,
                        'hoja': 'Varta'
                    }
                    reglas_minorista.append(regla_minorista)
                    
        except Exception as e:
            logger.warning(f"⚠️ Error procesando fila {i} en Varta: {e}")
            continue
    
    return {
        'minorista': reglas_minorista,
        'mayorista': reglas_mayorista
    }

def _procesar_hoja_moura(df_moura) -> Dict:
    """Procesa específicamente la hoja Moura con la estructura completa"""
    reglas_minorista = []
    reglas_mayorista = []
    
    # Estructura completa del archivo:
    # Columna 0: Código
    # Columna 1: P. Base
    # Columna 16: Markup Mayorista (decimal, ej: 0.1934 = 19.34%)
    # Columna 17: Rentabilidad Mayorista (decimal, ej: 0.0805 = 8.05%)
    # Columna 25: Markup Minorista (decimal, ej: 0.5998 = 59.98%)
    # Columna 26: Rentabilidad Minorista (decimal, ej: 0.3749 = 37.49%)
    
    # Procesar todos los productos (empezar desde fila 2 para saltar headers)
    for i in range(2, len(df_moura)):
        try:
            codigo = str(df_moura.iloc[i, 0]).strip()  # Columna 'Código'
            if not codigo or codigo == 'nan' or not codigo.startswith('M'):
                continue
            
            precio_base = df_moura.iloc[i, 1]  # Columna 'P. Base'
            if pd.isna(precio_base) or precio_base <= 0:
                continue
            
            # Datos Mayorista (columnas 16 y 17)
            markup_mayorista_raw = df_moura.iloc[i, 16]  # Columna 16 - Markup Mayorista
            rentabilidad_mayorista_raw = df_moura.iloc[i, 17]  # Columna 17 - Rentabilidad Mayorista
            
            # Datos Minorista (columnas 25 y 26)
            markup_minorista_raw = df_moura.iloc[i, 25]  # Columna 25 - Markup Minorista
            rentabilidad_minorista_raw = df_moura.iloc[i, 26]  # Columna 26 - Rentabilidad Minorista
            
            # Convertir de decimal a porcentaje
            markup_mayorista = float(markup_mayorista_raw) * 100 if pd.notna(markup_mayorista_raw) else 0.0
            rentabilidad_mayorista = float(rentabilidad_mayorista_raw) * 100 if pd.notna(rentabilidad_mayorista_raw) else 0.0
            markup_minorista = float(markup_minorista_raw) * 100 if pd.notna(markup_minorista_raw) else 0.0
            rentabilidad_minorista = float(rentabilidad_minorista_raw) * 100 if pd.notna(rentabilidad_minorista_raw) else 0.0
            
            # Crear regla Minorista
            regla_minorista = {
                'codigo': codigo,
                'canal': 'Minorista',
                'precio_base': float(precio_base),
                'markup': markup_minorista,
                'rentabilidad': rentabilidad_minorista,
                'fila': i,
                'hoja': 'Moura'
            }
            reglas_minorista.append(regla_minorista)
            
            # Crear regla Mayorista
            regla_mayorista = {
                'codigo': codigo,
                'canal': 'Mayorista',
                'precio_base': float(precio_base),
                'markup': markup_mayorista,
                'rentabilidad': rentabilidad_mayorista,
                'fila': i,
                'hoja': 'Moura'
            }
            reglas_mayorista.append(regla_mayorista)
                    
        except Exception as e:
            logger.warning(f"⚠️ Error procesando fila {i} en Moura: {e}")
            continue
    
    return {
        'minorista': reglas_minorista,
        'mayorista': reglas_mayorista
    }

def _convertir_precio(valor) -> Optional[float]:
    """Convierte un valor a precio float"""
    try:
        if pd.isna(valor) or valor == '':
            return None
        
        valor_str = str(valor).strip()
        if not valor_str or valor_str == 'nan':
            return None
        
        # Remover símbolos de moneda y espacios
        valor_str = valor_str.replace('$', '').replace(',', '').replace(' ', '')
        
        return float(valor_str)
        
    except Exception as e:
        logger.warning(f"Error convirtiendo precio '{valor}': {e}")
        return None

def _convertir_porcentaje(valor) -> float:
    """Convierte un valor a porcentaje float"""
    try:
        if pd.isna(valor) or valor == '':
            return 0.0
        
        valor_str = str(valor).strip()
        if not valor_str or valor_str == 'nan':
            return 0.0
        
        # Filtrar errores de Excel
        if valor_str in ['#DIV/0!', '#N/A', '#VALUE!', '#REF!', '#NAME?', '#NUM!']:
            return 0.0
        
        # Remover símbolo de porcentaje si existe
        valor_str = valor_str.replace('%', '').replace(',', '.').strip()
        
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