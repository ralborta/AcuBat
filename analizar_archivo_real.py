#!/usr/bin/env python3
"""
Script para analizar la estructura del archivo Excel real
"""

import pandas as pd
import sys

def analizar_archivo_excel(ruta_archivo):
    """Analiza la estructura de un archivo Excel"""
    print(f"🔍 Analizando archivo: {ruta_archivo}")
    print("=" * 60)
    
    try:
        # Leer el archivo
        df = pd.read_excel(ruta_archivo)
        
        print(f"📊 Información general:")
        print(f"   - Filas: {len(df)}")
        print(f"   - Columnas: {len(df.columns)}")
        print()
        
        print(f"📋 Columnas encontradas:")
        for i, col in enumerate(df.columns):
            print(f"   {i+1:2d}. '{col}'")
        print()
        
        print(f"📝 Primeras 3 filas:")
        print(df.head(3).to_string())
        print()
        
        print(f"🔍 Análisis de tipos de datos:")
        print(df.dtypes)
        print()
        
        print(f"📊 Valores únicos por columna (primeras 5):")
        for col in df.columns:
            valores_unicos = df[col].dropna().unique()
            print(f"   '{col}': {len(valores_unicos)} valores únicos")
            if len(valores_unicos) > 0:
                print(f"      Ejemplos: {valores_unicos[:5]}")
        print()
        
        # Buscar columnas que podrían ser códigos, nombres, precios, etc.
        print(f"🎯 Detección automática de columnas:")
        
        codigos = []
        nombres = []
        precios = []
        marcas = []
        categorias = []
        
        for col in df.columns:
            col_lower = str(col).lower()
            
            # Detectar códigos/modelos
            if any(palabra in col_lower for palabra in ['modelo', 'codigo', 'code', 'ref', 'id']):
                codigos.append(col)
            
            # Detectar nombres/descripciones
            if any(palabra in col_lower for palabra in ['descripcion', 'nombre', 'name', 'producto']):
                nombres.append(col)
            
            # Detectar precios
            if any(palabra in col_lower for palabra in ['precio', 'price', 'pvp', 'costo', 'valor']):
                precios.append(col)
            
            # Detectar marcas
            if any(palabra in col_lower for palabra in ['marca', 'brand']):
                marcas.append(col)
            
            # Detectar categorías
            if any(palabra in col_lower for palabra in ['rubro', 'categoria', 'category', 'subrubro']):
                categorias.append(col)
        
        print(f"   📦 Códigos/Modelos: {codigos}")
        print(f"   📝 Nombres/Descripciones: {nombres}")
        print(f"   💰 Precios: {precios}")
        print(f"   🏷️  Marcas: {marcas}")
        print(f"   📂 Categorías: {categorias}")
        print()
        
        # Verificar si hay filas con headers
        print(f"🔍 Verificando si hay headers múltiples:")
        primera_fila = df.iloc[0]
        segunda_fila = df.iloc[1] if len(df) > 1 else None
        
        print(f"   Primera fila: {list(primera_fila)}")
        if segunda_fila is not None:
            print(f"   Segunda fila: {list(segunda_fila)}")
        
        # Verificar si la primera fila parece ser un header
        primera_fila_es_header = any(
            str(val).lower() in ['marca', 'rubro', 'modelo', 'descripcion', 'precio', 'pvp']
            for val in primera_fila if pd.notna(val)
        )
        
        if primera_fila_es_header:
            print(f"   ⚠️  La primera fila parece ser un header, no datos")
            print(f"   💡 Sugerencia: Saltar la primera fila al leer el archivo")
        
        return df
        
    except Exception as e:
        print(f"❌ Error analizando archivo: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python analizar_archivo_real.py <ruta_archivo_excel>")
        print("Ejemplo: python analizar_archivo_real.py lista_precios.xlsx")
        sys.exit(1)
    
    ruta_archivo = sys.argv[1]
    analizar_archivo_excel(ruta_archivo) 