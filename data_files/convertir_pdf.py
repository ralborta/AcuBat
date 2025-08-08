#!/usr/bin/env python3
"""
Script simple para convertir PDFs a Excel/CSV
Uso: python convertir_pdf.py
"""

from pdf_converter import PDFConverter
import os

def main():
    print("🔄 Convertidor de PDF a Excel/CSV para AcuBat")
    print("=" * 50)
    
    # Solicitar archivo PDF
    pdf_path = input("📄 Ingresa la ruta del archivo PDF: ").strip()
    
    if not pdf_path:
        print("❌ No se ingresó ningún archivo")
        return
    
    # Verificar que el archivo existe
    if not os.path.exists(pdf_path):
        print(f"❌ Archivo no encontrado: {pdf_path}")
        return
    
    # Solicitar formato de salida
    print("\n📋 Formatos disponibles:")
    print("1. Excel (.xlsx)")
    print("2. CSV (.csv)")
    
    choice = input("Selecciona formato (1 o 2): ").strip()
    
    if choice == "2":
        output_format = "csv"
    else:
        output_format = "xlsx"
    
    # Crear convertidor
    converter = PDFConverter()
    
    print(f"\n🔄 Convirtiendo {pdf_path} a {output_format.upper()}...")
    
    # Convertir
    if output_format == "csv":
        result = converter.convert_pdf_to_csv(pdf_path)
    else:
        result = converter.convert_pdf_to_excel(pdf_path)
    
    if result:
        print(f"\n✅ ¡Conversión exitosa!")
        print(f"📁 Archivo creado: {result}")
        print(f"\n🚀 Ahora puedes:")
        print("1. Ir a tu sistema AcuBat en Vercel")
        print("2. Subir este archivo convertido")
        print("3. Ver el análisis automático de precios")
    else:
        print("\n❌ Error en la conversión")
        print("💡 Sugerencias:")
        print("- Verifica que el PDF tenga tablas o texto estructurado")
        print("- Intenta con otro archivo PDF")
        print("- Contacta soporte si el problema persiste")

if __name__ == "__main__":
    main() 