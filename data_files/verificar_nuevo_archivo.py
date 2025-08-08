#!/usr/bin/env python3
import pandas as pd

def verificar_nuevo_archivo():
    print("🔍 VERIFICANDO NUEVO ARCHIVO DE RENTABILIDADES")
    print("=" * 60)
    
    # Leer el nuevo archivo
    df = pd.read_excel('Rentalibilidades-2.xlsx', sheet_name='Moura')
    
    print(f"📊 Forma del DataFrame: {df.shape}")
    print(f"📊 Total de productos: {len(df)}")
    print()
    
    # Mostrar estructura
    print("📋 ESTRUCTURA DEL ARCHIVO:")
    print(f"  Columnas: {list(df.columns)}")
    print()
    
    # Mostrar primeros 10 productos
    print("📋 PRIMEROS 10 PRODUCTOS:")
    for i in range(min(10, len(df))):
        producto = df.iloc[i]
        print(f"  {i+1}. {producto['Código']} - ${producto['Precio Base']:,.0f}")
        print(f"     Minorista: {producto['Markup Minorista (%)']}% (rent: {producto['Rentabilidad Minorista (%)']}%)")
        print(f"     Mayorista: {producto['Markup Mayorista (%)']}% (rent: {producto['Rentabilidad Mayorista (%)']}%)")
        print()
    
    # Estadísticas
    print("📊 ESTADÍSTICAS:")
    print(f"  Markup Minorista promedio: {df['Markup Minorista (%)'].mean():.1f}%")
    print(f"  Markup Mayorista promedio: {df['Markup Mayorista (%)'].mean():.1f}%")
    print(f"  Rentabilidad Minorista promedio: {df['Rentabilidad Minorista (%)'].mean():.1f}%")
    print(f"  Rentabilidad Mayorista promedio: {df['Rentabilidad Mayorista (%)'].mean():.1f}%")

if __name__ == "__main__":
    verificar_nuevo_archivo() 