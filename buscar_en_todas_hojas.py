#!/usr/bin/env python3
import pandas as pd

def buscar_en_todas_hojas():
    print("🔍 BUSCANDO COLUMNAS P Y Y EN TODAS LAS HOJAS")
    print("=" * 60)
    
    # Leer todas las hojas del archivo
    xl = pd.ExcelFile('Rentalibilidades-2.xlsx')
    print(f"📋 Hojas disponibles: {xl.sheet_names}")
    print()
    
    for hoja_nombre in xl.sheet_names:
        print(f"🔍 REVISANDO HOJA: {hoja_nombre}")
        df = xl.parse(hoja_nombre)
        
        columna_p = None
        columna_y = None
        
        # Buscar en las primeras 10 filas
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
        
        if columna_p is not None or columna_y is not None:
            print(f"  📊 Datos encontrados en hoja {hoja_nombre}:")
            
            if columna_p is not None:
                print(f"    Columna P (posición {columna_p}):")
                for i in range(2, min(7, len(df))):
                    try:
                        codigo = str(df.iloc[i, 0]).strip()
                        valor_p = df.iloc[i, columna_p]
                        if pd.notna(valor_p) and valor_p != '':
                            print(f"      {codigo}: {valor_p}")
                    except:
                        continue
            
            if columna_y is not None:
                print(f"    Columna Y (posición {columna_y}):")
                for i in range(2, min(7, len(df))):
                    try:
                        codigo = str(df.iloc[i, 0]).strip()
                        valor_y = df.iloc[i, columna_y]
                        if pd.notna(valor_y) and valor_y != '':
                            print(f"      {codigo}: {valor_y}")
                    except:
                        continue
        else:
            print(f"  ❌ No se encontraron columnas P o Y en {hoja_nombre}")
        
        print()

if __name__ == "__main__":
    buscar_en_todas_hojas() 