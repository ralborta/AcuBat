#!/usr/bin/env python3
"""
Diagnóstico específico para el archivo actual del usuario
"""

import requests
import json

def diagnostico_archivo_actual():
    print("🔍 DIAGNÓSTICO DEL ARCHIVO ACTUAL")
    print("=" * 50)
    
    base_url = "https://acubat.vercel.app"
    
    # 1. Verificar qué archivo está cargado
    print("\n1️⃣ ARCHIVO CARGADO:")
    try:
        response = requests.get(f"{base_url}/api/diagnostico-detallado")
        if response.status_code == 200:
            data = response.json()
            
            precios = data.get('precios', {})
            if precios.get('cargado'):
                print(f"   📁 Archivo: {precios.get('archivo', 'No especificado')}")
                print(f"   📊 Total productos: {precios.get('total_productos', 0)}")
                print(f"   📋 Hojas disponibles: {precios.get('hojas', [])}")
                
                # Mostrar ejemplo de datos
                datos_ejemplo = precios.get('datos_ejemplo', [])
                if datos_ejemplo:
                    print(f"\n   📋 EJEMPLO DE PRODUCTOS:")
                    for i, producto in enumerate(datos_ejemplo[:3]):
                        print(f"   Producto {i+1}:")
                        for key, value in producto.items():
                            print(f"     {key}: {value}")
            else:
                print("   ❌ No hay archivo de precios cargado")
                
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Verificar reglas de rentabilidad
    print("\n2️⃣ REGLAS DE RENTABILIDAD:")
    try:
        response = requests.get(f"{base_url}/api/diagnostico-detallado")
        if response.status_code == 200:
            data = response.json()
            
            rentabilidades = data.get('rentabilidades', {})
            if rentabilidades.get('cargado'):
                print(f"   📁 Archivo: {rentabilidades.get('archivo', 'No especificado')}")
                print(f"   📊 Total reglas: {rentabilidades.get('total_reglas', 0)}")
                
                # Mostrar ejemplo de reglas Moura
                datos_ejemplo = rentabilidades.get('datos_ejemplo', [])
                if datos_ejemplo:
                    print(f"\n   📋 EJEMPLO DE REGLAS:")
                    for i, regla in enumerate(datos_ejemplo[:3]):
                        print(f"   Regla {i+1}:")
                        for key, value in regla.items():
                            print(f"     {key}: {value}")
            else:
                print("   ❌ No hay archivo de rentabilidades cargado")
                
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Intentar procesar y ver qué pasa
    print("\n3️⃣ INTENTAR PROCESAR:")
    try:
        response = requests.post(f"{base_url}/calcular-precios-con-rentabilidad")
        if response.status_code == 200:
            resultado = response.json()
            print(f"   ✅ Status: {resultado.get('status')}")
            print(f"   📊 Productos procesados: {resultado.get('productos', 0)}")
            print(f"   📄 Mensaje: {resultado.get('mensaje', 'No especificado')}")
            
            if resultado.get('productos', 0) == 0:
                print(f"\n   🚨 PROBLEMA: 0 productos procesados")
                print(f"   💡 Posibles causas:")
                print(f"      - No hay coincidencia entre códigos de productos y reglas")
                print(f"      - El archivo no tiene la estructura esperada")
                print(f"      - Las hojas no se están leyendo correctamente")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📄 Respuesta: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 DIAGNÓSTICO COMPLETADO")
    print("\n💡 PRÓXIMOS PASOS:")
    print("1. Revisar si los códigos de productos coinciden con las reglas")
    print("2. Verificar la estructura del archivo de precios")
    print("3. Ajustar el código si es necesario")

if __name__ == "__main__":
    diagnostico_archivo_actual() 