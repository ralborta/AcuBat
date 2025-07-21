#!/usr/bin/env python3
"""
Diagnóstico completo del backend para identificar el problema
"""

import requests
import json
import pandas as pd
import tempfile
import os

def diagnostico_completo():
    base_url = "https://acubat.vercel.app"
    
    print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA")
    print("=" * 60)
    
    # 1. Crear archivo de precios Moura real
    print("\n1️⃣ Creando archivo de precios Moura...")
    
    precios_moura = [
        {'codigo': 'M40FD', 'nombre': 'Batería Moura 40Ah', 'precio_base': 150000, 'marca': 'Moura', 'canal': 'minorista'},
        {'codigo': 'M18FD', 'nombre': 'Batería Moura 18Ah', 'precio_base': 80000, 'marca': 'Moura', 'canal': 'minorista'},
        {'codigo': 'M22ED', 'nombre': 'Batería Moura 22Ah', 'precio_base': 100000, 'marca': 'Moura', 'canal': 'minorista'},
        {'codigo': 'M20GD', 'nombre': 'Batería Moura 20Ah', 'precio_base': 90000, 'marca': 'Moura', 'canal': 'minorista'},
        {'codigo': 'M22GD', 'nombre': 'Batería Moura 22Ah GD', 'precio_base': 110000, 'marca': 'Moura', 'canal': 'minorista'}
    ]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
        df = pd.DataFrame(precios_moura)
        df.to_excel(temp_file.name, index=False)
        precios_path = temp_file.name
    
    # 2. Crear archivo de rentabilidades Moura
    print("\n2️⃣ Creando archivo de rentabilidades Moura...")
    
    rentabilidades_moura = [
        {'codigo': 'M40FD', 'markup': 25, 'margen_minimo': 15, 'margen_optimo': 30},
        {'codigo': 'M18FD', 'markup': 20, 'margen_minimo': 12, 'margen_optimo': 25},
        {'codigo': 'M22ED', 'markup': 22, 'margen_minimo': 14, 'margen_optimo': 28},
        {'codigo': 'M20GD', 'markup': 21, 'margen_minimo': 13, 'margen_optimo': 27},
        {'codigo': 'M22GD', 'markup': 23, 'margen_minimo': 15, 'margen_optimo': 29}
    ]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
        df = pd.DataFrame(rentabilidades_moura)
        df.to_excel(temp_file.name, index=False)
        rentabilidades_path = temp_file.name
    
    try:
        # 3. Subir archivo de precios
        print("\n3️⃣ Subiendo archivo de precios...")
        with open(precios_path, 'rb') as f:
            files = {'file': ('precios_moura.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{base_url}/cargar-precios", files=files)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Respuesta: {data}")
            else:
                print(f"   Error: {response.text}")
        
        # 4. Subir archivo de rentabilidades
        print("\n4️⃣ Subiendo archivo de rentabilidades...")
        with open(rentabilidades_path, 'rb') as f:
            files = {'file': ('rentabilidades_moura.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{base_url}/cargar-rentabilidades", files=files)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Respuesta: {data}")
            else:
                print(f"   Error: {response.text}")
        
        # 5. Verificar estado
        print("\n5️⃣ Verificando estado...")
        response = requests.get(f"{base_url}/api/estado-archivos")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            estado = response.json()
            print(f"   Estado: {estado}")
        else:
            print(f"   Error: {response.text}")
        
        # 6. Ejecutar cálculo
        print("\n6️⃣ Ejecutando cálculo...")
        response = requests.post(f"{base_url}/calcular-precios-con-rentabilidad")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"\n   ✅ RESULTADO COMPLETO:")
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
            
            # Verificar estructura de datos
            print(f"\n   🔍 VERIFICACIÓN DE ESTRUCTURA:")
            print(f"   - Tipo de 'productos': {type(resultado.get('productos'))}")
            print(f"   - Tipo de 'resumen': {type(resultado.get('resumen'))}")
            if resultado.get('resumen'):
                print(f"   - Claves en resumen: {list(resultado.get('resumen').keys())}")
            
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
    diagnostico_completo() 