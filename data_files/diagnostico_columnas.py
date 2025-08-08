#!/usr/bin/env python3
import pandas as pd
import numpy as np

def diagnosticar_columnas():
    print("🔍 DIAGNÓSTICO DE COLUMNAS - Rentalibilidades-2.xlsx")
    print("=" * 60)
    
    # Leer el archivo
    df = pd.read_excel('Rentalibilidades-2.xlsx', sheet_name='Moura')
    
    print(f"📊 Forma del DataFrame: {df.shape}")
    print(f"📋 Columnas: {df.columns.tolist()}")
    print()
    
    # Mostrar fila 2 (headers)
    print("📋 FILA 2 (Headers):")
    for i, valor in enumerate(df.iloc[1]):
        print(f"  Columna {i}: {valor}")
    print()
    
    # Buscar columnas con MARK-UP y RENT
    print("🔍 BUSCANDO COLUMNAS MARK-UP Y RENT:")
    col_markup_minorista = None
    col_rent_minorista = None
    col_markup_mayorista = None
    col_rent_mayorista = None
    
    for j in range(len(df.columns)):
        try:
            valor = str(df.iloc[1, j]).strip().upper()
            if 'MARK' in valor and 'UP' in valor:
                if col_markup_minorista is None:
                    col_markup_minorista = j
                    print(f"  ✅ MARK-UP Minorista: Columna {j} = '{df.iloc[1, j]}'")
                elif col_markup_mayorista is None:
                    col_markup_mayorista = j
                    print(f"  ✅ MARK-UP Mayorista: Columna {j} = '{df.iloc[1, j]}'")
            elif 'RENT' in valor and 'RENTABILIDAD' not in valor:
                if col_rent_minorista is None:
                    col_rent_minorista = j
                    print(f"  ✅ RENT Minorista: Columna {j} = '{df.iloc[1, j]}'")
            elif 'RENTABILIDAD' in valor:
                if col_rent_mayorista is None:
                    col_rent_mayorista = j
                    print(f"  ✅ RENTABILIDAD Mayorista: Columna {j} = '{df.iloc[1, j]}'")
        except:
            continue
    
    print()
    print("📊 PRIMEROS 5 PRODUCTOS CON SUS MARKUPS:")
    print("Código | Precio Base | Markup Minorista | Rent Minorista | Markup Mayorista | Rent Mayorista")
    print("-" * 100)
    
    for i in range(2, min(7, len(df))):
        try:
            codigo = str(df.iloc[i, 0]).strip()
            precio_base = df.iloc[i, 1]
            
            markup_minorista = df.iloc[i, col_markup_minorista] if col_markup_minorista is not None else "N/A"
            rent_minorista = df.iloc[i, col_rent_minorista] if col_rent_minorista is not None else "N/A"
            markup_mayorista = df.iloc[i, col_markup_mayorista] if col_markup_mayorista is not None else "N/A"
            rent_mayorista = df.iloc[i, col_rent_mayorista] if col_rent_mayorista is not None else "N/A"
            
            print(f"{codigo:8} | {precio_base:10} | {markup_minorista:16} | {rent_minorista:13} | {markup_mayorista:16} | {rent_mayorista:13}")
        except Exception as e:
            print(f"Error en fila {i}: {e}")
    
    print()
    print("🎯 POSICIONES FINALES DETECTADAS:")
    print(f"  MARK-UP Minorista: Columna {col_markup_minorista}")
    print(f"  RENT Minorista: Columna {col_rent_minorista}")
    print(f"  MARK-UP Mayorista: Columna {col_markup_mayorista}")
    print(f"  RENTABILIDAD Mayorista: Columna {col_rent_mayorista}")

if __name__ == "__main__":
    diagnosticar_columnas() 