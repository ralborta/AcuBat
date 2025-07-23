#!/usr/bin/env python3
"""
Buscar las columnas específicas de markup y rentabilidad en la hoja Moura
"""
import pandas as pd
import os

def buscar_columnas_markup():
    """Buscar columnas de markup y rentabilidad"""
    
    archivo = 'Rentalibilidades-2.xlsx'
    
    if not os.path.exists(archivo):
        print(f"❌ Archivo {archivo} no encontrado")
        return
    
    try:
        # Leer la hoja Moura
        df = pd.read_excel(archivo, sheet_name='Moura')
        print(f"✅ Hoja Moura leída correctamente")
        print(f"📊 Dimensiones: {df.shape}")
        
        print(f"\n🔍 Buscando columnas con markup/rentabilidad:")
        
        # Buscar en todas las columnas
        for i, col in enumerate(df.columns):
            col_str = str(col).lower()
            
            # Buscar columnas que contengan palabras clave
            if any(keyword in col_str for keyword in ['markup', 'mark-up', 'mark up', 'margen', 'rentabilidad', 'rent', 'mayorista', 'minorista']):
                print(f"\n📋 Columna {i}: {col}")
                
                # Mostrar algunos valores
                valores = df[col].dropna().head(10)
                print(f"   Primeros valores: {list(valores)}")
                
                # Contar valores únicos
                valores_unicos = df[col].dropna().unique()
                print(f"   Valores únicos: {len(valores_unicos)}")
                if len(valores_unicos) <= 10:
                    print(f"   Todos los valores: {sorted(valores_unicos)}")
                else:
                    print(f"   Primeros 10: {sorted(valores_unicos[:10])}")
        
        # También buscar en las primeras filas por si hay headers
        print(f"\n🔍 Buscando en las primeras filas por headers:")
        for i in range(min(5, len(df))):
            print(f"   Fila {i}: {list(df.iloc[i, :5])}")
                        
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")

if __name__ == "__main__":
    buscar_columnas_markup() 