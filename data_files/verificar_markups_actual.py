#!/usr/bin/env python3
"""
Verificar si los markups del canal mayorista están variados
"""
import pandas as pd
import os

def verificar_markups_mayorista():
    """Verificar los markups del canal mayorista en la planilla actual"""
    
    archivo = 'Rentalibilidades-2.xlsx'
    
    if not os.path.exists(archivo):
        print(f"❌ Archivo {archivo} no encontrado")
        return
    
    try:
        # Leer la hoja Moura
        df = pd.read_excel(archivo, sheet_name='Moura')
        print(f"✅ Archivo {archivo} leído correctamente")
        print(f"📊 Dimensiones: {df.shape}")
        
        # Buscar columnas de markup mayorista (columna 16 = P)
        col_markup_mayorista = 16  # Columna P
        
        if col_markup_mayorista < len(df.columns):
            print(f"\n🔍 Verificando columna {col_markup_mayorista} (markup mayorista):")
            
            # Obtener valores únicos
            valores_unicos = df.iloc[:, col_markup_mayorista].dropna().unique()
            print(f"📈 Valores únicos encontrados: {len(valores_unicos)}")
            
            if len(valores_unicos) > 1:
                print("✅ ¡MARKUPS VARIADOS! Los productos tienen diferentes markups")
                for i, valor in enumerate(valores_unicos[:10]):  # Mostrar primeros 10
                    print(f"   {i+1}. {valor}")
                if len(valores_unicos) > 10:
                    print(f"   ... y {len(valores_unicos) - 10} más")
            else:
                print("❌ MARKUP FIJO - Todos los productos tienen el mismo markup")
                print(f"   Valor: {valores_unicos[0] if len(valores_unicos) > 0 else 'N/A'}")
            
            # Mostrar algunos ejemplos
            print(f"\n📋 Primeros 10 productos:")
            for i in range(min(10, len(df))):
                valor = df.iloc[i, col_markup_mayorista]
                codigo = df.iloc[i, 0] if len(df.columns) > 0 else f"Fila {i+1}"
                print(f"   {codigo}: {valor}")
                
        else:
            print(f"❌ Columna {col_markup_mayorista} no existe")
            
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")

if __name__ == "__main__":
    verificar_markups_mayorista() 