#!/usr/bin/env python3
import pandas as pd

def verificar_columnas_moura():
    print("🔍 VERIFICANDO COLUMNAS CORRECTAS EN MOURA")
    print("=" * 60)
    
    # Leer la hoja Moura
    df = pd.read_excel('Rentalibilidades-2.xlsx', sheet_name='Moura')
    
    print(f"📊 Forma del DataFrame: {df.shape}")
    print()
    
    # Buscar productos específicos
    productos_buscar = ['M40FD', 'M18FD (100)', 'M22ED (100)', 'M20GD (80)', 'M22GD (80)']
    
    print("📊 VALORES POR PRODUCTO:")
    for producto in productos_buscar:
        print(f"\n🔍 Producto: {producto}")
        
        # Buscar el producto en la hoja
        encontrado = False
        for i in range(len(df)):
            codigo = str(df.iloc[i, 0]).strip()
            if codigo == producto:
                encontrado = True
                print(f"  Fila: {i+1}")
                print(f"  Precio Base: {df.iloc[i, 1]}")
                print(f"  Columna 15 (Q): {df.iloc[i, 15]}")  # Mak-up Mayorista
                print(f"  Columna 16 (R): {df.iloc[i, 16]}")  # rentabili Mayorista
                print(f"  Columna 24 (Y): {df.iloc[i, 24]}")  # Mark-UP Minorista
                print(f"  Columna 25 (Z): {df.iloc[i, 25]}")  # Rentabilidad Minorista
                break
        
        if not encontrado:
            print(f"  ❌ No encontrado")
    
    print()
    print("🎯 VERIFICACIÓN:")
    print("Los valores deberían ser:")
    print("  M40FD: Mayorista ~32.87%, Minorista ~22%")
    print("  M18FD: Mayorista ~32.87%, Minorista ~22%")
    print("  M22ED: Mayorista ~32.87%, Minorista ~17%")
    print("  M20GD: Mayorista ~32.87%, Minorista ~22%")
    print("  M22GD: Mayorista ~32.87%, Minorista ~19%")

if __name__ == "__main__":
    verificar_columnas_moura() 