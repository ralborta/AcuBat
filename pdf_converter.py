#!/usr/bin/env python3
"""
Script para convertir PDFs a Excel/CSV para el sistema AcuBat
Soporta múltiples métodos de extracción según el tipo de PDF
"""

import os
import sys
import pandas as pd
import pdfplumber
import tabula
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFConverter:
    def __init__(self):
        self.supported_formats = ['.pdf']
        self.output_formats = ['.xlsx', '.csv']
    
    def detect_pdf_type(self, pdf_path):
        """Detecta el tipo de PDF para elegir el mejor método de extracción"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                first_page = pdf.pages[0]
                
                # Intentar extraer tablas
                tables = first_page.extract_tables()
                if tables and len(tables) > 0:
                    return "table"
                
                # Intentar extraer texto estructurado
                text = first_page.extract_text()
                if text and len(text.split('\n')) > 10:
                    return "text"
                
                return "image"
                
        except Exception as e:
            logger.error(f"Error detectando tipo de PDF: {e}")
            return "unknown"
    
    def extract_tables_with_pdfplumber(self, pdf_path):
        """Extrae tablas usando pdfplumber"""
        logger.info("Extrayendo tablas con pdfplumber...")
        
        all_tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    logger.info(f"Procesando página {page_num + 1}")
                    
                    tables = page.extract_tables()
                    for table_num, table in enumerate(tables):
                        if table and len(table) > 1:  # Al menos header + 1 fila
                            df = pd.DataFrame(table[1:], columns=table[0])
                            df['pagina'] = page_num + 1
                            df['tabla'] = table_num + 1
                            all_tables.append(df)
            
            if all_tables:
                # Combinar todas las tablas
                combined_df = pd.concat(all_tables, ignore_index=True)
                return combined_df
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error extrayendo tablas con pdfplumber: {e}")
            return None
    
    def extract_tables_with_tabula(self, pdf_path):
        """Extrae tablas usando tabula-py"""
        logger.info("Extrayendo tablas con tabula...")
        
        try:
            # Extraer todas las tablas del PDF
            tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
            
            if tables:
                # Combinar todas las tablas
                combined_df = pd.concat(tables, ignore_index=True)
                return combined_df
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error extrayendo tablas con tabula: {e}")
            return None
    
    def extract_text_structured(self, pdf_path):
        """Extrae texto y lo estructura como tabla"""
        logger.info("Extrayendo texto estructurado...")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                all_lines = []
                
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        lines = text.split('\n')
                        for line in lines:
                            if line.strip():
                                # Intentar separar por espacios múltiples o tabs
                                parts = [part.strip() for part in line.split() if part.strip()]
                                if len(parts) >= 3:  # Al menos 3 columnas
                                    all_lines.append(parts)
                
                if all_lines:
                    # Crear DataFrame
                    df = pd.DataFrame(all_lines)
                    return df
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error extrayendo texto: {e}")
            return None
    
    def normalize_dataframe(self, df):
        """Normaliza el DataFrame para el formato esperado por AcuBat"""
        logger.info("Normalizando DataFrame...")
        
        if df is None or df.empty:
            return None
        
        # Limpiar columnas vacías
        df = df.dropna(how='all')
        
        # Intentar identificar columnas por contenido
        column_mapping = {}
        
        for col in df.columns:
            col_str = str(col).lower()
            col_values = df[col].astype(str).str.lower()
            
            # Detectar tipo de columna por contenido
            if any('modelo' in val or 'codigo' in val or 'ref' in val for val in col_values.head(10)):
                column_mapping[col] = 'MODELO'
            elif any('descripcion' in val or 'nombre' in val or 'producto' in val for val in col_values.head(10)):
                column_mapping[col] = 'DESCRIPCION'
            elif any('marca' in val or 'brand' in val for val in col_values.head(10)):
                column_mapping[col] = 'MARCA'
            elif any('precio' in val or '$' in val or 'costo' in val for val in col_values.head(10)):
                if 'lista' in col_str or 'base' in col_str:
                    column_mapping[col] = 'PRECIO LISTA'
                else:
                    column_mapping[col] = 'PVP ON LINE'
            elif any('cantidad' in val or 'stock' in val or 'q.' in val for val in col_values.head(10)):
                column_mapping[col] = 'Q. PALLET'
        
        # Renombrar columnas identificadas
        df = df.rename(columns=column_mapping)
        
        # Agregar columnas faltantes con valores por defecto
        required_columns = ['MODELO', 'DESCRIPCION', 'MARCA', 'PRECIO LISTA', 'PVP ON LINE', 'Q. PALLET']
        
        for col in required_columns:
            if col not in df.columns:
                if col == 'MARCA':
                    df[col] = 'ACUBAT'  # Marca por defecto
                elif col in ['PRECIO LISTA', 'PVP ON LINE']:
                    df[col] = 0.0
                elif col == 'Q. PALLET':
                    df[col] = 1
                else:
                    df[col] = ''
        
        # Reordenar columnas
        df = df[required_columns]
        
        return df
    
    def convert_pdf_to_excel(self, pdf_path, output_path=None):
        """Convierte PDF a Excel usando el mejor método disponible"""
        
        if not os.path.exists(pdf_path):
            logger.error(f"Archivo PDF no encontrado: {pdf_path}")
            return None
        
        pdf_path = Path(pdf_path)
        
        if output_path is None:
            output_path = pdf_path.with_suffix('.xlsx')
        
        logger.info(f"Convirtiendo {pdf_path} a {output_path}")
        
        # Detectar tipo de PDF
        pdf_type = self.detect_pdf_type(pdf_path)
        logger.info(f"Tipo de PDF detectado: {pdf_type}")
        
        df = None
        
        # Intentar diferentes métodos según el tipo
        if pdf_type == "table":
            # Intentar pdfplumber primero
            df = self.extract_tables_with_pdfplumber(pdf_path)
            if df is None:
                # Intentar tabula como respaldo
                df = self.extract_tables_with_tabula(pdf_path)
        
        elif pdf_type == "text":
            df = self.extract_text_structured(pdf_path)
        
        else:
            # Intentar todos los métodos
            logger.info("Intentando todos los métodos de extracción...")
            
            df = self.extract_tables_with_pdfplumber(pdf_path)
            if df is None:
                df = self.extract_tables_with_tabula(pdf_path)
            if df is None:
                df = self.extract_text_structured(pdf_path)
        
        if df is not None:
            # Normalizar DataFrame
            df = self.normalize_dataframe(df)
            
            if df is not None:
                # Guardar como Excel
                df.to_excel(output_path, index=False)
                logger.info(f"✅ Archivo convertido exitosamente: {output_path}")
                logger.info(f"📊 Filas procesadas: {len(df)}")
                logger.info(f"📋 Columnas: {list(df.columns)}")
                return output_path
            else:
                logger.error("❌ Error normalizando datos")
                return None
        else:
            logger.error("❌ No se pudieron extraer datos del PDF")
            return None
    
    def convert_pdf_to_csv(self, pdf_path, output_path=None):
        """Convierte PDF a CSV"""
        excel_path = self.convert_pdf_to_excel(pdf_path)
        
        if excel_path:
            if output_path is None:
                output_path = Path(pdf_path).with_suffix('.csv')
            
            # Leer Excel y guardar como CSV
            df = pd.read_excel(excel_path)
            df.to_csv(output_path, index=False)
            
            # Limpiar archivo Excel temporal
            os.remove(excel_path)
            
            logger.info(f"✅ Archivo CSV creado: {output_path}")
            return output_path
        
        return None

def main():
    """Función principal"""
    converter = PDFConverter()
    
    if len(sys.argv) < 2:
        print("Uso: python pdf_converter.py <archivo.pdf> [formato_salida]")
        print("Formatos soportados: xlsx, csv")
        print("Ejemplo: python pdf_converter.py lista_precios.pdf xlsx")
        return
    
    pdf_path = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else 'xlsx'
    
    if not os.path.exists(pdf_path):
        print(f"❌ Archivo no encontrado: {pdf_path}")
        return
    
    print(f"🔄 Convirtiendo {pdf_path}...")
    
    if output_format.lower() == 'csv':
        result = converter.convert_pdf_to_csv(pdf_path)
    else:
        result = converter.convert_pdf_to_excel(pdf_path)
    
    if result:
        print(f"✅ Conversión exitosa: {result}")
        print("🚀 Ahora puedes subir este archivo al sistema AcuBat")
    else:
        print("❌ Error en la conversión")

if __name__ == "__main__":
    main() 