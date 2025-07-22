#!/usr/bin/env python3
"""
Script para diagnosticar específicamente la hoja MOURA
en el archivo Rentalibilidades-2.xlsx
"""

import pandas as pd
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def diagnosticar_hoja_moura():
    """Diagnostica específicamente la hoja MOURA"""
    
    archivo = "Rentalibilidades-2.xlsx"
    
    try:
        # Leer solo la hoja MOURA
        logger.info(f"📁 Leyendo archivo: {archivo}")
        logger.info(f"🎯 Buscando específicamente la hoja MOURA")
        
        # Intentar leer la hoja Moura
        try:
            df_moura = pd.read_excel(archivo, sheet_name="Moura")
            logger.info(f"✅ Hoja Moura encontrada")
        except:
            logger.error(f"❌ No se pudo leer la hoja Moura")
            # Listar todas las hojas disponibles
            df_all = pd.read_excel(archivo, sheet_name=None)
            logger.info(f"📋 Hojas disponibles: {list(df_all.keys())}")
            return
        
        logger.info(f"📏 Dimensiones de la hoja Moura: {df_moura.shape}")
        
        # Mostrar las primeras 20 filas y todas las columnas
        logger.info(f"📊 Primeras 20 filas de Moura:")
        
        for i in range(min(20, len(df_moura))):
            fila_info = f"Fila {i}: "
            for j in range(len(df_moura.columns)):
                valor = str(df_moura.iloc[i, j]).strip()
                if valor and valor != 'nan':
                    fila_info += f"[{j}]:'{valor}' "
            if fila_info != f"Fila {i}: ":
                logger.info(fila_info)
        
        # Buscar específicamente las columnas P y Y en diferentes líneas
        logger.info(f"\n🎯 BUSCANDO COLUMNAS P y Y EN DIFERENTES LÍNEAS:")
        
        for linea in range(min(10, len(df_moura))):
            logger.info(f"\n🔍 Línea {linea + 1} (fila {linea}):")
            fila_actual = df_moura.iloc[linea]
            
            columna_p = None
            columna_y = None
            
            for j, valor in enumerate(fila_actual):
                valor_str = str(valor).strip().upper()
                if valor_str and valor_str != 'NAN':
                    logger.info(f"  Columna {j}: '{valor_str}'")
                    
                    # Buscar columna P (Minorista)
                    if valor_str == 'P' or 'P.' in valor_str or 'PUBLICO' in valor_str:
                        columna_p = j
                        logger.info(f"    ✅ POSIBLE COLUMNA P encontrada en posición {j}")
                    
                    # Buscar columna Y (Mayorista)
                    if valor_str == 'Y' or 'Y.' in valor_str or 'MAYORISTA' in valor_str:
                        columna_y = j
                        logger.info(f"    ✅ POSIBLE COLUMNA Y encontrada en posición {j}")
            
            if columna_p is not None or columna_y is not None:
                logger.info(f"🎯 RESULTADO Línea {linea + 1}:")
                if columna_p is not None:
                    logger.info(f"  ✅ COLUMNA P (Minorista): Posición {columna_p}")
                if columna_y is not None:
                    logger.info(f"  ✅ COLUMNA Y (Mayorista): Posición {columna_y}")
                
                # Mostrar datos de esas columnas desde la línea siguiente
                logger.info(f"📊 DATOS DE LAS COLUMNAS DETECTADAS:")
                for i in range(linea + 1, min(linea + 10, len(df_moura))):
                    fila_data = f"  Línea {i+1}: "
                    
                    if columna_p is not None:
                        valor_p = df_moura.iloc[i, columna_p]
                        fila_data += f"P[{columna_p}]='{valor_p}' "
                    
                    if columna_y is not None:
                        valor_y = df_moura.iloc[i, columna_y]
                        fila_data += f"Y[{columna_y}]='{valor_y}' "
                    
                    logger.info(fila_data)
                break
        
        # Si no se encontraron P y Y, buscar otros patrones
        if columna_p is None and columna_y is None:
            logger.info(f"\n🔍 NO SE ENCONTRARON P y Y, buscando otros patrones:")
            
            for i in range(min(10, len(df_moura))):
                for j in range(len(df_moura.columns)):
                    try:
                        valor = str(df_moura.iloc[i, j]).strip().upper()
                        
                        if 'PUBLICO' in valor or 'MINORISTA' in valor:
                            logger.info(f"  ✅ PATRÓN MINORISTA: Fila {i}, Col {j}: '{valor}'")
                        
                        if 'MAYORISTA' in valor:
                            logger.info(f"  ✅ PATRÓN MAYORISTA: Fila {i}, Col {j}: '{valor}'")
                        
                        if 'MARK' in valor and 'UP' in valor:
                            logger.info(f"  ✅ PATRÓN MARKUP: Fila {i}, Col {j}: '{valor}'")
                        
                        if 'RENTABILIDAD' in valor or 'RENT' in valor:
                            logger.info(f"  ✅ PATRÓN RENTABILIDAD: Fila {i}, Col {j}: '{valor}'")
                            
                    except:
                        continue
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    diagnosticar_hoja_moura() 