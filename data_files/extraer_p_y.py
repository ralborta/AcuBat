#!/usr/bin/env python3
import pandas as pd

def extraer_p_y():
    print("🔍 EXTRAYENDO DATOS DE COLUMNAS P Y Y")
    print("=" * 50)
    
    # Leer el archivo
    df = pd.read_excel('Rentalibilidades-2.xlsx', sheet_name='Moura')
    
    print(f"📊 Forma del DataFrame: {df.shape}")
    print()
    
    # Buscar las columnas P y Y en todas las filas
    columna_p = None
    columna_y = None
    
    print("🔍 BUSCANDO COLUMNAS P Y Y:")
    for fila in range(min(10, len(df))):
        for col in range(len(df.columns)):
            try:
                valor = str(df.iloc[fila, col]).strip().upper()
                if valor == 'P' and columna_p is None:
                    columna_p = col
                    print(f"  ✅ COLUMNA P encontrada en Fila {fila+1}, Columna {col}")
                elif valor == 'Y' and columna_y is None:
                    columna_y = col
                    print(f"  ✅ COLUMNA Y encontrada en Fila {fila+1}, Columna {col}")
            except:
                continue
    
    print()
    
    if columna_p is not None:
        print(f"📊 DATOS DE COLUMNA P (Posición {columna_p}):")
        print("Código | Valor P")
        print("-" * 30)
        for i in range(2, min(15, len(df))):
            try:
                codigo = str(df.iloc[i, 0]).strip()
                valor_p = df.iloc[i, columna_p]
                if pd.notna(valor_p) and valor_p != '':
                    print(f"{codigo:10} | {valor_p}")
            except:
                continue
    else:
        print("❌ NO SE ENCONTRÓ COLUMNA P")
    
    print()
    
    if columna_y is not None:
        print(f"📊 DATOS DE COLUMNA Y (Posición {columna_y}):")
        print("Código | Valor Y")
        print("-" * 30)
        for i in range(2, min(15, len(df))):
            try:
                codigo = str(df.iloc[i, 0]).strip()
                valor_y = df.iloc[i, columna_y]
                if pd.notna(valor_y) and valor_y != '':
                    print(f"{codigo:10} | {valor_y}")
            except:
                continue
    else:
        print("❌ NO SE ENCONTRÓ COLUMNA Y")
    
    print()
    print("🎯 RESUMEN:")
    print(f"  Columna P: {columna_p}")
    print(f"  Columna Y: {columna_y}")

if __name__ == "__main__":
    extraer_p_y() 