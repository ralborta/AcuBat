#!/usr/bin/env python3
"""
Script para crear un archivo de ejemplo de rentabilidades
"""

import pandas as pd
import os

def crear_rentabilidades_ejemplo():
    """Crea un archivo de ejemplo de rentabilidades"""
    
    # Datos de ejemplo para rentabilidades
    datos = {
        'Marca': [
            'Moura', 'Moura', 'Moura', 'Moura',
            'Acubat', 'Acubat', 'Acubat', 'Acubat',
            'Lubeck', 'Lubeck', 'Lubeck', 'Lubeck',
            'Solar', 'Solar', 'Solar', 'Solar',
            'Zetta', 'Zetta', 'Zetta', 'Zetta'
        ],
        'Canal': [
            'Minorista', 'Minorista', 'Mayorista', 'Mayorista',
            'Minorista', 'Minorista', 'Mayorista', 'Mayorista',
            'Minorista', 'Minorista', 'Mayorista', 'Mayorista',
            'Minorista', 'Minorista', 'Mayorista', 'Mayorista',
            'Minorista', 'Minorista', 'Mayorista', 'Mayorista'
        ],
        'Línea': [
            'Estándar', 'EFB', 'Estándar', 'EFB',
            'Estándar', 'Premium', 'Estándar', 'Premium',
            'Estándar', 'AGM', 'Estándar', 'AGM',
            'Estándar', 'Asiática', 'Estándar', 'Asiática',
            'Estándar', 'Premium', 'Estándar', 'Premium'
        ],
        'Margen Mínimo': [
            20, 25, 15, 20,
            25, 30, 20, 25,
            18, 22, 12, 18,
            15, 20, 10, 15,
            22, 28, 18, 22
        ],
        'Margen Óptimo': [
            35, 40, 25, 30,
            40, 45, 30, 35,
            30, 35, 20, 25,
            25, 30, 18, 22,
            35, 40, 28, 32
        ]
    }
    
    # Crear DataFrame
    df = pd.DataFrame(datos)
    
    # Crear directorio si no existe
    os.makedirs('data', exist_ok=True)
    
    # Guardar archivo
    ruta_archivo = 'data/Rentalibilidades.xlsx'
    df.to_excel(ruta_archivo, index=False)
    
    print(f"✅ Archivo de rentabilidades creado: {ruta_archivo}")
    print(f"📊 Reglas creadas: {len(df)}")
    print("\n📋 Estructura del archivo:")
    print(df.head(10).to_string(index=False))
    
    print("\n🎯 Instrucciones de uso:")
    print("1. Sube este archivo usando el botón 'Cargar Rentabilidades'")
    print("2. Luego sube tu lista de productos")
    print("3. El sistema validará automáticamente la rentabilidad")
    
    return ruta_archivo

if __name__ == "__main__":
    crear_rentabilidades_ejemplo() 