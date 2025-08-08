#!/usr/bin/env python3
import pandas as pd

def revisar_columnas_25_26():
    print("🔍 REVISANDO COLUMNAS 25 Y 26")
    print("=" * 50)
    
    # Leer el archivo
    df = pd.read_excel('Rentalibilidades-2.xlsx', sheet_name='Moura')
    
    print("📊 VALORES EN COLUMNA 25 (Mark-up Mayorista):")
    for i in range(2, min(15, len(df))):
        valor = df.iloc[i, 25]
        codigo = df.iloc[i, 0]
        if pd.notna(valor) and valor != '':
            print(f"  {codigo}: {valor}")
    
    print()
    print("📊 VALORES EN COLUMNA 26 (Rentabilidad Mayorista):")
    for i in range(2, min(15, len(df))):
        valor = df.iloc[i, 26]
        codigo = df.iloc[i, 0]
        if pd.notna(valor) and valor != '':
            print(f"  {codigo}: {valor}")
    
    print()
    print("📊 COMPARACIÓN:")
    print("Código | Col16 (Minorista) | Col17 (Rent) | Col25 (Mayorista) | Col26 (Rent)")
    print("-" * 80)
    
    for i in range(2, min(10, len(df))):
        codigo = df.iloc[i, 0]
        col16 = df.iloc[i, 16] if pd.notna(df.iloc[i, 16]) else "N/A"
        col17 = df.iloc[i, 17] if pd.notna(df.iloc[i, 17]) else "N/A"
        col25 = df.iloc[i, 25] if pd.notna(df.iloc[i, 25]) else "N/A"
        col26 = df.iloc[i, 26] if pd.notna(df.iloc[i, 26]) else "N/A"
        
        print(f"{codigo:10} | {col16:16} | {col17:12} | {col25:16} | {col26:12}")

if __name__ == "__main__":
    revisar_columnas_25_26() 