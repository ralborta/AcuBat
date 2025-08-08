#!/usr/bin/env python3
"""
Test del parser actualizado con el archivo completo
"""
import sys
import os

# Agregar el directorio api al path
sys.path.append('api')

try:
    from moura_rentabilidad import analizar_rentabilidades_moura
    
    def test_parser_actualizado():
        """Test del parser actualizado"""
        
        print("🔍 Test del parser actualizado con archivo completo")
        print("=" * 60)
        
        # Analizar rentabilidades
        resultado = analizar_rentabilidades_moura('Rentalibilidades-2.xlsx')
        
        print(f"✅ Análisis completado")
        print(f"📊 Reglas minorista: {len(resultado['reglas_minorista'])}")
        print(f"📊 Reglas mayorista: {len(resultado['reglas_mayorista'])}")
        
        # Verificar markups únicos
        markups_minorista = set()
        markups_mayorista = set()
        
        for regla in resultado['reglas_minorista']:
            markups_minorista.add(round(regla['markup'], 2))
            
        for regla in resultado['reglas_mayorista']:
            markups_mayorista.add(round(regla['markup'], 2))
        
        print(f"\n📈 Markups únicos Minorista: {len(markups_minorista)} valores")
        print(f"   Valores: {sorted(markups_minorista)}")
        
        print(f"\n📈 Markups únicos Mayorista: {len(markups_mayorista)} valores")
        print(f"   Valores: {sorted(markups_mayorista)}")
        
        # Mostrar algunos ejemplos
        print(f"\n📋 Ejemplos de reglas:")
        print("Minorista:")
        for i, regla in enumerate(resultado['reglas_minorista'][:5]):
            print(f"  {i+1}. {regla['codigo']}: {regla['markup']:.2f}%")
            
        print("Mayorista:")
        for i, regla in enumerate(resultado['reglas_mayorista'][:5]):
            print(f"  {i+1}. {regla['codigo']}: {regla['markup']:.2f}%")
        
        # Verificar si hay valores como los de la imagen
        valores_imagen = [19.34, 22.22, 21.70, 23.90, 39.06, 14.49, 15.78, 19.80, 18.71, 16.56, 28.22, 19.61, 29.01]
        coincidencias = [v for v in markups_mayorista if any(abs(v - vi) < 0.1 for vi in valores_imagen)]
        
        if coincidencias:
            print(f"\n✅ ¡COINCIDENCIAS CON LA IMAGEN!: {coincidencias}")
        else:
            print(f"\n❌ No se encontraron coincidencias exactas")
    
    if __name__ == "__main__":
        test_parser_actualizado()
        
except ImportError as e:
    print(f"❌ Error importando módulos: {e}") 