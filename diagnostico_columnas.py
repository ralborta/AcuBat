#!/usr/bin/env python3
"""
Script para diagnosticar qué columnas está detectando el sistema
en el archivo Rentalibilidades-2.xlsx
"""

import pandas as pd
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def diagnosticar_columnas():
    """Diagnostica las columnas del archivo de rentabilidades"""
    
    archivo = "Rentalibilidades-2.xlsx"
    
    try:
        # Leer el archivo
        logger.info(f"📁 Leyendo archivo: {archivo}")
        df = pd.read_excel(archivo, sheet_name=None)
        
        # Mostrar hojas disponibles
        logger.info(f"📋 Hojas disponibles: {list(df.keys())}")
        
        # Analizar cada hoja
        for hoja_nombre, df_hoja in df.items():
            logger.info(f"\n🔍 ANALIZANDO HOJA: {hoja_nombre}")
            logger.info(f"📏 Dimensiones: {df_hoja.shape}")
            
            # Mostrar las primeras 10 filas y 30 columnas
            logger.info(f"📊 Primeras 10 filas, primeras 30 columnas:")
            
            for i in range(min(10, len(df_hoja))):
                fila_info = f"Fila {i}: "
                for j in range(min(30, len(df_hoja.columns))):
                    valor = str(df_hoja.iloc[i, j]).strip()
                    if valor and valor != 'nan':
                        fila_info += f"[{j}]:'{valor}' "
                if fila_info != f"Fila {i}: ":
                    logger.info(fila_info)
            
            # Buscar específicamente las columnas P y Y en la línea 5 (fila 4)
            if len(df_hoja) > 4:
                logger.info(f"\n🎯 BUSCANDO COLUMNAS P y Y EN LÍNEA 5 (fila 4):")
                fila_5 = df_hoja.iloc[4]  # Línea 5
                
                columna_p = None
                columna_y = None
                
                for j, valor in enumerate(fila_5):
                    valor_str = str(valor).strip().upper()
                    logger.info(f"  Columna {j}: '{valor_str}'")
                    
                    if valor_str == 'P' or 'P.' in valor_str:
                        columna_p = j
                        logger.info(f"  ✅ COLUMNA P ENCONTRADA en posición {j}")
                    
                    if valor_str == 'Y' or 'Y.' in valor_str:
                        columna_y = j
                        logger.info(f"  ✅ COLUMNA Y ENCONTRADA en posición {j}")
                
                if columna_p is not None:
                    logger.info(f"🎯 COLUMNA P (Minorista): Posición {columna_p}")
                else:
                    logger.info(f"❌ NO SE ENCONTRÓ COLUMNA P")
                
                if columna_y is not None:
                    logger.info(f"🎯 COLUMNA Y (Mayorista): Posición {columna_y}")
                else:
                    logger.info(f"❌ NO SE ENCONTRÓ COLUMNA Y")
                
                # Mostrar datos de las columnas P y Y si se encontraron
                if columna_p is not None or columna_y is not None:
                    logger.info(f"\n📊 DATOS DE LAS COLUMNAS DETECTADAS:")
                    
                    for i in range(5, min(15, len(df_hoja))):  # Desde línea 6
                        fila_data = f"Línea {i+1}: "
                        
                        if columna_p is not None:
                            valor_p = df_hoja.iloc[i, columna_p]
                            fila_data += f"P[{columna_p}]='{valor_p}' "
                        
                        if columna_y is not None:
                            valor_y = df_hoja.iloc[i, columna_y]
                            fila_data += f"Y[{columna_y}]='{valor_y}' "
                        
                        logger.info(fila_data)
            
            # Buscar patrones de texto que el sistema actual está buscando
            logger.info(f"\n🔍 BUSCANDO PATRONES QUE EL SISTEMA DETECTA:")
            
            for i in range(min(10, len(df_hoja))):
                for j in range(min(30, len(df_hoja.columns))):
                    try:
                        valor = str(df_hoja.iloc[i, j]).strip().upper()
                        
                        if 'P. PUBLICO' in valor or 'PUBLICO' in valor or 'MINORISTA' in valor:
                            logger.info(f"  ✅ PATRÓN MINORISTA: Fila {i}, Col {j}: '{valor}'")
                        
                        if 'P. MAYORISTA' in valor or 'MAYORISTA' in valor:
                            logger.info(f"  ✅ PATRÓN MAYORISTA: Fila {i}, Col {j}: '{valor}'")
                            
                    except:
                        continue
            
            logger.info(f"\n{'='*50}")
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    diagnosticar_columnas() 