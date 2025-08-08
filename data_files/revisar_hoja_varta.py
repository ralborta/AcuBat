#!/usr/bin/env python3
import pandas as pd

def revisar_hoja_varta():
    print("🔍 REVISANDO HOJA VARTA")
    print("=" * 50)
    
    # Leer la hoja Varta
    df = pd.read_excel('Rentalibilidades-2.xlsx', sheet_name='Varta')
    
    print(f"📊 Forma del DataFrame: {df.shape}")
    print()
    
    # Buscar las columnas correctas
    print("🔍 BUSCANDO COLUMNAS MARK-UP Y MAK-UP:")
    
    for fila in range(min(10, len(df))):
        print(f"📋 FILA {fila + 1}:")
        for col in range(len(df.columns)):
            try:
                valor = str(df.iloc[fila, col]).strip()
                if valor and valor != 'nan':
                    print(f"  Col{col}: '{valor}'")
            except:
                continue
        print()
    
    # Buscar específicamente las columnas Q y Y
    print("🎯 BUSCANDO COLUMNAS Q (16) Y Y (24):")
    
    if len(df.columns) > 24:
        print("📊 VALORES EN COLUMNA Q (16) - Mak-up Mayorista:")
        for i in range(2, min(10, len(df))):
            try:
                codigo = str(df.iloc[i, 0]).strip()
                valor_q = df.iloc[i, 16]
                if pd.notna(valor_q) and valor_q != '':
                    print(f"  {codigo}: {valor_q}")
            except:
                continue
        
        print()
        print("📊 VALORES EN COLUMNA Y (24) - Mark-UP Minorista:")
        for i in range(2, min(10, len(df))):
            try:
                codigo = str(df.iloc[i, 0]).strip()
                valor_y = df.iloc[i, 24]
                if pd.notna(valor_y) and valor_y != '':
                    print(f"  {codigo}: {valor_y}")
            except:
                continue

if __name__ == "__main__":
    revisar_hoja_varta() 