#!/usr/bin/env python3
"""
Script para diagnosticar el backend y ver exactamente qué está devolviendo
"""

import requests
import json
import pandas as pd
import tempfile
import os

def debug_backend():
    base_url = "https://acubat.vercel.app"  # Ajusta esta URL
    
    print("🔍 DIAGNÓSTICO DETALLADO DEL BACKEND")
    print("=" * 60)
    
    # 1. Crear archivos de prueba
    print("\n1️⃣ Creando archivos de prueba...")
    
    # Archivo de precios de prueba
    precios_test = [
        {'codigo': 'M40FD', 'nombre': 'Batería Moura 40Ah', 'precio': 150000},
        {'codigo': 'M18FD', 'nombre': 'Batería Moura 18Ah', 'precio': 80000},
        {'codigo': 'M60FD', 'nombre': 'Batería Moura 60Ah', 'precio': 220000}
    ]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
        df = pd.DataFrame(precios_test)
        df.to_excel(temp_file.name, index=False)
        precios_path = temp_file.name
    
    # Archivo de rentabilidades de prueba
    rentabilidades_test = [
        {'codigo': 'M40FD', 'markup': 25, 'margen_minimo': 15, 'margen_optimo': 30},
        {'codigo': 'M18FD', 'markup': 20, 'margen_minimo': 12, 'margen_optimo': 25},
        {'codigo': 'M60FD', 'markup': 30, 'margen_minimo': 18, 'margen_optimo': 35}
    ]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
        df = pd.DataFrame(rentabilidades_test)
        df.to_excel(temp_file.name, index=False)
        rentabilidades_path = temp_file.name
    
    try:
        # 2. Subir archivo de precios
        print("\n2️⃣ Subiendo archivo de precios...")
        with open(precios_path, 'rb') as f:
            files = {'file': ('precios_test.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{base_url}/cargar-precios", files=files)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Respuesta: {data}")
            else:
                print(f"   Error: {response.text}")
        
        # 3. Subir archivo de rentabilidades
        print("\n3️⃣ Subiendo archivo de rentabilidades...")
        with open(rentabilidades_path, 'rb') as f:
            files = {'file': ('rentabilidades_test.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{base_url}/cargar-rentabilidades", files=files)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Respuesta: {data}")
            else:
                print(f"   Error: {response.text}")
        
        # 4. Verificar estado
        print("\n4️⃣ Verificando estado...")
        response = requests.get(f"{base_url}/api/estado-archivos")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            estado = response.json()
            print(f"   Estado: {estado}")
        else:
            print(f"   Error: {response.text}")
        
        # 5. Ejecutar cálculo
        print("\n5️⃣ Ejecutando cálculo...")
        response = requests.post(f"{base_url}/calcular-precios-con-rentabilidad")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"   ✅ RESULTADO COMPLETO:")
            print(f"   Status: {resultado.get('status')}")
            print(f"   Mensaje: {resultado.get('mensaje')}")
            print(f"   Productos: {resultado.get('productos')}")
            print(f"   Pasos completados: {resultado.get('pasos_completados')}")
            print(f"   Resumen: {resultado.get('resumen')}")
            
            # Análisis detallado
            print(f"\n   📊 ANÁLISIS DETALLADO:")
            print(f"   - Total productos en respuesta: {resultado.get('productos', 'NO ENCONTRADO')}")
            print(f"   - Total productos en resumen: {resultado.get('resumen', {}).get('total_productos', 'NO ENCONTRADO')}")
            print(f"   - Con alertas: {resultado.get('resumen', {}).get('con_alertas', 'NO ENCONTRADO')}")
            print(f"   - Margen promedio: {resultado.get('resumen', {}).get('margen_promedio', 'NO ENCONTRADO')}")
            
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Detalle: {error_detail}")
            except:
                print(f"   Texto: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    finally:
        # Limpiar archivos temporales
        if os.path.exists(precios_path):
            os.unlink(precios_path)
        if os.path.exists(rentabilidades_path):
            os.unlink(rentabilidades_path)
    
    print("\n" + "=" * 60)
    print("🏁 DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    debug_backend() 