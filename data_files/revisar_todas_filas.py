#!/usr/bin/env python3
import pandas as pd

def revisar_todas_filas():
    print("🔍 REVISANDO TODAS LAS FILAS")
    print("=" * 50)
    
    # Leer el archivo
    df = pd.read_excel('Rentalibilidades-2.xlsx', sheet_name='Moura')
    
    print(f"📊 Forma del DataFrame: {df.shape}")
    print()
    
    # Revisar las primeras 15 filas
    for fila in range(min(15, len(df))):
        print(f"📋 FILA {fila + 1}:")
        valores_encontrados = []
        for col in range(len(df.columns)):
            try:
                valor = str(df.iloc[fila, col]).strip()
                if valor and valor != 'nan' and valor != '':
                    valores_encontrados.append(f"Col{col}: '{valor}'")
            except:
                continue
        
        # Mostrar solo los primeros 20 valores para no saturar
        for i, valor in enumerate(valores_encontrados[:20]):
            print(f"  {valor}")
        if len(valores_encontrados) > 20:
            print(f"  ... y {len(valores_encontrados) - 20} valores más")
        print()

if __name__ == "__main__":
    revisar_todas_filas() 