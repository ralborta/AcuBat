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
    Analiza específicamente la hoja Moura del archivo de rentabilidades
    """
    try:
        logger.info(f"🔍 Analizando rentabilidades específicas de Moura: {file_path}")
        
        # Verificar si la hoja Moura existe
        try:
            xl = pd.ExcelFile(file_path)
            if "Moura" not in xl.sheet_names:
                logger.error(f"❌ No se encontró la hoja 'Moura' en el archivo. Hojas disponibles: {xl.sheet_names}")
                return {
                    'reglas_minorista': [],
                    'reglas_mayorista': [],
                    'resumen': f"Error: No se encontró la hoja 'Moura'. Hojas disponibles: {xl.sheet_names}"
                }
            df_moura = xl.parse("Moura")
        except Exception as e:
            logger.error(f"❌ Error leyendo la hoja 'Moura': {e}")
            return {
                'reglas_minorista': [],
                'reglas_mayorista': [],
                'resumen': f"Error leyendo hoja 'Moura': {str(e)}"
            }
        logger.info(f"✅ Hoja Moura cargada: {df_moura.shape}")
        
        reglas_minorista = []
        reglas_mayorista = []
        
        # Buscar dinámicamente las columnas MARK-UP y RENT
        col_markup_minorista = None
        col_rent_minorista = None
        col_markup_mayorista = None
        col_rent_mayorista = None
        
        # Buscar en la fila de headers (línea 2, fila 1)
        fila_headers = 1  # Línea 2
        
        logger.info(f"🔍 Buscando columnas MARK-UP y RENT dinámicamente en fila {fila_headers + 1}:")
        
        # Buscar columnas por contenido
        for j in range(len(df_moura.columns)):
            try:
                valor = str(df_moura.iloc[fila_headers, j]).strip().upper()
                logger.info(f"  Columna {j}: '{valor}'")
                
                # Buscar MARK-UP (Minorista)
                if 'MARK' in valor and 'UP' in valor and col_markup_minorista is None:
                    col_markup_minorista = j
                    logger.info(f"    ✅ MARK-UP Minorista encontrado en columna {j}")
                
                # Buscar RENT (Minorista)
                elif 'RENT' in valor and col_rent_minorista is None and col_markup_minorista is not None:
                    col_rent_minorista = j
                    logger.info(f"    ✅ RENT Minorista encontrado en columna {j}")
                
                # Buscar segundo MARK-UP (Mayorista)
                elif 'MARK' in valor and 'UP' in valor and col_markup_minorista is not None and col_markup_mayorista is None:
                    col_markup_mayorista = j
                    logger.info(f"    ✅ MARK-UP Mayorista encontrado en columna {j}")
                
                # Buscar RENTABILIDAD (Mayorista)
                elif 'RENTABILIDAD' in valor and col_rent_mayorista is None:
                    col_rent_mayorista = j
                    logger.info(f"    ✅ RENTABILIDAD Mayorista encontrado en columna {j}")
                    
            except Exception as e:
                logger.warning(f"    ⚠️ Error procesando columna {j}: {e}")
                continue
        
        # Si no se encontraron, usar las posiciones originales como fallback
        if col_markup_minorista is None and 16 < len(df_moura.columns):
            col_markup_minorista = 16
            logger.info(f"    ⚠️ Usando posición fallback para MARK-UP Minorista: {col_markup_minorista}")
        
        if col_rent_minorista is None and 17 < len(df_moura.columns):
            col_rent_minorista = 17
            logger.info(f"    ⚠️ Usando posición fallback para RENT Minorista: {col_rent_minorista}")
        
        if col_markup_mayorista is None and 25 < len(df_moura.columns):
            col_markup_mayorista = 25
            logger.info(f"    ⚠️ Usando posición fallback para MARK-UP Mayorista: {col_markup_mayorista}")
        
        if col_rent_mayorista is None and 26 < len(df_moura.columns):
            col_rent_mayorista = 26
            logger.info(f"    ⚠️ Usando posición fallback para RENTABILIDAD Mayorista: {col_rent_mayorista}")
        
        logger.info(f"📊 Columnas finales detectadas:")
        logger.info(f"  MARK-UP Minorista: {col_markup_minorista} - Valor: {df_moura.iloc[fila_headers, col_markup_minorista] if col_markup_minorista is not None else 'NO ENCONTRADO'}")
        logger.info(f"  RENT Minorista: {col_rent_minorista} - Valor: {df_moura.iloc[fila_headers, col_rent_minorista] if col_rent_minorista is not None else 'NO ENCONTRADO'}")
        logger.info(f"  MARK-UP Mayorista: {col_markup_mayorista} - Valor: {df_moura.iloc[fila_headers, col_markup_mayorista] if col_markup_mayorista is not None else 'NO ENCONTRADO'}")
        logger.info(f"  RENTABILIDAD Mayorista: {col_rent_mayorista} - Valor: {df_moura.iloc[fila_headers, col_rent_mayorista] if col_rent_mayorista is not None else 'NO ENCONTRADO'}")
        
        # Procesar productos desde la línea 3 (fila 2) en adelante
        for i in range(fila_headers + 1, len(df_moura)):
            try:
                codigo = str(df_moura.iloc[i, 0]).strip()
                if not codigo or codigo == 'nan':
                    continue
                precio_base = _convertir_precio(df_moura.iloc[i, 1])
                if not precio_base:
                    continue
                # Extraer datos Minorista
                if col_markup_minorista < len(df_moura.columns) and col_rent_minorista < len(df_moura.columns):
                    markup_minorista = _convertir_porcentaje(df_moura.iloc[i, col_markup_minorista])
                    rent_minorista = _convertir_porcentaje(df_moura.iloc[i, col_rent_minorista])
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
                        logger.info(f"✅ Regla Minorista: {codigo} - Markup: {markup_minorista}%")
                # Extraer datos Mayorista
                if col_markup_mayorista < len(df_moura.columns) and col_rent_mayorista < len(df_moura.columns):
                    markup_mayorista = _convertir_porcentaje(df_moura.iloc[i, col_markup_mayorista])
                    rent_mayorista = _convertir_porcentaje(df_moura.iloc[i, col_rent_mayorista])
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
                        logger.info(f"✅ Regla Mayorista: {codigo} - Markup: {markup_mayorista}%")
            except Exception as e:
                logger.warning(f"⚠️ Error procesando fila {i}: {e}")
                continue
        resumen = {
            'total_reglas': len(reglas_minorista) + len(reglas_mayorista),
            'reglas_minorista': len(reglas_minorista),
            'reglas_mayorista': len(reglas_mayorista),
            'hoja': 'Moura',
            'estado': '✅ Procesado correctamente' if (reglas_minorista or reglas_mayorista) else '❌ Sin reglas encontradas'
        }
        logger.info(f"🎉 Análisis completado: {resumen['total_reglas']} reglas encontradas")
        return {
            'reglas_minorista': reglas_minorista,
            'reglas_mayorista': reglas_mayorista,
            'resumen': resumen
        }
    except Exception as e:
        logger.error(f"❌ Error analizando rentabilidades Moura: {e}")
        return {
            'reglas_minorista': [],
            'reglas_mayorista': [],
            'resumen': f'Error: {str(e)}'
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