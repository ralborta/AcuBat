#!/usr/bin/env python3
import pandas as pd

def buscar_columnas_p_y():
    print("🔍 BUSCANDO COLUMNAS P Y Y")
    print("=" * 50)
    
    # Leer el archivo
    df = pd.read_excel('Rentalibilidades-2.xlsx', sheet_name='Moura')
    
    print(f"📊 Forma del DataFrame: {df.shape}")
    print()
    
    # Buscar en todas las filas por las columnas P y Y
    for fila in range(min(10, len(df))):  # Revisar las primeras 10 filas
        print(f"📋 FILA {fila + 1}:")
        for col in range(len(df.columns)):
            try:
                valor = str(df.iloc[fila, col]).strip().upper()
                if valor == 'P' or valor == 'Y':
                    print(f"  ✅ Columna {col}: '{df.iloc[fila, col]}' (Fila {fila + 1})")
            except:
                continue
        print()
    
    # Buscar específicamente en la línea 5 (fila 4)
    print("🎯 BUSCANDO ESPECÍFICAMENTE EN LÍNEA 5 (fila 4):")
    fila_5 = df.iloc[4]  # Línea 5
    columna_p = None
    columna_y = None
    
    for j, valor in enumerate(fila_5):
        valor_str = str(valor).strip().upper()
        if valor_str == 'P':
            columna_p = j
            print(f"  ✅ COLUMNA P ENCONTRADA en posición {j}")
        elif valor_str == 'Y':
            columna_y = j
            print(f"  ✅ COLUMNA Y ENCONTRADA en posición {j}")
    
    if columna_p is not None:
        print(f"🎯 COLUMNA P (Minorista): Posición {columna_p}")
        print("   Valores de la columna P:")
        for i in range(5, min(15, len(df))):  # Desde línea 6
            valor = df.iloc[i, columna_p]
            if pd.notna(valor) and valor != '':
                print(f"     Línea {i+1}: {valor}")
    else:
        print("❌ NO SE ENCONTRÓ COLUMNA P")
    
    if columna_y is not None:
        print(f"🎯 COLUMNA Y (Mayorista): Posición {columna_y}")
        print("   Valores de la columna Y:")
        for i in range(5, min(15, len(df))):  # Desde línea 6
            valor = df.iloc[i, columna_y]
            if pd.notna(valor) and valor != '':
                print(f"     Línea {i+1}: {valor}")
    else:
        print("❌ NO SE ENCONTRÓ COLUMNA Y")

if __name__ == "__main__":
    buscar_columnas_p_y() 