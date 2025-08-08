#!/usr/bin/env python3
import pandas as pd
from api.moura_rentabilidad import _convertir_porcentaje, _convertir_precio

def debug_calculo_detallado():
    print("🔍 DEBUG DETALLADO DE CÁLCULOS")
    print("=" * 60)
    
    # Leer la hoja Moura
    df = pd.read_excel('Rentalibilidades-2.xlsx', sheet_name='Moura')
    
    # Productos específicos para debug
    productos = ['M40FD', 'M18FD (100)', 'M22ED (100)', 'M20GD (80)', 'M22GD (80)']
    
    print("📊 VALORES RAW DE LAS COLUMNAS:")
    for producto in productos:
        print(f"\n🔍 Producto: {producto}")
        
        # Buscar el producto
        for i in range(len(df)):
            codigo = str(df.iloc[i, 0]).strip()
            if codigo == producto:
                print(f"  Fila: {i+1}")
                print(f"  Precio Base: {df.iloc[i, 1]}")
                
                # Valores raw de las columnas
                print(f"  Col 15 (Q) - Raw: {df.iloc[i, 15]}")
                print(f"  Col 16 (R) - Raw: {df.iloc[i, 16]}")
                print(f"  Col 24 (Y) - Raw: {df.iloc[i, 24]}")
                print(f"  Col 25 (Z) - Raw: {df.iloc[i, 25]}")
                
                # Convertir con la función
                markup_minorista = _convertir_porcentaje(df.iloc[i, 16])
                rent_minorista = _convertir_porcentaje(df.iloc[i, 17])
                markup_mayorista = _convertir_porcentaje(df.iloc[i, 25])
                rent_mayorista = _convertir_porcentaje(df.iloc[i, 26])
                
                print(f"  Minorista - Markup: {markup_minorista}%, Rent: {rent_minorista}%")
                print(f"  Mayorista - Markup: {markup_mayorista}%, Rent: {rent_mayorista}%")
                break
    
    print("\n" + "=" * 60)
    print("🎯 PREGUNTA CRÍTICA:")
    print("¿Los valores en las columnas son:")
    print("1. Markups ya calculados (ej: 22% = 22)")
    print("2. Factores de multiplicación (ej: 1.22 = 22%)")
    print("3. Otro formato?")
    print()
    print("¿Qué valores esperas ver para cada producto?")

if __name__ == "__main__":
    debug_calculo_detallado() 