#!/usr/bin/env python3
"""
Script para analizar la estructura de archivos Excel
"""

import pandas as pd
import sys
import os

def analizar_excel(ruta_archivo):
    """Analiza la estructura de un archivo Excel"""
    try:
        # Leer el archivo
        df = pd.read_excel(ruta_archivo)
        
        print(f"📊 Análisis del archivo: {ruta_archivo}")
        print("=" * 50)
        
        # Información básica
        print(f"📋 Filas: {len(df)}")
        print(f"📋 Columnas: {len(df.columns)}")
        print()
        
        # Mostrar columnas
        print("📋 COLUMNAS ENCONTRADAS:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. '{col}'")
        print()
        
        # Mostrar primeras filas
        print("📋 PRIMERAS 3 FILAS:")
        print(df.head(3).to_string())
        print()
        
        # Verificar datos
        print("📋 ANÁLISIS DE DATOS:")
        for col in df.columns:
            valores_no_vacios = df[col].notna().sum()
            print(f"  '{col}': {valores_no_vacios}/{len(df)} valores no vacíos")
        
        print()
        print("💡 SUGERENCIAS:")
        
        # Mapeo de columnas
        mapeo_sugerido = {}
        for col in df.columns:
            col_lower = col.lower()
            if any(palabra in col_lower for palabra in ['codigo', 'code', 'id']):
                mapeo_sugerido[col] = 'codigo'
            elif any(palabra in col_lower for palabra in ['nombre', 'name', 'desc', 'producto']):
                mapeo_sugerido[col] = 'nombre'
            elif any(palabra in col_lower for palabra in ['precio', 'price', 'costo']):
                mapeo_sugerido[col] = 'precio_base'
            elif any(palabra in col_lower for palabra in ['marca', 'brand']):
                mapeo_sugerido[col] = 'marca'
            elif any(palabra in col_lower for palabra in ['canal', 'channel', 'tipo']):
                mapeo_sugerido[col] = 'canal'
        
        if mapeo_sugerido:
            print("  Mapeo sugerido de columnas:")
            for col_original, col_sugerido in mapeo_sugerido.items():
                print(f"    '{col_original}' → '{col_sugerido}'")
        else:
            print("  No se detectaron columnas que coincidan con el formato esperado")
        
        return df
        
    except Exception as e:
        print(f"❌ Error al analizar el archivo: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
        analizar_excel(archivo)
    else:
        # Analizar archivos en el directorio data
        print("🔍 Analizando archivos Excel en el directorio 'data':")
        print()
        
        if os.path.exists("data"):
            archivos = [f for f in os.listdir("data") if f.endswith(('.xlsx', '.xls'))]
            if archivos:
                for archivo in archivos:
                    ruta = os.path.join("data", archivo)
                    analizar_excel(ruta)
                    print("\n" + "="*60 + "\n")
            else:
                print("❌ No se encontraron archivos Excel en el directorio 'data'")
        else:
            print("❌ El directorio 'data' no existe") 