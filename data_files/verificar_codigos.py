#!/usr/bin/env python3
import pandas as pd
import sys
import os

# Agregar el directorio api al path
sys.path.append('api')

from moura_rentabilidad import analizar_rentabilidades_moura

def verificar_codigos():
    print("🔍 VERIFICACIÓN DE CÓDIGOS")
    print("=" * 50)
    
    # Analizar reglas de rentabilidad
    resultado_rentabilidades = analizar_rentabilidades_moura('Rentalibilidades-2.xlsx')
    
    # Leer archivo de precios
    try:
        df_precios = pd.read_excel('Lista Moura 04 (1).xlsx')
        print(f"📊 Archivo de precios cargado: {df_precios.shape}")
    except:
        print("❌ No se pudo cargar el archivo de precios")
        return
    
    # Obtener códigos de precios
    codigos_precios = []
    for i in range(len(df_precios)):
        try:
            codigo = str(df_precios.iloc[i, 0]).strip()
            if codigo and codigo != 'nan':
                codigos_precios.append(codigo)
        except:
            continue
    
    print(f"📋 Códigos en archivo de precios: {len(codigos_precios)}")
    print("Primeros 10 códigos de precios:")
    for i, codigo in enumerate(codigos_precios[:10]):
        print(f"  {i+1}. {codigo}")
    
    print()
    
    # Obtener códigos de reglas
    codigos_reglas_minorista = [regla['codigo'] for regla in resultado_rentabilidades['reglas_minorista']]
    codigos_reglas_mayorista = [regla['codigo'] for regla in resultado_rentabilidades['reglas_mayorista']]
    
    print(f"📋 Códigos en reglas Minorista: {len(codigos_reglas_minorista)}")
    print("Primeros 10 códigos de reglas Minorista:")
    for i, codigo in enumerate(codigos_reglas_minorista[:10]):
        print(f"  {i+1}. {codigo}")
    
    print()
    print(f"📋 Códigos en reglas Mayorista: {len(codigos_reglas_mayorista)}")
    print("Primeros 10 códigos de reglas Mayorista:")
    for i, codigo in enumerate(codigos_reglas_mayorista[:10]):
        print(f"  {i+1}. {codigo}")
    
    print()
    print("🔍 VERIFICANDO COINCIDENCIAS:")
    
    # Verificar coincidencias exactas
    coincidencias_exactas_minorista = []
    coincidencias_exactas_mayorista = []
    
    for codigo_precio in codigos_precios[:10]:  # Solo los primeros 10
        if codigo_precio in codigos_reglas_minorista:
            coincidencias_exactas_minorista.append(codigo_precio)
        if codigo_precio in codigos_reglas_mayorista:
            coincidencias_exactas_mayorista.append(codigo_precio)
    
    print(f"✅ Coincidencias exactas Minorista: {len(coincidencias_exactas_minorista)}")
    print(f"✅ Coincidencias exactas Mayorista: {len(coincidencias_exactas_mayorista)}")
    
    # Verificar coincidencias por similitud
    coincidencias_similitud_minorista = []
    coincidencias_similitud_mayorista = []
    
    for codigo_precio in codigos_precios[:10]:  # Solo los primeros 10
        for codigo_regla in codigos_reglas_minorista:
            if codigo_precio.startswith(codigo_regla[:3]) or codigo_regla.startswith(codigo_precio[:3]):
                coincidencias_similitud_minorista.append((codigo_precio, codigo_regla))
                break
        
        for codigo_regla in codigos_reglas_mayorista:
            if codigo_precio.startswith(codigo_regla[:3]) or codigo_regla.startswith(codigo_precio[:3]):
                coincidencias_similitud_mayorista.append((codigo_precio, codigo_regla))
                break
    
    print(f"⚠️ Coincidencias por similitud Minorista: {len(coincidencias_similitud_minorista)}")
    for precio, regla in coincidencias_similitud_minorista:
        print(f"  {precio} → {regla}")
    
    print(f"⚠️ Coincidencias por similitud Mayorista: {len(coincidencias_similitud_mayorista)}")
    for precio, regla in coincidencias_similitud_mayorista:
        print(f"  {precio} → {regla}")

if __name__ == "__main__":
    verificar_codigos() 