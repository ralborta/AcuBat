#!/usr/bin/env python3
"""
Script para probar el sistema de rentabilidades con hojas múltiples
"""

import os
import sys
import pandas as pd

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def crear_rentabilidades_ejemplo_multihojas():
    """Crea un archivo de ejemplo de rentabilidades con múltiples hojas"""
    
    # Crear directorio si no existe
    os.makedirs('data', exist_ok=True)
    
    # Datos para hoja MOURA
    datos_moura = {
        'Canal': ['Minorista', 'Minorista', 'Mayorista', 'Mayorista'],
        'Línea': ['Estándar', 'EFB', 'Estándar', 'EFB'],
        'Margen Mínimo': [20, 25, 15, 20],
        'Margen Óptimo': [35, 40, 25, 30]
    }
    
    # Datos para hoja general
    datos_general = {
        'Canal': ['Minorista', 'Minorista', 'Mayorista', 'Mayorista'],
        'Línea': ['Premium', 'AGM', 'Premium', 'AGM'],
        'Margen Mínimo': [30, 35, 25, 30],
        'Margen Óptimo': [45, 50, 35, 40]
    }
    
    # Crear archivo Excel con múltiples hojas
    with pd.ExcelWriter('data/Rentabilidades.xlsx', engine='openpyxl') as writer:
        # Hoja MOURA
        df_moura = pd.DataFrame(datos_moura)
        df_moura.to_excel(writer, sheet_name='Moura', index=False)
        
        # Hoja General
        df_general = pd.DataFrame(datos_general)
        df_general.to_excel(writer, sheet_name='General', index=False)
        
        # Hoja Acubat (ejemplo)
        df_acubat = pd.DataFrame({
            'Canal': ['Minorista', 'Mayorista'],
            'Línea': ['Estándar', 'Estándar'],
            'Margen Mínimo': [25, 20],
            'Margen Óptimo': [40, 30]
        })
        df_acubat.to_excel(writer, sheet_name='Acubat', index=False)
    
    print("✅ Archivo de rentabilidades con múltiples hojas creado: data/Rentabilidades.xlsx")
    print("📊 Hojas creadas: Moura, General, Acubat")
    
    return 'data/Rentabilidades.xlsx'

def test_rentabilidades():
    """Prueba el sistema de rentabilidades"""
    
    print("🧪 Probando Sistema de Rentabilidades...")
    
    # Crear archivo de ejemplo si no existe
    rentabilidades_file = 'data/Rentabilidades.xlsx'
    if not os.path.exists(rentabilidades_file):
        print("📝 Creando archivo de ejemplo...")
        rentabilidades_file = crear_rentabilidades_ejemplo_multihojas()
    
    try:
        from api.rentabilidad import RentabilidadValidator
        
        # Crear validador
        validator = RentabilidadValidator()
        
        # Cargar rentabilidades
        print(f"📂 Cargando archivo: {rentabilidades_file}")
        success = validator.cargar_rentabilidades(rentabilidades_file)
        
        if not success:
            print("❌ Error al cargar rentabilidades")
            return
        
        print("✅ Rentabilidades cargadas exitosamente!")
        
        # Obtener resumen
        resumen = validator.obtener_resumen_rentabilidad()
        print(f"\n📊 Resumen de Rentabilidades:")
        print(f"  - Total de reglas: {resumen['total_reglas']}")
        print(f"  - Archivo: {resumen.get('archivo', 'N/A')}")
        
        # Mostrar reglas por marca
        print(f"\n🏷️ Reglas por Marca:")
        for marca, count in resumen.get('por_marca', {}).items():
            print(f"  - {marca}: {count} reglas")
        
        # Mostrar reglas por canal
        print(f"\n🛒 Reglas por Canal:")
        for canal, count in resumen.get('por_canal', {}).items():
            print(f"  - {canal}: {count} reglas")
        
        # Probar validación de productos
        print(f"\n🔍 Probando validación de productos...")
        
        productos_test = [
            {
                'marca': 'Moura',
                'canal': 'Minorista',
                'linea': 'Estándar',
                'margen': 25.0
            },
            {
                'marca': 'Moura',
                'canal': 'Minorista',
                'linea': 'EFB',
                'margen': 35.0
            },
            {
                'marca': 'Acubat',
                'canal': 'Minorista',
                'linea': 'Estándar',
                'margen': 30.0
            }
        ]
        
        for producto in productos_test:
            estado, margen_min, margen_opt = validator.evaluar_rentabilidad(
                producto['marca'], 
                producto['canal'], 
                producto['linea'], 
                producto['margen']
            )
            
            print(f"  📦 {producto['marca']} - {producto['canal']} - {producto['linea']}:")
            print(f"     Margen actual: {producto['margen']:.1f}%")
            print(f"     Margen esperado: {margen_min:.1f}% - {margen_opt:.1f}%")
            print(f"     Estado: {estado}")
        
        return validator
        
    except Exception as e:
        print(f"❌ Error al probar rentabilidades: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_rentabilidades() 