#!/usr/bin/env python3
import pandas as pd
from api.moura_rentabilidad import analizar_rentabilidades_moura

def test_sistema_completo():
    print("🧪 PROBANDO SISTEMA COMPLETO")
    print("=" * 60)
    
    # 1. Verificar archivo de rentabilidades
    print("1️⃣ VERIFICANDO ARCHIVO DE RENTABILIDADES:")
    try:
        resultado_rentabilidades = analizar_rentabilidades_moura('Rentalibilidades-2.xlsx')
        print(f"   ✅ Reglas Minorista: {len(resultado_rentabilidades['reglas_minorista'])}")
        print(f"   ✅ Reglas Mayorista: {len(resultado_rentabilidades['reglas_mayorista'])}")
        print(f"   ✅ Total de reglas: {resultado_rentabilidades['resumen']['total_reglas']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 2. Verificar archivo de precios
    print("\n2️⃣ VERIFICANDO ARCHIVO DE PRECIOS:")
    try:
        xl = pd.ExcelFile('Lista Moura 04 (1).xlsx')
        hojas = xl.sheet_names
        print(f"   📊 Hojas disponibles: {hojas}")
        
        total_productos = 0
        for hoja in hojas:
            df = pd.read_excel('Lista Moura 04 (1).xlsx', sheet_name=hoja)
            if len(df) > 0:
                productos_hoja = 0
                for i in range(len(df)):
                    try:
                        codigo = None
                        precio = None
                        for col in range(min(5, len(df.columns))):
                            valor = df.iloc[i, col]
                            if pd.notna(valor) and str(valor).strip() and str(valor).strip() != 'nan':
                                if codigo is None:
                                    codigo = str(valor).strip()
                                elif precio is None and isinstance(valor, (int, float)) and valor > 0:
                                    precio = valor
                                    break
                        if codigo and precio:
                            productos_hoja += 1
                    except:
                        continue
                print(f"   📋 {hoja}: {productos_hoja} productos")
                total_productos += productos_hoja
        
        print(f"   🎯 TOTAL DE PRODUCTOS EN LISTADO: {total_productos}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 3. Simular procesamiento
    print("\n3️⃣ SIMULANDO PROCESAMIENTO:")
    print("   🔍 Buscando coincidencias entre productos y reglas...")
    
    # Obtener códigos de productos
    productos_codigos = []
    for hoja in hojas:
        df = pd.read_excel('Lista Moura 04 (1).xlsx', sheet_name=hoja)
        for i in range(len(df)):
            try:
                for col in range(min(5, len(df.columns))):
                    valor = df.iloc[i, col]
                    if pd.notna(valor) and str(valor).strip() and str(valor).strip() != 'nan':
                        productos_codigos.append(str(valor).strip())
                        break
            except:
                continue
    
    # Obtener códigos de reglas
    reglas_codigos = []
    for regla in resultado_rentabilidades['reglas_minorista']:
        reglas_codigos.append(regla['codigo'])
    
    # Buscar coincidencias
    coincidencias = []
    for codigo_producto in productos_codigos:
        if codigo_producto in reglas_codigos:
            coincidencias.append(codigo_producto)
    
    print(f"   📊 Productos en listado: {len(productos_codigos)}")
    print(f"   📊 Reglas disponibles: {len(reglas_codigos)}")
    print(f"   ✅ Coincidencias encontradas: {len(coincidencias)}")
    
    if len(coincidencias) > 0:
        print(f"   📋 Primeras 5 coincidencias: {coincidencias[:5]}")
    
    print("\n🎯 CONCLUSIÓN:")
    print(f"   - El sistema debería procesar {len(coincidencias)} productos")
    print(f"   - Si solo muestra 10, hay un límite en el frontend o backend")

if __name__ == "__main__":
    test_sistema_completo() 