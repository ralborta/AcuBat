#!/usr/bin/env python3
"""
Test para verificar cómo se están aplicando las reglas de rentabilidad
"""
import sys
import os

# Agregar el directorio api al path
sys.path.append('api')

try:
    from moura_rentabilidad import analizar_rentabilidades_moura
    
    def test_reglas():
        """Test de las reglas de rentabilidad"""
        
        print("🔍 Test de reglas de rentabilidad")
        print("=" * 50)
        
        # Analizar rentabilidades
        resultado = analizar_rentabilidades_moura('Rentalibilidades-2.xlsx')
        
        print(f"✅ Análisis completado")
        print(f"📊 Reglas minorista: {len(resultado['reglas_minorista'])}")
        print(f"📊 Reglas mayorista: {len(resultado['reglas_mayorista'])}")
        
        # Verificar markups únicos
        markups_minorista = set()
        markups_mayorista = set()
        
        for regla in resultado['reglas_minorista']:
            markups_minorista.add(regla['markup'])
            
        for regla in resultado['reglas_mayorista']:
            markups_mayorista.add(regla['markup'])
        
        print(f"\n📈 Markups únicos Minorista: {sorted(markups_minorista)}")
        print(f"📈 Markups únicos Mayorista: {sorted(markups_mayorista)}")
        
        # Mostrar algunos ejemplos
        print(f"\n📋 Ejemplos de reglas:")
        print("Minorista:")
        for i, regla in enumerate(resultado['reglas_minorista'][:5]):
            print(f"  {i+1}. {regla['codigo']}: {regla['markup']}%")
            
        print("Mayorista:")
        for i, regla in enumerate(resultado['reglas_mayorista'][:5]):
            print(f"  {i+1}. {regla['codigo']}: {regla['markup']}%")
        
        # Simular búsqueda de reglas como en main.py
        print(f"\n🔍 Simulando búsqueda de reglas:")
        
        # Códigos de ejemplo
        codigos_ejemplo = ['M40FD', 'M18FD', 'M22ED', 'M20GD', 'M22GD']
        
        for codigo in codigos_ejemplo:
            print(f"\n📦 Buscando reglas para {codigo}:")
            
            # Buscar regla exacta
            regla_minorista = None
            regla_mayorista = None
            
            for regla in resultado['reglas_minorista']:
                if regla['codigo'] == codigo:
                    regla_minorista = regla
                    break
                    
            for regla in resultado['reglas_mayorista']:
                if regla['codigo'] == codigo:
                    regla_mayorista = regla
                    break
            
            # Si no encuentra exacta, usar la primera (como en main.py)
            if not regla_minorista and resultado['reglas_minorista']:
                regla_minorista = resultado['reglas_minorista'][0]
                print(f"  ⚠️ Minorista: Usando default {regla_minorista['markup']}%")
            elif regla_minorista:
                print(f"  ✅ Minorista: Encontrada {regla_minorista['markup']}%")
                
            if not regla_mayorista and resultado['reglas_mayorista']:
                regla_mayorista = resultado['reglas_mayorista'][0]
                print(f"  ⚠️ Mayorista: Usando default {regla_mayorista['markup']}%")
            elif regla_mayorista:
                print(f"  ✅ Mayorista: Encontrada {regla_mayorista['markup']}%")
    
    if __name__ == "__main__":
        test_reglas()
        
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("Asegúrate de estar en el directorio correcto") 