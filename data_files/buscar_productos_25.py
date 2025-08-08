#!/usr/bin/env python3
"""
Buscar productos que tengan markup 25% en mayorista
"""
import sys
import os

# Agregar el directorio api al path
sys.path.append('api')

try:
    from moura_rentabilidad import analizar_rentabilidades_moura
    
    def buscar_productos_25():
        """Buscar productos con markup 25%"""
        
        print("🔍 Buscando productos con markup 25% en mayorista")
        print("=" * 60)
        
        # Analizar rentabilidades
        resultado = analizar_rentabilidades_moura('Rentalibilidades-2.xlsx')
        
        # Buscar productos con markup 25%
        productos_25 = []
        productos_22 = []
        
        for regla in resultado['reglas_mayorista']:
            if regla['markup'] == 25.0:
                productos_25.append(regla['codigo'])
            elif regla['markup'] == 22.0:
                productos_22.append(regla['codigo'])
        
        print(f"📊 Productos con markup 25%: {len(productos_25)}")
        print(f"📊 Productos con markup 22%: {len(productos_22)}")
        
        print(f"\n📋 Productos con markup 25%:")
        for i, codigo in enumerate(productos_25[:10]):
            print(f"  {i+1}. {codigo}")
        if len(productos_25) > 10:
            print(f"  ... y {len(productos_25) - 10} más")
            
        print(f"\n📋 Productos con markup 22% (primeros 10):")
        for i, codigo in enumerate(productos_22[:10]):
            print(f"  {i+1}. {codigo}")
        if len(productos_22) > 10:
            print(f"  ... y {len(productos_22) - 10} más")
    
    if __name__ == "__main__":
        buscar_productos_25()
        
except ImportError as e:
    print(f"❌ Error importando módulos: {e}") 