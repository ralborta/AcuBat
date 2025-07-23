#!/usr/bin/env python3
"""
Verificar específicamente la hoja Moura del archivo completo
"""
import pandas as pd
import os

def verificar_moura_completo():
    """Verificar la hoja Moura del archivo completo"""
    
    archivo = 'Rentalibilidades-2.xlsx'
    
    if not os.path.exists(archivo):
        print(f"❌ Archivo {archivo} no encontrado")
        return
    
    try:
        # Leer específicamente la hoja Moura
        df = pd.read_excel(archivo, sheet_name='Moura')
        print(f"✅ Hoja Moura leída correctamente")
        print(f"📊 Dimensiones: {df.shape}")
        
        print(f"\n📋 Columnas disponibles:")
        for i, col in enumerate(df.columns):
            print(f"   {i}: {col}")
        
        print(f"\n📋 Primeras 5 filas:")
        print(df.head())
        
        # Buscar columnas de markup mayorista
        print(f"\n🔍 Buscando columnas de markup mayorista:")
        for i, col in enumerate(df.columns):
            if 'markup' in str(col).lower() or 'mayorista' in str(col).lower():
                try:
                    valores_unicos = df[col].dropna().unique()
                    print(f"   Columna {i} ({col}): {len(valores_unicos)} valores únicos")
                    if len(valores_unicos) <= 15:
                        print(f"      Valores: {sorted(valores_unicos)}")
                    else:
                        print(f"      Primeros 15: {sorted(valores_unicos[:15])}")
                        print(f"      ... y {len(valores_unicos) - 15} más")
                except Exception as e:
                    print(f"      Error procesando columna: {e}")
        
        # Buscar columnas de rentabilidad mayorista
        print(f"\n🔍 Buscando columnas de rentabilidad mayorista:")
        for i, col in enumerate(df.columns):
            if 'rentabilidad' in str(col).lower() or 'rent' in str(col).lower():
                try:
                    valores_unicos = df[col].dropna().unique()
                    print(f"   Columna {i} ({col}): {len(valores_unicos)} valores únicos")
                    if len(valores_unicos) <= 15:
                        print(f"      Valores: {sorted(valores_unicos)}")
                    else:
                        print(f"      Primeros 15: {sorted(valores_unicos[:15])}")
                        print(f"      ... y {len(valores_unicos) - 15} más")
                except Exception as e:
                    print(f"      Error procesando columna: {e}")
                        
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")

if __name__ == "__main__":
    verificar_moura_completo() 