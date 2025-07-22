#!/usr/bin/env python3
"""
Parser específico para la hoja Moura del archivo de rentabilidades
Basado en el diagnóstico que muestra columnas MARK-UP y RENT en las posiciones 16, 17, 25, 26
"""

import pandas as pd
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def analizar_rentabilidades_moura(file_path: str) -> Dict:
    """
    Analiza reglas de rentabilidad de múltiples hojas (Varta y Moura)
    """
    try:
        logger.info(f"🔍 Analizando rentabilidades de múltiples hojas: {file_path}")
        
        # Verificar hojas disponibles
        try:
            xl = pd.ExcelFile(file_path)
            hojas_disponibles = xl.sheet_names
            logger.info(f"📋 Hojas disponibles: {hojas_disponibles}")
        except Exception as e:
            logger.error(f"❌ Error leyendo archivo: {e}")
            return {
                'reglas_minorista': [],
                'reglas_mayorista': [],
                'resumen': f"Error leyendo archivo: {str(e)}"
            }
        
        reglas_minorista = []
        reglas_mayorista = []
        
        # Procesar hoja Varta
        if "Varta" in hojas_disponibles:
            logger.info("🔍 Procesando hoja Varta...")
            df_varta = xl.parse("Varta")
            reglas_varta = _procesar_hoja_varta(df_varta)
            reglas_minorista.extend(reglas_varta['minorista'])
            reglas_mayorista.extend(reglas_varta['mayorista'])
            logger.info(f"✅ Hoja Varta: {len(reglas_varta['minorista'])} reglas minorista, {len(reglas_varta['mayorista'])} reglas mayorista")
        
        # Procesar hoja Moura
        if "Moura" in hojas_disponibles:
            logger.info("🔍 Procesando hoja Moura...")
            df_moura = xl.parse("Moura")
            reglas_moura = _procesar_hoja_moura(df_moura)
            reglas_minorista.extend(reglas_moura['minorista'])
            reglas_mayorista.extend(reglas_moura['mayorista'])
            logger.info(f"✅ Hoja Moura: {len(reglas_moura['minorista'])} reglas minorista, {len(reglas_moura['mayorista'])} reglas mayorista")
        
        resumen = {
            'total_reglas': len(reglas_minorista) + len(reglas_mayorista),
            'reglas_minorista': len(reglas_minorista),
            'reglas_mayorista': len(reglas_mayorista),
            'hojas_procesadas': [h for h in ['Varta', 'Moura'] if h in hojas_disponibles],
            'estado': '✅ Procesado correctamente' if (reglas_minorista or reglas_mayorista) else '❌ Sin reglas encontradas'
        }
        
        logger.info(f"🎉 Análisis completado: {resumen['total_reglas']} reglas encontradas")
        return {
            'reglas_minorista': reglas_minorista,
            'reglas_mayorista': reglas_mayorista,
            'resumen': resumen
        }
        
    except Exception as e:
        logger.error(f"❌ Error analizando rentabilidades: {e}")
        return {
            'reglas_minorista': [],
            'reglas_mayorista': [],
            'resumen': f'Error: {str(e)}'
        }

def _procesar_hoja_varta(df_varta) -> Dict:
    """Procesa específicamente la hoja Varta"""
    reglas_minorista = []
    reglas_mayorista = []
    
    # Buscar columnas específicas de Varta
    col_markup_minorista = 24  # Columna Y
    col_rent_minorista = 25    # Columna Z
    col_markup_mayorista = 15  # Columna Q
    col_rent_mayorista = 16    # Columna R
    
    # Procesar productos desde la línea 4 en adelante
    for i in range(3, len(df_varta)):
        try:
            codigo = str(df_varta.iloc[i, 0]).strip()
            if not codigo or codigo == 'nan' or codigo == 'Modelo':
                continue
            
            precio_base = _convertir_precio(df_varta.iloc[i, 1])
            if not precio_base:
                continue
            
            # Extraer datos Minorista (Columna Y)
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
            
            # Extraer datos Mayorista (Columna Q)
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
                    
        except Exception as e:
            logger.warning(f"⚠️ Error procesando fila {i} en Varta: {e}")
            continue
    
    return {
        'minorista': reglas_minorista,
        'mayorista': reglas_mayorista
    }

def _procesar_hoja_moura(df_moura) -> Dict:
    """Procesa específicamente la hoja Moura"""
    reglas_minorista = []
    reglas_mayorista = []
    
    # Buscar columnas específicas de Moura
    col_markup_minorista = 16  # Columna Q
    col_rent_minorista = 17    # Columna R
    col_markup_mayorista = 25  # Columna Y
    col_rent_mayorista = 26    # Columna Z
    
    # Procesar productos desde la línea 3 en adelante
    for i in range(2, len(df_moura)):
        try:
            codigo = str(df_moura.iloc[i, 0]).strip()
            if not codigo or codigo == 'nan':
                continue
            
            precio_base = _convertir_precio(df_moura.iloc[i, 1])
            if not precio_base:
                continue
            
            # Extraer datos Minorista
            if col_markup_minorista < len(df_moura.columns):
                markup_minorista = _convertir_porcentaje(df_moura.iloc[i, col_markup_minorista])
                rent_minorista = _convertir_porcentaje(df_moura.iloc[i, col_rent_minorista]) if col_rent_minorista < len(df_moura.columns) else 0
                if markup_minorista > 0:
                    regla_minorista = {
                        'codigo': codigo,
                        'canal': 'Minorista',
                        'precio_base': precio_base,
                        'markup': markup_minorista,
                        'rentabilidad': rent_minorista,
                        'fila': i,
                        'hoja': 'Moura'
                    }
                    reglas_minorista.append(regla_minorista)
            
            # Extraer datos Mayorista
            if col_markup_mayorista < len(df_moura.columns):
                markup_mayorista = _convertir_porcentaje(df_moura.iloc[i, col_markup_mayorista])
                rent_mayorista = _convertir_porcentaje(df_moura.iloc[i, col_rent_mayorista]) if col_rent_mayorista < len(df_moura.columns) else 0
                if markup_mayorista > 0:
                    regla_mayorista = {
                        'codigo': codigo,
                        'canal': 'Mayorista',
                        'precio_base': precio_base,
                        'markup': markup_mayorista,
                        'rentabilidad': rent_mayorista,
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