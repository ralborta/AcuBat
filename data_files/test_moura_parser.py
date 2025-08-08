#!/usr/bin/env python3
"""
Script de prueba para el parser de MOURA
"""

import os
import sys
import pandas as pd

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_moura_parser():
    """Prueba el parser de MOURA"""
    
    print("🧪 Probando Parser de MOURA...")
    
    # Buscar archivos MOURA en el directorio data
    data_dir = "data"
    moura_files = []
    
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.lower().endswith(('.xlsx', '.xls')):
                file_path = os.path.join(data_dir, file)
                print(f"📁 Encontrado archivo: {file}")
                
                # Verificar si es un archivo MOURA
                try:
                    from api.parser import is_moura_file
                    if is_moura_file(file_path):
                        moura_files.append(file_path)
                        print(f"✅ Archivo MOURA detectado: {file}")
                    else:
                        print(f"❌ No es archivo MOURA: {file}")
                except Exception as e:
                    print(f"⚠️ Error al verificar {file}: {e}")
    
    if not moura_files:
        print("❌ No se encontraron archivos MOURA para probar")
        print("💡 Copia tu archivo 'Lista Moura 04 (1).xlsx' a la carpeta 'data/'")
        return
    
    # Probar con el primer archivo MOURA encontrado
    test_file = moura_files[0]
    print(f"\n🎯 Probando con: {test_file}")
    
    try:
        from api.moura_parser import parse_moura_file
        
        # Parsear archivo
        productos = parse_moura_file(test_file)
        
        print(f"\n✅ Parser exitoso!")
        print(f"📊 Productos extraídos: {len(productos)}")
        
        if productos:
            print("\n📋 Primeros 5 productos:")
            for i, producto in enumerate(productos[:5]):
                print(f"  {i+1}. {producto['codigo']} - ${producto['precio_final']:,.0f} - {producto['margen']:.1f}% - {producto['estado']}")
        
        # Estadísticas
        precios_validos = [p for p in productos if p['precio_final']]
        margenes_validos = [p for p in productos if p['margen']]
        
        print(f"\n📈 Estadísticas:")
        print(f"  - Productos con precio válido: {len(precios_validos)}")
        print(f"  - Productos con margen válido: {len(margenes_validos)}")
        
        if margenes_validos:
            margen_promedio = sum(p['margen'] for p in margenes_validos) / len(margenes_validos)
            print(f"  - Margen promedio: {margen_promedio:.1f}%")
        
        # Estados
        estados = {}
        for p in productos:
            estado = p['estado']
            estados[estado] = estados.get(estado, 0) + 1
        
        print(f"\n🎯 Estados:")
        for estado, count in estados.items():
            print(f"  - {estado}: {count}")
        
        return productos
        
    except Exception as e:
        print(f"❌ Error al probar parser: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_moura_parser() 