#!/usr/bin/env python3
import pandas as pd

def revisar_moura_completo():
    print("🔍 REVISANDO TODA LA HOJA MOURA")
    print("=" * 50)
    
    # Leer la hoja Moura
    df = pd.read_excel('Rentalibilidades-2.xlsx', sheet_name='Moura')
    
    print(f"📊 Forma del DataFrame: {df.shape}")
    print()
    
    # Revisar TODAS las filas de la hoja Moura
    print("🔍 BUSCANDO 'P' Y 'Y' EN TODAS LAS FILAS:")
    
    for fila in range(len(df)):
        encontrado_p = False
        encontrado_y = False
        
        for col in range(len(df.columns)):
            try:
                valor = str(df.iloc[fila, col]).strip().upper()
                if valor == 'P':
                    encontrado_p = True
                    print(f"  ✅ 'P' encontrado en Fila {fila+1}, Columna {col}")
                elif valor == 'Y':
                    encontrado_y = True
                    print(f"  ✅ 'Y' encontrado en Fila {fila+1}, Columna {col}")
            except:
                continue
        
        if encontrado_p or encontrado_y:
            print(f"  📋 Fila {fila+1} completa:")
            for col in range(len(df.columns)):
                try:
                    valor = str(df.iloc[fila, col]).strip()
                    if valor and valor != 'nan':
                        print(f"    Col{col}: '{valor}'")
                except:
                    continue
            print()
    
    print()
    print("🎯 BUSCANDO VALORES QUE SEAN NÚMEROS GRANDES (como 93, 82):")
    
    for fila in range(len(df)):
        for col in range(len(df.columns)):
            try:
                valor = df.iloc[fila, col]
                if pd.notna(valor) and isinstance(valor, (int, float)):
                    if valor >= 50 and valor <= 200:  # Posibles markups
                        codigo = df.iloc[fila, 0] if fila > 0 else "HEADER"
                        print(f"  Fila {fila+1}, Col {col}: {valor} (Código: {codigo})")
            except:
                continue

if __name__ == "__main__":
    revisar_moura_completo() 