#!/usr/bin/env python3
import pandas as pd

def buscar_markups_reales():
    print("🔍 BUSCANDO MARKUPS REALES (93%, 82%, etc.)")
    print("=" * 60)
    
    # Leer el archivo
    df = pd.read_excel('Rentalibilidades-2.xlsx', sheet_name='Moura')
    
    print(f"📊 Forma del DataFrame: {df.shape}")
    print()
    
    # Buscar valores que se parezcan a markups (entre 50 y 200)
    print("🎯 BUSCANDO VALORES ENTRE 50 Y 200 (posibles markups):")
    
    for fila in range(len(df)):
        for col in range(len(df.columns)):
            try:
                valor = df.iloc[fila, col]
                if pd.notna(valor) and isinstance(valor, (int, float)):
                    if 50 <= valor <= 200:
                        codigo = df.iloc[fila, 0] if fila > 0 else "HEADER"
                        print(f"  Fila {fila+1}, Col {col}: {valor} (Código: {codigo})")
            except:
                continue
    
    print()
    print("🎯 BUSCANDO VALORES ENTRE 80 Y 100 (markups típicos):")
    
    for fila in range(len(df)):
        for col in range(len(df.columns)):
            try:
                valor = df.iloc[fila, col]
                if pd.notna(valor) and isinstance(valor, (int, float)):
                    if 80 <= valor <= 100:
                        codigo = df.iloc[fila, 0] if fila > 0 else "HEADER"
                        print(f"  Fila {fila+1}, Col {col}: {valor} (Código: {codigo})")
            except:
                continue
    
    print()
    print("🎯 BUSCANDO VALORES QUE CONTENGAN '93' O '82':")
    
    for fila in range(len(df)):
        for col in range(len(df.columns)):
            try:
                valor = str(df.iloc[fila, col])
                if '93' in valor or '82' in valor:
                    codigo = df.iloc[fila, 0] if fila > 0 else "HEADER"
                    print(f"  Fila {fila+1}, Col {col}: {valor} (Código: {codigo})")
            except:
                continue

if __name__ == "__main__":
    buscar_markups_reales() 