#!/usr/bin/env python3
"""
Script de prueba para la demo de AcuBat
Verifica que todas las funcionalidades estén funcionando
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
DEMO_TENANT_ID = "demo-tenant-001"
DEMO_LIST_ID = "demo-list-001"
DEMO_RULESET_ID = "demo-ruleset-001"

def test_health():
    """Prueba el health check"""
    print("🔍 Probando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check OK - DB: {data.get('database', 'unknown')}")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return False

def test_demo_data():
    """Prueba el endpoint de datos de demo"""
    print("\n🔍 Probando datos de demo...")
    try:
        response = requests.get(f"{BASE_URL}/demo/data")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Datos de demo disponibles:")
            print(f"   - Tenant: {data.get('tenant_id')}")
            print(f"   - Lista: {data.get('list_id')}")
            print(f"   - Ruleset: {data.get('ruleset_id')}")
            print(f"   - Productos: {len(data.get('products', []))}")
            return True
        else:
            print(f"❌ Datos de demo fallaron: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en datos de demo: {e}")
        return False

def test_simulation():
    """Prueba la simulación de pricing"""
    print("\n🔍 Probando simulación...")
    try:
        payload = {
            "tenant_id": DEMO_TENANT_ID,
            "list_id": DEMO_LIST_ID,
            "ruleset_id": DEMO_RULESET_ID
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/simulate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Simulación exitosa:")
            print(f"   - Run ID: {data.get('id')}")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Resumen: {data.get('summary', {})}")
            return data.get('id')
        else:
            print(f"❌ Simulación falló: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
        return None

def test_run_details(run_id):
    """Prueba obtener detalles del run"""
    print(f"\n🔍 Probando detalles del run {run_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/runs/{run_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Detalles del run obtenidos:")
            print(f"   - Items: {len(data.get('items', []))}")
            print(f"   - Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Detalles del run fallaron: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en detalles del run: {e}")
        return False

def test_publish(run_id):
    """Prueba la publicación"""
    print(f"\n🔍 Probando publicación del run {run_id}...")
    try:
        payload = {
            "run_id": run_id,
            "canal": "web"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/publish",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Publicación exitosa:")
            print(f"   - Publish ID: {data.get('id')}")
            print(f"   - Canal: {data.get('canal')}")
            return True
        else:
            print(f"❌ Publicación falló: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en publicación: {e}")
        return False

def test_tenant_data():
    """Prueba obtener datos del tenant"""
    print("\n🔍 Probando datos del tenant...")
    try:
        # Probar uploads del tenant
        response = requests.get(f"{BASE_URL}/api/v1/upload/tenant/{DEMO_TENANT_ID}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Uploads del tenant: {len(data)} archivos")
        
        # Probar simulaciones del tenant
        response = requests.get(f"{BASE_URL}/api/v1/simulate/tenant/{DEMO_TENANT_ID}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Simulaciones del tenant: {len(data)} ejecuciones")
        
        return True
    except Exception as e:
        print(f"❌ Error en datos del tenant: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de la demo de AcuBat")
    print("=" * 50)
    
    # Verificar que la app esté corriendo
    if not test_health():
        print("\n❌ La aplicación no está corriendo o hay problemas")
        return
    
    # Probar datos de demo
    if not test_demo_data():
        print("\n❌ Problemas con los datos de demo")
        return
    
    # Probar simulación
    run_id = test_simulation()
    if not run_id:
        print("\n❌ La simulación falló")
        return
    
    # Probar detalles del run
    test_run_details(run_id)
    
    # Probar publicación
    test_publish(run_id)
    
    # Probar datos del tenant
    test_tenant_data()
    
    print("\n" + "=" * 50)
    print("🎉 ¡Todas las pruebas completadas!")
    print("✅ Tu demo está funcionando correctamente")
    print(f"🌐 Puedes acceder a la documentación en: {BASE_URL}/docs")

if __name__ == "__main__":
    main()
