#!/usr/bin/env python3
"""
Verificar todas las hojas del archivo de rentabilidades
"""
import pandas as pd
import os

def verificar_todas_hojas():
    """Verificar todas las hojas del archivo"""
    
    archivo = 'Rentalibilidades-2.xlsx'
    
    if not os.path.exists(archivo):
        print(f"❌ Archivo {archivo} no encontrado")
        return
    
    try:
        # Leer todas las hojas
        xl = pd.ExcelFile(archivo)
        hojas = xl.sheet_names
        
        print(f"✅ Archivo {archivo} leído correctamente")
        print(f"📊 Hojas disponibles: {hojas}")
        
        for hoja in hojas:
            print(f"\n{'='*50}")
            print(f"📋 HOJA: {hoja}")
            print(f"{'='*50}")
            
            df = xl.parse(hoja)
            print(f"📊 Dimensiones: {df.shape}")
            
            print(f"📋 Columnas:")
            for i, col in enumerate(df.columns):
                print(f"   {i}: {col}")
            
            print(f"\n📋 Primeras 3 filas:")
            print(df.head(3))
            
            # Buscar columnas de markup
            for i, col in enumerate(df.columns):
                if 'markup' in col.lower() or 'mayorista' in col.lower():
                    valores_unicos = df[col].dropna().unique()
                    print(f"\n🔍 Columna {i} ({col}): {len(valores_unicos)} valores únicos")
                    if len(valores_unicos) <= 10:
                        print(f"   Valores: {sorted(valores_unicos)}")
                    else:
                        print(f"   Primeros 10: {sorted(valores_unicos[:10])}")
                        print(f"   ... y {len(valores_unicos) - 10} más")
                        
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")

if __name__ == "__main__":
    verificar_todas_hojas() 