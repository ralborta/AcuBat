#!/usr/bin/env python3
"""
Test directo del parser de Moura con el archivo real
"""

import sys
import os
sys.path.append('api')

from moura_rentabilidad import analizar_rentabilidades_moura
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_parser_moura():
    """Test directo del parser de Moura"""
    
    archivo = "Rentalibilidades-2.xlsx"
    
    logger.info(f"🔍 TEST DIRECTO - Analizando archivo: {archivo}")
    logger.info(f"📁 Archivo existe: {os.path.exists(archivo)}")
    logger.info(f"📏 Tamaño: {os.path.getsize(archivo)} bytes")
    
    try:
        # Ejecutar el parser
        resultado = analizar_rentabilidades_moura(archivo)
        
        logger.info(f"\n🎯 RESULTADO DEL PARSER:")
        logger.info(f"  Status: {resultado['resumen']}")
        logger.info(f"  Reglas Minorista: {len(resultado['reglas_minorista'])}")
        logger.info(f"  Reglas Mayorista: {len(resultado['reglas_mayorista'])}")
        
        if resultado['reglas_minorista']:
            logger.info(f"\n📊 PRIMERAS 3 REGLAS MINORISTA:")
            for i, regla in enumerate(resultado['reglas_minorista'][:3]):
                logger.info(f"  {i+1}. Código: {regla['codigo']} - Markup: {regla['markup']}% - Precio: ${regla['precio_base']}")
        
        if resultado['reglas_mayorista']:
            logger.info(f"\n📊 PRIMERAS 3 REGLAS MAYORISTA:")
            for i, regla in enumerate(resultado['reglas_mayorista'][:3]):
                logger.info(f"  {i+1}. Código: {regla['codigo']} - Markup: {regla['markup']}% - Precio: ${regla['precio_base']}")
        
        if not resultado['reglas_minorista'] and not resultado['reglas_mayorista']:
            logger.error(f"❌ NO SE ENCONTRARON REGLAS - Revisar estructura del archivo")
        
    except Exception as e:
        logger.error(f"❌ Error en el test: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_parser_moura() 