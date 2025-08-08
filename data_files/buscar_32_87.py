#!/usr/bin/env python3
import pandas as pd

def buscar_32_87():
    print("🔍 BUSCANDO EL VALOR 32.87% EN MOURA")
    print("=" * 50)
    
    # Leer la hoja Moura
    df = pd.read_excel('Rentalibilidades-2.xlsx', sheet_name='Moura')
    
    print(f"📊 Forma del DataFrame: {df.shape}")
    print()
    
    # Buscar el valor 32.87 o 0.3287 en todas las columnas
    valor_buscar = [32.87, 0.3287, 32.87, 0.3287]
    
    for i in range(len(df)):
        for j in range(len(df.columns)):
            valor = df.iloc[i, j]
            if pd.notna(valor):
                # Buscar valores cercanos a 32.87%
                if isinstance(valor, (int, float)):
                    if abs(valor - 32.87) < 1 or abs(valor - 0.3287) < 0.01:
                        codigo = str(df.iloc[i, 0]).strip()
                        print(f"🎯 Encontrado {valor} en fila {i+1}, columna {j} ({chr(65+j)}) - Producto: {codigo}")
    
    print("\n🔍 REVISANDO COLUMNAS ESPECÍFICAS:")
    # Revisar columnas específicas donde podría estar
    columnas_revisar = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
    
    for producto in ['M18FD (100)', 'M22ED (100)', 'M20GD (80)', 'M22GD (80)']:
        print(f"\n🔍 {producto}:")
        for i in range(len(df)):
            codigo = str(df.iloc[i, 0]).strip()
            if codigo == producto:
                for col in columnas_revisar:
                    if col < len(df.columns):
                        valor = df.iloc[i, col]
                        if pd.notna(valor) and isinstance(valor, (int, float)):
                            print(f"  Col {col} ({chr(65+col)}): {valor}")
                break

if __name__ == "__main__":
    buscar_32_87() 