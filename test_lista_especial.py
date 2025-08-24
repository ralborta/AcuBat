#!/usr/bin/env python3
"""
Script de prueba para la funcionalidad de listas específicas
"""
import sys
import os
sys.path.append('api')

from api.logic import PricingLogic
from api.models import Producto, Marca, Canal

def test_lista_especial():
    """Prueba la funcionalidad de lista especial"""
    print("🧪 PRUEBA DE LISTA ESPECIAL")
    print("=" * 50)
    
    # Crear instancia de PricingLogic
    pricing_logic = PricingLogic()
    
    # Verificar estado inicial
    print(f"📊 Estado inicial:")
    print(f"   - Rentabilidades cargadas: {pricing_logic.rentabilidades_cargadas}")
    print(f"   - Cache de precios: {len(pricing_logic.precios_minorista_cache)} items")
    
    # Simular carga de rentabilidades
    print(f"\n📁 Intentando cargar rentabilidades...")
    try:
        # Buscar archivo de rentabilidades
        archivos_posibles = [
            'Rentalibilidades-2.xlsx',
            'data_files/Rentalibilidades-2.xlsx',
            '../Rentalibilidades-2.xlsx'
        ]
        
        archivo_encontrado = None
        for archivo in archivos_posibles:
            if os.path.exists(archivo):
                archivo_encontrado = archivo
                break
        
        if archivo_encontrado:
            pricing_logic.cargar_listas_especificas(archivo_encontrado)
            print(f"✅ Rentabilidades cargadas desde: {archivo_encontrado}")
        else:
            print("⚠️ No se encontró archivo de rentabilidades, simulando datos...")
            # Simular datos para prueba
            pricing_logic.rentabilidades_data = {
                'reglas_minorista': [
                    {
                        'codigo': '32-87',
                        'precio_base': 50000,
                        'markup': 85.5,
                        'canal': 'Minorista'
                    },
                    {
                        'codigo': 'M20GD',
                        'precio_base': 35000,
                        'markup': 90.2,
                        'canal': 'Minorista'
                    }
                ]
            }
            pricing_logic.rentabilidades_cargadas = True
            print("✅ Datos simulados cargados")
    
    except Exception as e:
        print(f"❌ Error cargando rentabilidades: {e}")
    
    # Probar productos de ejemplo
    productos_prueba = [
        Producto(
            codigo="32-87",
            nombre="Batería Moura 32-87",
            marca=Marca.MOURA,
            canal=Canal.MINORISTA,
            precio_base=50000.0,
            precio_final=0.0
        ),
        Producto(
            codigo="M20GD",
            nombre="Batería Moura M20GD",
            marca=Marca.MOURA,
            canal=Canal.MINORISTA,
            precio_base=35000.0,
            precio_final=0.0
        ),
        Producto(
            codigo="XXX123",
            nombre="Batería No Existente",
            marca=Marca.MOURA,
            canal=Canal.MINORISTA,
            precio_base=40000.0,
            precio_final=0.0
        )
    ]
    
    print(f"\n🧪 Probando aplicación de markups...")
    
    for i, producto in enumerate(productos_prueba, 1):
        print(f"\n--- Producto {i}: {producto.codigo} ---")
        print(f"Precio base: ${producto.precio_base:,.0f}")
        
        # Probar función directa
        precio_especial = pricing_logic._obtener_precio_lista_especial(
            producto.codigo, 
            producto.marca.value, 
            producto.canal.value
        )
        
        if precio_especial:
            print(f"✅ Precio lista especial: ${precio_especial:,.0f}")
            markup_real = (precio_especial - producto.precio_base) / producto.precio_base * 100
            print(f"   Markup aplicado: {markup_real:.1f}%")
        else:
            print(f"❌ No se encontró precio en lista especial")
    
    # Probar procesamiento completo
    print(f"\n🚀 Probando procesamiento completo...")
    try:
        resultado = pricing_logic.aplicar_markups_dinamicos(productos_prueba)
        
        print(f"\n📊 RESULTADOS:")
        for producto in resultado:
            print(f"- {producto.codigo}: ${producto.precio_final:,.0f} (markup: {producto.markup_aplicado:.1f}%)")
    
    except Exception as e:
        print(f"❌ Error en procesamiento: {e}")
    
    # Mostrar estado del cache
    print(f"\n📝 Estado final del cache: {len(pricing_logic.precios_minorista_cache)} items")
    for key, value in pricing_logic.precios_minorista_cache.items():
        print(f"   {key}: ${value:,.0f}")
    
    print(f"\n✅ Prueba completada")

if __name__ == "__main__":
    test_lista_especial()