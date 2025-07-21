#!/usr/bin/env python3
"""
Diagnóstico completo final
"""

import requests
import json

def diagnostico_completo():
    print("🔍 DIAGNÓSTICO COMPLETO FINAL")
    print("=" * 60)
    
    base_url = "https://acubat.vercel.app"
    
    # 1. Verificar qué archivos están cargados
    print("\n1️⃣ ARCHIVOS CARGADOS:")
    try:
        response = requests.get(f"{base_url}/api/diagnostico-detallado")
        if response.status_code == 200:
            data = response.json()
            
            precios = data.get('precios', {})
            if precios.get('cargado'):
                print(f"   📁 Archivo de precios: {precios.get('archivo', 'No especificado')}")
                print(f"   📊 Total productos: {precios.get('total_productos', 0)}")
                print(f"   📋 Hojas: {precios.get('hojas', [])}")
                
                # Verificar si tiene productos Moura
                datos_ejemplo = precios.get('datos_ejemplo', [])
                if datos_ejemplo:
                    print(f"   📋 EJEMPLO DE PRODUCTOS:")
                    for i, producto in enumerate(datos_ejemplo[:3]):
                        codigo = producto.get('CODIGO BATERIAS', '')
                        precio = producto.get('Precio de Lista', 0)
                        print(f"   Producto {i+1}: {codigo} - ${precio}")
            else:
                print("   ❌ No hay archivo de precios cargado")
            
            rentabilidades = data.get('rentabilidades', {})
            if rentabilidades.get('cargado'):
                print(f"   📁 Archivo de rentabilidades: {rentabilidades.get('archivo', 'No especificado')}")
                print(f"   📊 Total reglas: {rentabilidades.get('total_reglas', 0)}")
                print(f"   📋 Hojas: {rentabilidades.get('hojas', [])}")
                
                # Verificar si tiene hoja Moura
                hojas = rentabilidades.get('hojas', [])
                if 'Moura' in hojas:
                    print("   ✅ TIENE HOJA 'Moura'")
                else:
                    print("   ❌ NO TIENE HOJA 'Moura'")
            else:
                print("   ❌ No hay archivo de rentabilidades cargado")
                
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Intentar calcular precios y ver la respuesta completa
    print("\n2️⃣ CALCULAR PRECIOS - RESPUESTA COMPLETA:")
    try:
        response = requests.post(f"{base_url}/calcular-precios-con-rentabilidad")
        if response.status_code == 200:
            resultado = response.json()
            print(f"   ✅ Status: {resultado.get('status')}")
            print(f"   📊 Productos procesados: {resultado.get('productos', 0)}")
            print(f"   📄 Mensaje: {resultado.get('mensaje', 'No especificado')}")
            
            # Verificar si tiene productos_detalle
            productos_detalle = resultado.get('productos_detalle', [])
            print(f"   📋 Productos detalle: {len(productos_detalle)} elementos")
            
            if productos_detalle:
                print(f"   📋 PRIMEROS 3 PRODUCTOS:")
                for i, producto in enumerate(productos_detalle[:3]):
                    print(f"   Producto {i+1}:")
                    print(f"     Código: {producto.get('codigo', 'N/A')}")
                    print(f"     Nombre: {producto.get('nombre', 'N/A')}")
                    print(f"     Precio Base: ${producto.get('precio_base', 0)}")
                    print(f"     Precio Final: ${producto.get('precio_final', 0)}")
                    print(f"     Margen: {producto.get('margen', 0)}%")
                    print(f"     Estado: {producto.get('estado', 'N/A')}")
                    print(f"     Alertas: {producto.get('alertas', [])}")
            else:
                print("   ❌ NO HAY PRODUCTOS_DETALLE")
            
            # Verificar resumen
            resumen = resultado.get('resumen', {})
            print(f"   📊 RESUMEN:")
            print(f"     Total productos: {resumen.get('total_productos', 0)}")
            print(f"     Con alertas: {resumen.get('con_alertas', 0)}")
            print(f"     Margen promedio: {resumen.get('margen_promedio', 0)}%")
            
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📄 Respuesta: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Verificar logs del servidor
    print("\n3️⃣ LOGS DEL SERVIDOR:")
    try:
        response = requests.get(f"{base_url}/api/logs")
        if response.status_code == 200:
            logs = response.json()
            if 'logs' in logs:
                print("   📋 ÚLTIMOS LOGS:")
                for log in logs['logs'][-10:]:  # Últimos 10 logs
                    print(f"     {log}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 DIAGNÓSTICO COMPLETADO")
    print("\n💡 ANÁLISIS:")
    print("1. Si productos_detalle está vacío, el backend no está devolviendo los productos")
    print("2. Si productos_detalle tiene datos pero no se muestra, es problema del frontend")
    print("3. Si el estado de rentabilidad está en 0, las reglas no se están aplicando correctamente")

if __name__ == "__main__":
    diagnostico_completo() 