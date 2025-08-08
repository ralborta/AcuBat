#!/usr/bin/env python3
"""
Verificar la estructura real del archivo de rentabilidades
"""
import pandas as pd
import os

def verificar_estructura_archivo():
    """Verificar la estructura del archivo de rentabilidades"""
    
    archivo = 'Rentalibilidades-2.xlsx'
    
    if not os.path.exists(archivo):
        print(f"❌ Archivo {archivo} no encontrado")
        return
    
    try:
        # Leer la hoja Moura
        df = pd.read_excel(archivo, sheet_name='Moura')
        print(f"✅ Archivo {archivo} leído correctamente")
        print(f"📊 Dimensiones: {df.shape}")
        
        print(f"\n📋 Columnas disponibles:")
        for i, col in enumerate(df.columns):
            print(f"   {i}: {col}")
        
        print(f"\n📋 Primeras 5 filas:")
        print(df.head())
        
        print(f"\n🔍 Verificando si hay markups variados:")
        
        # Buscar columnas que puedan contener markups
        for i, col in enumerate(df.columns):
            if 'markup' in col.lower() or 'mayorista' in col.lower() or 'minorista' in col.lower():
                valores_unicos = df[col].dropna().unique()
                print(f"   Columna {i} ({col}): {len(valores_unicos)} valores únicos")
                if len(valores_unicos) <= 5:
                    print(f"      Valores: {valores_unicos}")
                    
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")

if __name__ == "__main__":
    verificar_estructura_archivo() 