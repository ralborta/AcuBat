#!/usr/bin/env python3
import pandas as pd

def verificar_moura_correcto():
    print("🔍 VERIFICANDO COLUMNAS CORRECTAS EN MOURA")
    print("=" * 60)
    
    # Leer la hoja Moura
    df = pd.read_excel('Rentalibilidades-2.xlsx', sheet_name='Moura')
    
    print(f"📊 Forma del DataFrame: {df.shape}")
    print()
    
    # Buscar productos específicos
    productos = ['M18FD (100)', 'M22ED (100)', 'M20GD (80)', 'M22GD (80)']
    
    print("📊 VALORES POR PRODUCTO:")
    for producto in productos:
        print(f"\n🔍 Producto: {producto}")
        
        # Buscar el producto
        for i in range(len(df)):
            codigo = str(df.iloc[i, 0]).strip()
            if codigo == producto:
                print(f"  Fila: {i+1}")
                print(f"  Precio Base: {df.iloc[i, 1]}")
                
                # Revisar TODAS las columnas para encontrar 32.87%
                print(f"  Buscando 32.87% en todas las columnas:")
                for col in range(15, 30):  # Columnas O a AD
                    if col < len(df.columns):
                        valor = df.iloc[i, col]
                        if pd.notna(valor) and isinstance(valor, (int, float)):
                            if abs(valor - 32.87) < 1 or abs(valor - 0.3287) < 0.01:
                                print(f"    🎯 Col {col} ({chr(65+col)}): {valor} - ¡ENCONTRADO 32.87%!")
                            else:
                                print(f"    Col {col} ({chr(65+col)}): {valor}")
                break
    
    print("\n" + "=" * 60)
    print("🎯 PREGUNTA:")
    print("¿En qué columna está el 32.87% para mayorista en Moura?")

if __name__ == "__main__":
    verificar_moura_correcto() 