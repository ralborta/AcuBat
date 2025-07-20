#!/usr/bin/env python3
"""
Script de diagnóstico para probar el endpoint de cálculo de precios
"""

import requests
import json
import time

def test_calculo():
    base_url = "http://localhost:8000"
    
    print("🔍 DIAGNÓSTICO DE CÁLCULO DE PRECIOS")
    print("=" * 50)
    
    # 1. Verificar estado inicial
    print("\n1️⃣ Verificando estado inicial...")
    try:
        response = requests.get(f"{base_url}/api/estado-archivos")
        estado = response.json()
        print(f"   Estado: {estado}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 2. Simular carga de archivos (si no están cargados)
    if not estado.get('precios_cargados'):
        print("\n2️⃣ Cargando archivo de precios de prueba...")
        # Crear archivo de prueba
        import pandas as pd
        import tempfile
        import os
        
        # Crear datos de prueba
        precios_test = [
            {'codigo': 'M40FD', 'nombre': 'Batería Moura 40Ah', 'precio': 150000},
            {'codigo': 'M18FD', 'nombre': 'Batería Moura 18Ah', 'precio': 80000},
            {'codigo': 'M60FD', 'nombre': 'Batería Moura 60Ah', 'precio': 220000}
        ]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            df = pd.DataFrame(precios_test)
            df.to_excel(temp_file.name, index=False)
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('precios_test.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = requests.post(f"{base_url}/cargar-precios", files=files)
                print(f"   Respuesta: {response.json()}")
        finally:
            os.unlink(temp_file_path)
    
    if not estado.get('rentabilidades_cargadas'):
        print("\n3️⃣ Cargando archivo de rentabilidades de prueba...")
        # Crear datos de rentabilidad de prueba
        rentabilidades_test = [
            {'codigo': 'M40FD', 'markup': 25, 'margen_minimo': 15, 'margen_optimo': 30},
            {'codigo': 'M18FD', 'markup': 20, 'margen_minimo': 12, 'margen_optimo': 25},
            {'codigo': 'M60FD', 'markup': 30, 'margen_minimo': 18, 'margen_optimo': 35}
        ]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            df = pd.DataFrame(rentabilidades_test)
            df.to_excel(temp_file.name, index=False)
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('rentabilidades_test.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = requests.post(f"{base_url}/cargar-rentabilidades", files=files)
                print(f"   Respuesta: {response.json()}")
        finally:
            os.unlink(temp_file_path)
    
    # 3. Verificar estado después de carga
    print("\n4️⃣ Verificando estado después de carga...")
    time.sleep(2)
    try:
        response = requests.get(f"{base_url}/api/estado-archivos")
        estado = response.json()
        print(f"   Estado: {estado}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 4. Intentar cálculo
    print("\n5️⃣ Intentando cálculo de precios...")
    try:
        response = requests.post(f"{base_url}/calcular-precios-con-rentabilidad")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"   ✅ Éxito: {resultado}")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Detalle: {error_detail}")
            except:
                print(f"   Texto: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    test_calculo() 