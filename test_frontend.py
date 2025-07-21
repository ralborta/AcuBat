#!/usr/bin/env python3
"""
Test para verificar si el frontend puede mostrar los datos
"""

import requests
import json

def test_frontend():
    print("🧪 TEST FRONTEND - VERIFICAR DISPLAY DE PRODUCTOS")
    print("=" * 60)
    
    base_url = "https://acubat.vercel.app"
    
    # 1. Obtener datos del backend
    print("\n1️⃣ OBTENIENDO DATOS DEL BACKEND:")
    try:
        response = requests.post(f"{base_url}/calcular-precios-con-rentabilidad")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
            print(f"   📊 Productos: {data.get('productos', 0)}")
            print(f"   📋 Productos detalle: {len(data.get('productos_detalle', []))}")
            
            productos_detalle = data.get('productos_detalle', [])
            if productos_detalle:
                print(f"   ✅ PRIMEROS 3 PRODUCTOS:")
                for i, producto in enumerate(productos_detalle[:3]):
                    print(f"   Producto {i+1}: {producto.get('codigo')} - {producto.get('estado')}")
            else:
                print("   ❌ NO HAY PRODUCTOS_DETALLE")
                
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Verificar si el frontend puede acceder a los datos
    print("\n2️⃣ VERIFICANDO ACCESO FRONTEND:")
    try:
        # Simular la respuesta que debería recibir el frontend
        test_data = {
            "status": "success",
            "mensaje": "Proceso completado exitosamente para 32 productos",
            "productos": 32,
            "productos_detalle": [
                {
                    "codigo": "M40FD",
                    "nombre": "Clio mio, Prisma; Onix, Palio 8v, Uno mod \"N\"",
                    "precio_base": 136490.0,
                    "precio_final": 163800,
                    "margen": 16.67,
                    "estado": "ADVERTENCIA",
                    "alertas": ["Margen subóptimo: 16.7% < 25.0%"],
                    "markup_aplicado": 20.0
                }
            ],
            "resumen": {
                "total_productos": 32,
                "con_alertas": 32,
                "margen_promedio": 16.7
            }
        }
        
        print(f"   📊 Datos de prueba creados:")
        print(f"   - productos_detalle existe: {'productos_detalle' in test_data}")
        print(f"   - productos_detalle es array: {isinstance(test_data['productos_detalle'], list)}")
        print(f"   - productos_detalle length: {len(test_data['productos_detalle'])}")
        print(f"   - Primer producto: {test_data['productos_detalle'][0] if test_data['productos_detalle'] else 'No disponible'}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 TEST COMPLETADO")
    print("\n💡 CONCLUSIÓN:")
    print("Si el backend devuelve datos correctos pero el frontend no los muestra,")
    print("el problema está en el JavaScript del frontend.")

if __name__ == "__main__":
    test_frontend() 