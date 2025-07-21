#!/usr/bin/env python3
"""
Verificar la estructura real de las reglas de rentabilidad
"""

import requests
import json

def verificar_reglas():
    print("🔍 VERIFICANDO ESTRUCTURA DE REGLAS DE RENTABILIDAD")
    print("=" * 60)
    
    base_url = "https://acubat.vercel.app"
    
    # Obtener diagnóstico detallado
    try:
        response = requests.get(f"{base_url}/api/diagnostico-detallado")
        if response.status_code == 200:
            data = response.json()
            
            rentabilidades = data.get('rentabilidades', {})
            if rentabilidades.get('cargado'):
                print(f"📁 Archivo: {rentabilidades.get('archivo', 'No especificado')}")
                print(f"📊 Total reglas: {rentabilidades.get('total_reglas', 0)}")
                
                # Verificar hojas disponibles
                hojas = rentabilidades.get('hojas', [])
                print(f"📋 Hojas disponibles: {hojas}")
                
                # Buscar hoja Moura
                if 'Moura' in hojas:
                    print("✅ HOJA 'Moura' ENCONTRADA")
                    
                    # Obtener datos de ejemplo
                    datos_ejemplo = rentabilidades.get('datos_ejemplo', [])
                    if datos_ejemplo:
                        print(f"\n📋 ESTRUCTURA DE REGLAS (primeras 3):")
                        for i, regla in enumerate(datos_ejemplo[:3]):
                            print(f"\nRegla {i+1}:")
                            print(f"  Columnas disponibles: {list(regla.keys())}")
                            print(f"  Valores:")
                            for key, value in regla.items():
                                if str(value) != 'nan' and value is not None:
                                    print(f"    {key}: {value}")
                else:
                    print("❌ NO SE ENCONTRÓ HOJA 'Moura'")
                    
            else:
                print("❌ No hay archivo de rentabilidades cargado")
                
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 VERIFICACIÓN COMPLETADA")

if __name__ == "__main__":
    verificar_reglas() 