#!/usr/bin/env python3
"""
Script de prueba para la Fase 2 - Sistema de Pricing por Canal
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.models import Producto, Marca, Canal
from api.logic import PricingLogic
from api.openai_helper import OpenAIHelper

def test_pricing_logic():
    """Prueba la lógica de pricing"""
    print("🧪 Probando lógica de pricing...")
    
    # Crear instancia de pricing logic
    pricing = PricingLogic()
    
    # Crear productos de prueba
    productos_prueba = [
        Producto(
            codigo="TEST001",
            nombre="Batería 60Ah Moura",
            marca=Marca.MOURA,
            canal=Canal.MINORISTA,
            precio_base=120.50,
            precio_final=0,  # Se calculará
            margen=0  # Se calculará
        ),
        Producto(
            codigo="TEST002",
            nombre="Batería 80Ah Acubat",
            marca=Marca.ACUBAT,
            canal=Canal.MAYORISTA,
            precio_base=160.00,
            precio_final=0,  # Se calculará
            margen=0  # Se calculará
        ),
        Producto(
            codigo="TEST003",
            nombre="Batería 100Ah Lubeck",
            marca=Marca.LUBECK,
            canal=Canal.DISTRIBUIDOR,
            precio_base=190.00,
            precio_final=0,  # Se calculará
            margen=0  # Se calculará
        )
    ]
    
    # Aplicar pricing
    productos_procesados = pricing.procesar_productos(productos_prueba)
    
    print(f"✅ Procesados {len(productos_procesados)} productos")
    
    for producto in productos_procesados:
        print(f"  📦 {producto.codigo}:")
        print(f"     Precio base: ${producto.precio_base:.2f}")
        print(f"     Precio final: ${producto.precio_final:.2f}")
        print(f"     Markup: {producto.markup_aplicado:.1f}%")
        print(f"     Margen: {producto.margen:.1f}%")
        print(f"     Alertas: {producto.alertas}")
        print()
    
    return productos_procesados

def test_openai_helper():
    """Prueba el helper de OpenAI"""
    print("🤖 Probando OpenAI Helper...")
    
    openai_helper = OpenAIHelper()
    
    if openai_helper.esta_disponible():
        print("✅ OpenAI está disponible")
        
        # Crear un producto de prueba
        producto_prueba = Producto(
            codigo="AI_TEST",
            nombre="Batería de prueba para IA",
            marca=Marca.MOURA,
            canal=Canal.MINORISTA,
            precio_base=100.00,
            precio_final=135.00,
            margen=35.0,
            alertas=[]
        )
        
        # Analizar con IA
        sugerencia = openai_helper.analizar_producto(producto_prueba)
        if sugerencia:
            print(f"✅ Sugerencia IA: {sugerencia}")
        else:
            print("❌ No se obtuvo sugerencia de IA")
    else:
        print("⚠️ OpenAI no está disponible (verificar OPENAI_API_KEY)")
    
    print()

def test_export_csv():
    """Prueba la exportación a CSV"""
    print("📄 Probando exportación CSV...")
    
    pricing = PricingLogic()
    
    # Crear productos de prueba
    productos_prueba = [
        Producto(
            codigo="CSV001",
            nombre="Producto CSV 1",
            marca=Marca.MOURA,
            canal=Canal.MINORISTA,
            precio_base=100.00,
            precio_final=135.00,
            margen=35.0,
            alertas=[]
        ),
        Producto(
            codigo="CSV002",
            nombre="Producto CSV 2",
            marca=Marca.ACUBAT,
            canal=Canal.MAYORISTA,
            precio_base=150.00,
            precio_final=187.50,
            margen=25.0,
            alertas=[]
        )
    ]
    
    # Exportar a CSV
    csv_content = pricing.exportar_a_csv(productos_prueba)
    
    print("✅ CSV generado:")
    print(csv_content)
    print()

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de la Fase 2 - Sistema de Pricing")
    print("=" * 60)
    
    try:
        # Probar lógica de pricing
        productos = test_pricing_logic()
        
        # Probar OpenAI helper
        test_openai_helper()
        
        # Probar exportación CSV
        test_export_csv()
        
        print("✅ Todas las pruebas completadas exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 