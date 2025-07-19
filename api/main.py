from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import logging
import io

# Importar módulos de la fase 2
from .logic import PricingLogic
from .openai_helper import OpenAIHelper
from .parser import ExcelParser

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Backend Acubat",
    description="Sistema de gestión de productos con procesamiento de Excel y alertas inteligentes",
    version="1.0.0"
)

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Variables globales para almacenar productos procesados
productos_actuales = []
pricing_logic = PricingLogic()
openai_helper = OpenAIHelper()
excel_parser = ExcelParser()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal con panel de productos"""
    try:
        # Generar resúmenes
        resumen_marcas = pricing_logic.obtener_resumen_marcas(productos_actuales) if productos_actuales else {}
        resumen_canales = pricing_logic.obtener_resumen_canales(productos_actuales) if productos_actuales else {}
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "productos": productos_actuales if productos_actuales else [],
            "total_productos": len(productos_actuales) if productos_actuales else 0,
            "productos_con_alertas": len([p for p in productos_actuales if p.alertas]) if productos_actuales else 0,
            "openai_disponible": openai_helper.esta_disponible(),
            "resumen_marcas": resumen_marcas,
            "resumen_canales": resumen_canales
        })
    except Exception as e:
        logger.error(f"Error en página principal: {e}")
        # Retornar una página simple en caso de error
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>Acubat - Error</title></head>
        <body>
            <h1>Backend Acubat</h1>
            <p>Error cargando la página: {str(e)}</p>
            <p>Productos cargados: {len(productos_actuales) if productos_actuales else 0}</p>
            <a href="/health">Health Check</a>
        </body>
        </html>
        """)

@app.get("/alertas", response_class=HTMLResponse)
async def alertas(request: Request):
    """Página de alertas"""
    try:
        productos_con_alertas = [p for p in productos_actuales if p.get('alertas')] if productos_actuales else []
        return templates.TemplateResponse("alertas.html", {
            "request": request,
            "productos": productos_con_alertas,
            "total_alertas": len(productos_con_alertas)
        })
    except Exception as e:
        logger.error(f"Error en página de alertas: {e}")
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>Acubat - Alertas</title></head>
        <body>
            <h1>Alertas</h1>
            <p>Error cargando alertas: {str(e)}</p>
            <a href="/">Volver al inicio</a>
        </body>
        </html>
        """)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Endpoint para subir archivo Excel y procesar con pricing"""
    try:
        # Verificar que sea un archivo soportado
        if not file.filename.endswith(('.xlsx', '.xls', '.csv', '.pdf')):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos Excel (.xlsx, .xls), CSV (.csv) o PDF (.pdf)")
        
        # Leer el archivo
        contenido = file.file.read()
        
        if not contenido:
            raise HTTPException(status_code=400, detail="El archivo está vacío")
        
        # Guardar archivo temporalmente
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(contenido)
            temp_file_path = temp_file.name
        
        try:
            # Verificar si es un PDF y convertirlo
            if file.filename.endswith('.pdf'):
                logger.info(f"Detectado archivo PDF: {file.filename}")
                
                # Importar convertidor PDF
                from pdf_converter import PDFConverter
                pdf_converter = PDFConverter()
                
                # Convertir PDF a Excel
                excel_path = pdf_converter.convert_pdf_to_excel(temp_file_path)
                
                if excel_path:
                    logger.info(f"PDF convertido exitosamente a: {excel_path}")
                    # Usar el archivo Excel convertido
                    productos = excel_parser.leer_excel(excel_path)
                    
                    # Limpiar archivo temporal Excel
                    if os.path.exists(excel_path):
                        os.unlink(excel_path)
                else:
                    raise HTTPException(status_code=400, detail="No se pudo convertir el PDF. Verifica que contenga tablas o texto estructurado.")
            else:
                # Procesar archivo Excel/CSV directamente
                productos = excel_parser.leer_excel(temp_file_path)
            
            if not productos:
                raise HTTPException(status_code=400, detail="No se pudieron procesar productos del archivo")
            
            # Aplicar pricing logic
            productos_procesados = pricing_logic.procesar_productos(productos)
            
            # Analizar con OpenAI si está disponible
            if openai_helper.esta_disponible():
                productos_analizados = openai_helper.analizar_lote_productos(productos_procesados)
                productos_procesados = productos_analizados
            
            # Actualizar productos globales
            global productos_actuales
            productos_actuales = productos_procesados
            
            # Generar resúmenes
            resumen_marcas = pricing_logic.obtener_resumen_marcas(productos_procesados)
            resumen_canales = pricing_logic.obtener_resumen_canales(productos_procesados)
            
            productos_con_alertas = len([p for p in productos_procesados if p.alertas])
            
            # Determinar tipo de archivo procesado
            archivo_tipo = "PDF convertido" if file.filename.endswith('.pdf') else "Excel/CSV"
            
            return {
                "mensaje": f"Archivo {archivo_tipo} procesado exitosamente con pricing",
                "productos_procesados": len(productos_procesados),
                "productos_con_alertas": productos_con_alertas,
                "resumen_marcas": resumen_marcas,
                "resumen_canales": resumen_canales,
                "openai_utilizado": openai_helper.esta_disponible(),
                "archivo_original": file.filename,
                "tipo_procesamiento": archivo_tipo
            }
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al procesar archivo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar archivo: {str(e)}")

@app.get("/api/status")
async def get_status():
    """Obtiene el estado del sistema"""
    return {
        "status": "ok",
        "mensaje": "Aplicación funcionando correctamente",
        "productos_cargados": len(productos_actuales)
    }

@app.get("/health")
async def health_check():
    """Health check para verificar que la aplicación funciona"""
    return {"status": "healthy", "message": "Backend Acubat funcionando"}

@app.get("/export/csv")
async def export_csv():
    """Exporta los productos actuales a CSV"""
    try:
        if not productos_actuales:
            raise HTTPException(status_code=404, detail="No hay productos para exportar")
        
        csv_content = pricing_logic.exportar_a_csv(productos_actuales)
        
        # Crear respuesta de streaming
        csv_io = io.StringIO(csv_content)
        
        return StreamingResponse(
            iter([csv_io.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=productos_pricing.csv"}
        )
        
    except Exception as e:
        logger.error(f"Error exportando CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Error exportando CSV: {str(e)}")

@app.get("/api/analisis-openai")
async def obtener_analisis_openai():
    """Obtiene análisis de OpenAI para los productos actuales"""
    try:
        if not productos_actuales:
            raise HTTPException(status_code=404, detail="No hay productos para analizar")
        
        if not openai_helper.esta_disponible():
            raise HTTPException(status_code=503, detail="OpenAI no está disponible")
        
        resumen = openai_helper.generar_resumen_analisis(productos_actuales)
        
        return {
            "resumen": resumen,
            "total_productos": len(productos_actuales),
            "productos_con_alertas": len([p for p in productos_actuales if p.alertas])
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo análisis OpenAI: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo análisis: {str(e)}")

@app.get("/api/filtrar")
async def filtrar_productos(
    canal: str = None,
    marca: str = None,
    con_alertas: bool = None
):
    """Filtra productos según criterios"""
    try:
        if not productos_actuales:
            return {"productos": [], "total": 0}
        
        productos_filtrados = productos_actuales.copy()
        
        # Filtrar por canal
        if canal:
            productos_filtrados = [p for p in productos_filtrados if p.canal.value == canal.lower()]
        
        # Filtrar por marca
        if marca:
            productos_filtrados = [p for p in productos_filtrados if p.marca.value == marca.lower()]
        
        # Filtrar por alertas
        if con_alertas is not None:
            if con_alertas:
                productos_filtrados = [p for p in productos_filtrados if p.alertas]
            else:
                productos_filtrados = [p for p in productos_filtrados if not p.alertas]
        
        return {
            "productos": productos_filtrados,
            "total": len(productos_filtrados),
            "filtros_aplicados": {
                "canal": canal,
                "marca": marca,
                "con_alertas": con_alertas
            }
        }
        
            except Exception as e:
            logger.error(f"Error filtrando productos: {e}")
            raise HTTPException(status_code=500, detail=f"Error filtrando productos: {str(e)}")

@app.post("/convertir-pdf")
async def convertir_pdf(file: UploadFile = File(...)):
    """Endpoint específico para convertir PDFs a Excel"""
    try:
        # Verificar que sea un archivo PDF
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF (.pdf)")
        
        # Leer el archivo
        contenido = file.file.read()
        
        if not contenido:
            raise HTTPException(status_code=400, detail="El archivo está vacío")
        
        # Guardar archivo temporalmente
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(contenido)
            temp_file_path = temp_file.name
        
        try:
            # Importar convertidor PDF
            from pdf_converter import PDFConverter
            pdf_converter = PDFConverter()
            
            # Convertir PDF a Excel
            excel_path = pdf_converter.convert_pdf_to_excel(temp_file_path)
            
            if excel_path:
                # Leer el archivo Excel convertido
                import pandas as pd
                df = pd.read_excel(excel_path)
                
                # Preparar respuesta
                response_data = {
                    "mensaje": "PDF convertido exitosamente",
                    "archivo_original": file.filename,
                    "archivo_convertido": os.path.basename(excel_path),
                    "filas_procesadas": len(df),
                    "columnas": list(df.columns),
                    "preview": df.head(5).to_dict('records')
                }
                
                # Limpiar archivo temporal Excel
                if os.path.exists(excel_path):
                    os.unlink(excel_path)
                
                return response_data
            else:
                raise HTTPException(status_code=400, detail="No se pudo convertir el PDF. Verifica que contenga tablas o texto estructurado.")
                
        finally:
            # Limpiar archivo temporal PDF
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al convertir PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al convertir PDF: {str(e)}") 